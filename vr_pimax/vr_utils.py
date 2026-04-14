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
  VRPlayer                  — movement-only FPS entity (no mouse look)
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
# VR-friendly player controller
# ---------------------------------------------------------------------------

class VRPlayer(Entity):
    """
    Minimal first-person movement controller for VR.

    Replaces Ursina's FirstPersonController so that:
      - WASD drives locomotion
      - Mouse is NOT used for looking (the HMD handles head orientation)

    The entity acts as the locomotion anchor.  Its ``position`` is used
    for proximity checks (star collection, trajectory logging, etc.).
    The actual view direction comes from the Pimax headset automatically.

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
        self.gravity = 0     # disable gravity; VR locomotion is comfort-first
        self.enabled = False  # enabled/disabled by the experiment state machine

    def update(self):
        if not self.enabled:
            return

        dx = held_keys["d"] - held_keys["a"]   # strafe right/left
        dz = held_keys["w"] - held_keys["s"]   # forward/back

        if dx == 0 and dz == 0:
            return

        # Project the HMD heading onto the horizontal plane so that
        # looking up/down does not push the player vertically.
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
