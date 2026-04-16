"""
vr_utils.py
===========
VR helper utilities for Pimax Crystal Super Q LED running on SteamVR.

Tested configuration
--------------------
  Hardware : Pimax Crystal Super Q LED (eye tracking, USB connection)
  Software : Pimax Play 1.43.9 → SteamVR → panda3d-openvr → Ursina

Public API
----------
  enable_vr(render_scale)   — call BEFORE Ursina() to activate VR rendering
  VRControllerInput         — polls SteamVR controller thumbstick + trigger
  VRPlayer                  — movement-only FPS entity (keyboard + controller)
  EyeTracker                — gaze direction sampler with graceful fallback
"""

import math

from panda3d.core import ConfigVariableString, KeyboardButton, loadPrcFileData
from ursina import *


def _ensure_openvr_initialized() -> bool:
    """
    Ensure ``base.openvr`` exists after Ursina/ShowBase has started.

    Some environments do not auto-load the ``p3openvr`` aux display module,
    so we fall back to explicit Python-side initialization.
    """
    try:
        _ = base.openvr
        return True
    except Exception:
        pass

    try:
        from p3dopenvr.p3dopenvr import P3DOpenVR

        # p3dopenvr sets textures-power-2 to "none" at import time.
        # Ursina enables textures-auto-power-2, which requires up/down.
        ConfigVariableString("textures-power-2").setValue("down")

        base.openvr = P3DOpenVR()
        base.openvr.init()
        print("[VR] Fallback init: P3DOpenVR initialized from Python module.")
        return True
    except Exception as e:
        print(f"[VR] Fallback init failed: {e}")
        return False


# ---------------------------------------------------------------------------
# VR rendering setup
# ---------------------------------------------------------------------------

def enable_vr(render_scale: float = 0.8) -> None:
    """
    Configure panda3d-openvr before Ursina starts.

    Must be called BEFORE ``app = Ursina()``.

    Parameters
    ----------
    render_scale : float
        Render resolution multiplier (1.0 = full native resolution).
        Crystal Super Q LED has very high resolution; 0.8 gives good
        frame rates without a visible quality drop for most experiments.
    """
    loadPrcFileData("", "aux-display p3openvr")
    loadPrcFileData("", f"openvr-render-size-multiplier {render_scale}")


# ---------------------------------------------------------------------------
# Controller input
# ---------------------------------------------------------------------------

class VRControllerInput:
    """
    Polls SteamVR controller state (thumbstick + trigger) via the
    ``openvr`` Python package.

    Install
    -------
    pip install openvr

    Works alongside panda3d-openvr — both packages talk to the same
    already-running SteamVR runtime, so there is no conflict.

    Axis mapping (standard SteamVR / Pimax controllers)
    ----------------------------------------------------
      rAxis[0].x / .y   thumbstick  (-1 … +1)
      rAxis[1].x         trigger     ( 0 … +1)

    Falls back silently if the package is missing or no controller is found,
    so keyboard-only use always works without changes.
    """

    TRIGGER_THRESHOLD = 0.5   # above = pressed, below = released

    def __init__(self):
        self._ok      = False
        self._system  = None
        self._ovr     = None
        self._owns_runtime = False
        self._last_reconnect_try = 0.0
        self._reconnect_interval = 2.0
        self._indices = None          # cached controller device indices
        self._trigger_prev = {'left': 0.0, 'right': 0.0}
        self._state_cache = {'left': (False, None), 'right': (False, None)}
        self._state_next_poll = {'left': 0.0, 'right': 0.0}
        self._state_poll_interval = 0.016  # ~60 Hz; getControllerState is a shared-memory read

        self._initialize_runtime(log_prefix=True)

    def _initialize_runtime(self, log_prefix: bool = False) -> bool:
        """Try to attach to SteamVR, preferring the active panda3d-openvr runtime."""
        try:
            if _ensure_openvr_initialized():
                import openvr as _ovr
                self._ovr = _ovr
                self._system = base.openvr.vr_system
                self._ok = True
                if log_prefix:
                    print("[VRController] Ready (reusing base.openvr.vr_system).")
                return True
        except Exception:
            pass

        try:
            import openvr as _ovr
            self._ovr = _ovr
            _ovr.init(_ovr.VRApplication_Scene)
            self._owns_runtime = True
            self._system = _ovr.VRSystem()
            self._ok = True
            if log_prefix:
                print("[VRController] Ready (direct openvr init).")
            return True
        except ImportError:
            if log_prefix:
                print("[VRController] openvr package not installed  →  pip install openvr")
        except Exception as e:
            if log_prefix:
                print(f"[VRController] Init failed: {e}")

        self._ok = False
        return False

    def _maybe_reconnect(self) -> None:
        if self._ok:
            return
        now = time.time()
        if (now - self._last_reconnect_try) < self._reconnect_interval:
            return
        self._last_reconnect_try = now
        if self._initialize_runtime(log_prefix=False):
            print("[VRController] Reconnected.")

    def poll_connection(self) -> bool:
        """Low-frequency reconnect entry point for external update loops."""
        self._maybe_reconnect()
        return self._ok

    def set_reconnect_interval(self, seconds: float) -> None:
        """Set minimum retry interval for reconnect attempts."""
        self._reconnect_interval = max(0.1, float(seconds))

    def set_state_poll_interval(self, seconds: float) -> None:
        """Set minimum interval for controller state refreshes."""
        self._state_poll_interval = max(0.05, float(seconds))

    def _poll_state(self, hand: str, force: bool = False):
        """Refresh and cache controller state at a bounded frequency."""
        if not self._ok:
            return False, None
        now = time.perf_counter()
        if force or now >= self._state_next_poll[hand]:
            self._state_cache[hand] = self._get_state(hand)
            self._state_next_poll[hand] = now + self._state_poll_interval
        return self._state_cache[hand]

    def __del__(self):
        if self._owns_runtime:
            try:
                self._ovr.shutdown()
            except Exception:
                pass

    # ------------------------------------------------------------------
    def _get_indices(self) -> list[int]:
        """Return cached list of controller device indices."""
        if self._ovr is None or self._system is None:
            return []

        if self._indices is None:
            found = []
            for i in range(self._ovr.k_unMaxTrackedDeviceCount):
                if (self._system.getTrackedDeviceClass(i) ==
                        self._ovr.TrackedDeviceClass_Controller):
                    found.append(i)
            if found:
                self._indices = found
                print(f"[VRController] Found {len(found)} controller(s): {found}")
            else:
                return []

        # Re-scan if previously cached controllers got disconnected.
        if self._indices and not any(
            self._system.isTrackedDeviceConnected(i) for i in self._indices
        ):
            self._indices = None
            return self._get_indices()

        return self._indices

    def _get_state(self, hand: str):
        indices = self._get_indices()
        if not indices:
            return False, None
        idx = indices[-1] if hand == 'right' else indices[0]

        # Prefer SteamVR-reported hand roles when available.
        try:
            right_role = self._ovr.TrackedControllerRole_RightHand
            left_role = self._ovr.TrackedControllerRole_LeftHand
            for i in indices:
                role = self._system.getControllerRoleForTrackedDeviceIndex(i)
                if hand == 'right' and role == right_role:
                    idx = i
                    break
                if hand == 'left' and role == left_role:
                    idx = i
                    break
        except Exception:
            pass

        return self._system.getControllerState(idx)

    # ------------------------------------------------------------------
    def get_thumbstick(self, hand: str = 'right') -> tuple[float, float]:
        """
        Return (x, y) thumbstick values in range [-1, 1].
        x = strafe left/right,  y = forward (+) / back (-)
        Reads rAxis[0] which is the thumbstick on Pimax Crystal via SteamVR.
        rAxis[1] is the trigger (0..1) and must never be used for locomotion.
        """
        if not self._ok:
            return (0.0, 0.0)
        try:
            ok, state = self._poll_state(hand)
            if ok:
                return (state.rAxis[0].x, state.rAxis[0].y)
        except Exception:
            pass
        return (0.0, 0.0)

    def get_trigger(self, hand: str = 'right') -> float:
        """Return trigger value in range [0, 1]."""
        if not self._ok:
            return 0.0
        try:
            ok, state = self._poll_state(hand)
            if ok:
                # Trigger is often rAxis[1].x, but controller mappings vary.
                vals = []
                for i in range(1, 5):
                    vals.append(state.rAxis[i].x)
                return max(vals) if vals else 0.0
        except Exception:
            pass
        return 0.0

    def trigger_just_pressed(self, hand: str = 'right') -> bool:
        """
        Return True on the frame the trigger crosses the press threshold.
        Must be called exactly once per frame for correct edge detection.
        Forces a fresh state read so quick presses are never missed.
        """
        self._poll_state(hand, force=True)   # bypass cache — trigger needs per-frame accuracy
        prev = self._trigger_prev[hand]
        curr = self.get_trigger(hand)
        self._trigger_prev[hand] = curr
        return prev < self.TRIGGER_THRESHOLD <= curr

    @property
    def available(self) -> bool:
        return self._ok


# ---------------------------------------------------------------------------
# VR-friendly player controller
# ---------------------------------------------------------------------------

class VRPlayer(Entity):
    """
    First-person movement controller for VR.

    Accepts input from both keyboard (WASD) and controller thumbstick
    simultaneously — whichever gives a non-zero signal is used.

    Mouse is NOT used for looking; the HMD handles head orientation.

    Parameters
    ----------
    speed : float
        Walk speed in world units per second (default 5).
    """

    def __init__(self, speed: float = 5.0, **kwargs):
        super().__init__(
            model=None,
            collider=None,   # no Panda3D physics collider; AABB handled manually
            **kwargs,
        )
        self.speed   = speed
        self.gravity = 0      # disable gravity; VR locomotion is comfort-first
        self.enabled = False  # enabled/disabled by the experiment state machine
        self._ctrl   = VRControllerInput()
        self._collision_rects: list[tuple[float, float, float, float]] = []
        self._collision_radius = 0.45
        self._enable_snap_turn = True
        self._snap_turn_angle = 30.0
        self._snap_turn_deadzone = 0.6
        self._snap_turn_latch = False
        self._last_safe_pos = Vec3(0, 0, 0)
        self._ctrl_available_cached = self._ctrl.available
        self._ctrl_poll_interval = 0.25   # availability check only — not state refresh rate
        self._ctrl_next_poll_t = 0.0
        self._stick_x_sign = 1.0
        self._stick_y_sign = 1.0
        # State poll interval (thumbstick/trigger) stays at VRControllerInput default (0.016 s)

    @staticmethod
    def _move_vr_rig(delta: Vec3) -> bool:
        """Move OpenVR tracking space when available (true VR locomotion)."""
        try:
            ts = base.openvr.tracking_space
            ts.setPos(ts.getPos() + delta)
            return True
        except Exception:
            return False

    @staticmethod
    def _get_hmd_offset() -> Vec3:
        """Return the current HMD offset inside tracking space if available."""
        try:
            hmd = base.openvr.hmd_anchor
            pos = hmd.getPos()
            return Vec3(pos.x, pos.y, pos.z)
        except Exception:
            return Vec3(0, 0, 0)

    def teleport_to(self, world_pos: Vec3) -> None:
        """Place the player and align tracking space so the HMD appears at world_pos."""
        self.position = Vec3(world_pos.x, world_pos.y, world_pos.z)
        self._last_safe_pos = Vec3(world_pos.x, world_pos.y, world_pos.z)
        try:
            tracking_space = base.openvr.tracking_space
            hmd_offset = self._get_hmd_offset()
            tracking_space.setPos(world_pos - hmd_offset)
        except Exception:
            pass

    def set_collision_rects(self, rects: list[tuple[float, float, float, float]], radius: float = 0.45) -> None:
        """Set wall rectangles (x, z, sx, sz) used to block movement."""
        self._collision_rects = list(rects)
        self._collision_radius = radius

    def set_controller_poll_interval(self, seconds: float) -> None:
        """Set controller *availability* polling interval used in update().
        Does not affect thumbstick/trigger state refresh rate."""
        self._ctrl_poll_interval = max(0.05, float(seconds))

    def set_locomotion_signs(self, x_sign: float = 1.0, y_sign: float = 1.0) -> None:
        """Set sign multipliers for controller locomotion axes."""
        self._stick_x_sign = 1.0 if x_sign >= 0 else -1.0
        self._stick_y_sign = 1.0 if y_sign >= 0 else -1.0

    def _collides_at(self, pos: Vec3) -> bool:
        px, pz = pos.x, pos.z
        r = self._collision_radius
        for wx, wz, sx, sz in self._collision_rects:
            if abs(px - wx) <= (sx * 0.5 + r) and abs(pz - wz) <= (sz * 0.5 + r):
                return True
        return False

    def _apply_movement(self, delta: Vec3) -> Vec3:
        """Apply planar movement with stepwise collision checks and wall sliding."""
        remaining = delta.length()
        if remaining <= 1e-8:
            return Vec3(0, 0, 0)

        direction = delta / remaining
        max_step = max(0.04, self._collision_radius * 0.25)
        steps = max(1, int(math.ceil(remaining / max_step)))
        step_delta = delta / steps
        applied = Vec3(0, 0, 0)

        for _ in range(steps):
            trial = self.position + step_delta
            if not self._collides_at(trial):
                self.position = trial
                applied += step_delta
                continue

            # If the full step is blocked, try each axis separately to slide along walls.
            trial_x = Vec3(self.position.x + step_delta.x, self.position.y, self.position.z)
            if not self._collides_at(trial_x):
                self.position = trial_x
                applied.x += step_delta.x
                continue

            trial_z = Vec3(self.position.x, self.position.y, self.position.z + step_delta.z)
            if not self._collides_at(trial_z):
                self.position = trial_z
                applied.z += step_delta.z
                continue

            # Completely blocked; stop instead of forcing a partial penetration.
            break

        return applied

    def _apply_snap_turn(self) -> None:
        """Use right-stick X for snap turning in VR (mouse-look replacement)."""
        if not self._enable_snap_turn:
            return
        if not self._controller_available():
            self._snap_turn_latch = False
            return

        rx, _ = self._ctrl.get_thumbstick('right')
        if abs(rx) < self._snap_turn_deadzone:
            self._snap_turn_latch = False
            return

        if self._snap_turn_latch:
            return

        self._snap_turn_latch = True
        turn = -self._snap_turn_angle if rx > 0 else self._snap_turn_angle
        try:
            ts = base.openvr.tracking_space
            ts.setH(ts.getH() + turn)
        except Exception:
            pass

    @staticmethod
    def _raw_key_axis(pos_key: str, neg_key: str) -> float:
        """Read raw Panda key state as a fallback when held_keys misses focus."""
        try:
            mw = base.mouseWatcherNode
            pos = 1.0 if mw and mw.isButtonDown(KeyboardButton.asciiKey(pos_key)) else 0.0
            neg = 1.0 if mw and mw.isButtonDown(KeyboardButton.asciiKey(neg_key)) else 0.0
            return pos - neg
        except Exception:
            return 0.0

    @staticmethod
    def _get_head_world_pos() -> Vec3:
        """Return HMD world position from the openvr anchor node (world space)."""
        try:
            hmd = base.openvr.hmd_anchor
            pos = hmd.getPos(render)
            return Vec3(pos.x, pos.y, pos.z)
        except Exception:
            try:
                p = camera.world_position
                return Vec3(p.x, p.y, p.z)
            except Exception:
                return Vec3(0, 0, 0)

    def _controller_available(self, force: bool = False) -> bool:
        """Poll controller availability at low frequency to avoid per-frame stalls."""
        now = time.perf_counter()
        if force or now >= self._ctrl_next_poll_t:
            self._ctrl_available_cached = self._ctrl.poll_connection()
            self._ctrl_next_poll_t = now + self._ctrl_poll_interval
        return self._ctrl_available_cached

    def update(self):
        if not self.enabled:
            return

        self._apply_snap_turn()

        # Keep collision anchor aligned with real HMD position.
        head_pos = self._get_head_world_pos()
        self.position = Vec3(head_pos.x, self.position.y, head_pos.z)

        # If room-scale drift puts the head inside a wall, snap back to last safe point.
        if self._collides_at(self.position):
            correction = Vec3(
                self._last_safe_pos.x - self.position.x,
                0,
                self._last_safe_pos.z - self.position.z,
            )
            if correction.length_squared() > 1e-8:
                self._move_vr_rig(correction)
            self.position = Vec3(self._last_safe_pos.x, self.position.y, self._last_safe_pos.z)
            return
        else:
            self._last_safe_pos = Vec3(self.position.x, self.position.y, self.position.z)

        # --- keyboard ---
        kb_x = (held_keys["d"] - held_keys["a"]) + self._raw_key_axis("d", "a")
        kb_z = (held_keys["w"] - held_keys["s"]) + self._raw_key_axis("w", "s")

        # --- controller thumbstick (left = locomotion, right = snap turn only) ---
        if self._controller_available():
            ct_x, ct_y = self._ctrl.get_thumbstick('left')
            ct_x *= self._stick_x_sign
            ct_y *= self._stick_y_sign
        else:
            ct_x, ct_y = (0.0, 0.0)

        # Combine and clamp to [-1, 1]
        dx = max(-1.0, min(1.0, kb_x + ct_x))
        dz = max(-1.0, min(1.0, kb_z + ct_y))   # stick y = forward

        if dx == 0 and dz == 0:
            return

        # Project the HMD heading onto the horizontal plane.
        # camera.forward is NOT updated by p3dopenvr — the Ursina camera
        # entity is decoupled from HMD tracking. Read orientation directly
        # from the HMD anchor node instead.
        fwd = right = None
        try:
            q = base.openvr.hmd_anchor.getQuat(render)
            # Ursina world space is Y-up; forward = +Z, right = +X.
            f = q.xform(Vec3(0, 0, 1))
            r = q.xform(Vec3(1, 0, 0))
            fwd   = Vec3(f.x, 0, f.z)
            right = Vec3(r.x, 0, r.z)
        except Exception:
            pass

        if fwd is None or fwd.length_squared() < 1e-6:
            fwd   = Vec3(camera.forward.x, 0, camera.forward.z)
            right = Vec3(camera.right.x,   0, camera.right.z)

        if fwd.length_squared() < 1e-6:
            fwd   = Vec3(self.forward.x, 0, self.forward.z)
            right = Vec3(self.right.x,   0, self.right.z)

        if fwd.length_squared() > 0:
            fwd.normalize()
        if right.length_squared() > 0:
            right.normalize()

        move = (fwd * dz + right * dx)
        if move.length_squared() <= 1e-8:
            return
        delta = move.normalized() * self.speed * time.dt

        applied = self._apply_movement(delta)

        if applied.length_squared() > 0:
            self._last_safe_pos = Vec3(self.position.x, self.position.y, self.position.z)
            self._move_vr_rig(applied)


# ---------------------------------------------------------------------------
# Eye gaze tracker
# ---------------------------------------------------------------------------

class EyeTracker:
    """
    Samples gaze direction from the Pimax Crystal's built-in eye tracker.

    Current implementation
    ----------------------
    Uses the HMD forward vector as a gaze proxy.  This gives you
    head-direction data immediately with zero extra dependencies and
    is a valid baseline for head-referenced analyses.

    Upgrade to true per-eye gaze
    ----------------------------
    Option A — Pimax PGEE SDK (recommended for Pimax Crystal)
        Install the Pimax Eye Tracking SDK, then replace ``sample()``::

            from PimaxEyeTracker import PimaxEyeTracker
            self._et = PimaxEyeTracker()
            self._et.open()
            # in sample():
            data = self._et.get_gaze_data()
            return (data.gaze_x, data.gaze_y, data.gaze_z)

    Option B — pyopenxr XR_EXT_eye_gaze_interaction
        Works if SteamVR exposes the extension for your device.
        See GUIDE.md §Eye Tracking for a full implementation example.

    The ``sample()`` signature is identical for both options, so
    swapping implementations requires no changes to the experiment scripts.
    """

    def __init__(self):
        self._ok = False
        if _ensure_openvr_initialized():
            self._ok = True
            print("[EyeTracker] Active — using HMD forward as gaze proxy.")
            print("[EyeTracker] See GUIDE.md §Eye Tracking to enable true gaze.")
        else:
            print("[EyeTracker] WARNING: base.openvr not found.")
            print("[EyeTracker]   Did you call enable_vr() before Ursina()?")

    def sample(self) -> tuple[float, float, float]:
        """
        Return the current gaze direction (gx, gy, gz) in world space.

        The returned vector points in the direction the participant is
        looking.  Currently this is the HMD forward vector (head direction).

        Returns ``(0.0, 0.0, 0.0)`` if the tracker is unavailable.
        """
        if not self._ok:
            return (0.0, 0.0, 0.0)
        try:
            f = camera.forward
            return (round(f.x, 4), round(f.y, 4), round(f.z, 4))
        except Exception:
            return (0.0, 0.0, 0.0)

    @property
    def available(self) -> bool:
        """True if the tracker initialized successfully."""
        return self._ok
