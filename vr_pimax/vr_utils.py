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

from panda3d.core import loadPrcFileData
from ursina import *


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
        self._indices = None          # cached controller device indices
        self._trigger_prev = {'left': 0.0, 'right': 0.0}

        try:
            import openvr as _ovr
            self._ovr    = _ovr
            self._system = _ovr.VRSystem()   # reuses the already-running session
            self._ok     = True
            print("[VRController] Ready.")
        except ImportError:
            print("[VRController] openvr package not installed  →  pip install openvr")
        except Exception as e:
            print(f"[VRController] Init failed: {e}")

    # ------------------------------------------------------------------
    def _get_indices(self) -> list[int]:
        """Return cached list of controller device indices."""
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
        return self._indices

    def _get_state(self, hand: str):
        indices = self._get_indices()
        if not indices:
            return False, None
        idx = indices[-1] if hand == 'right' else indices[0]
        return self._system.getControllerState(idx)

    # ------------------------------------------------------------------
    def get_thumbstick(self, hand: str = 'right') -> tuple[float, float]:
        """
        Return (x, y) thumbstick values in range [-1, 1].
        x = strafe left/right,  y = forward (+) / back (-)
        """
        if not self._ok:
            return (0.0, 0.0)
        try:
            ok, state = self._get_state(hand)
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
            ok, state = self._get_state(hand)
            if ok:
                return state.rAxis[1].x
        except Exception:
            pass
        return 0.0

    def trigger_just_pressed(self, hand: str = 'right') -> bool:
        """
        Return True on the frame the trigger crosses the press threshold.
        Must be called exactly once per frame for correct edge detection.
        """
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
            collider="capsule",
            **kwargs,
        )
        self.speed   = speed
        self.gravity = 0      # disable gravity; VR locomotion is comfort-first
        self.enabled = False  # enabled/disabled by the experiment state machine
        self._ctrl   = VRControllerInput()

    def update(self):
        if not self.enabled:
            return

        # --- keyboard ---
        kb_x = held_keys["d"] - held_keys["a"]
        kb_z = held_keys["w"] - held_keys["s"]

        # --- controller thumbstick ---
        ct_x, ct_y = self._ctrl.get_thumbstick() if self._ctrl.available else (0.0, 0.0)

        # Combine and clamp to [-1, 1]
        dx = max(-1.0, min(1.0, kb_x + ct_x))
        dz = max(-1.0, min(1.0, kb_z + ct_y))   # stick y = forward

        if dx == 0 and dz == 0:
            return

        # Project the HMD heading onto the horizontal plane
        fwd   = Vec3(camera.forward.x, 0, camera.forward.z)
        right = Vec3(camera.right.x,   0, camera.right.z)

        if fwd.length_squared() > 0:
            fwd.normalize()
        if right.length_squared() > 0:
            right.normalize()

        move = (fwd * dz + right * dx).normalized()
        self.position += move * self.speed * time.dt


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
        try:
            # Verify that panda3d-openvr is active
            _ = base.openvr        # raises AttributeError if not loaded
            self._ok = True
            print("[EyeTracker] Active — using HMD forward as gaze proxy.")
            print("[EyeTracker] See GUIDE.md §Eye Tracking to enable true gaze.")
        except AttributeError:
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
