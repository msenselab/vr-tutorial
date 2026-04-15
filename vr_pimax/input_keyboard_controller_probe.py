"""
input_keyboard_controller_probe.py
==================================
Standalone locomotion probe for VR input debugging.

Goal
----
Verify that keyboard (WASD) and VR controller stick input can drive
first-person movement in the same scene.

How to use
----------
1) Start Pimax Play, then SteamVR.
2) Run this script from the repo root:
   c:/Users/PC/Documents/GitHub/vr-tutorial/.venv/Scripts/python.exe vr_pimax/input_keyboard_controller_probe.py
3) Put on the headset and test movement:
   - Keyboard: W A S D
   - Controller: left or right stick
   - Mixed input: hold W and push stick sideways

Hotkeys
-------
R      reset player position
L      toggle console logging
[/]    decrease/increase speed by 1
0      reset speed to default
Shift+Q quit
"""

from panda3d.core import KeyboardButton
from direct.showbase import ShowBaseGlobal
from ursina import AmbientLight, DirectionalLight, Entity, Sky, Text, Ursina, Vec3, application, camera, color, held_keys, time

from vr_utils import VRControllerInput, enable_vr


class LocomotionProbePlayer(Entity):
    """Simple first-person locomotion probe driven by keyboard + controller."""

    DEFAULT_SPEED = 9.0

    def __init__(self, speed: float = DEFAULT_SPEED, **kwargs):
        super().__init__(model=None, collider="capsule", **kwargs)
        self.speed = speed
        self.enabled = True
        self.ctrl = VRControllerInput()
        self.log_enabled = False
        self.last_report = 0.0
        self._last_reconnect_try = 0.0

        self.last_kb = (0.0, 0.0)
        self.last_left = (0.0, 0.0)
        self.last_right = (0.0, 0.0)
        self.last_ctrl = (0.0, 0.0)
        self.last_combined = (0.0, 0.0)
        self.last_move_len = 0.0

        self.position = Vec3(0.0, 1.0, 0.0)

    @staticmethod
    def _move_vr_rig(delta: Vec3) -> bool:
        """Move OpenVR tracking space so headset view translates in VR."""
        try:
            sb = ShowBaseGlobal.base
            ts = sb.openvr.tracking_space
            ts.setPos(ts.getPos() + delta)
            return True
        except Exception:
            return False

    @staticmethod
    def _move_fallback_view(delta: Vec3) -> None:
        """Fallback translation when OpenVR tracking space is not available."""
        try:
            camera.position += delta
        except Exception:
            pass

    @staticmethod
    def _raw_key_axis(pos_key: str, neg_key: str) -> float:
        try:
            sb = ShowBaseGlobal.base
            mw = sb.mouseWatcherNode if sb else None
            pos = 1.0 if mw and mw.isButtonDown(KeyboardButton.asciiKey(pos_key)) else 0.0
            neg = 1.0 if mw and mw.isButtonDown(KeyboardButton.asciiKey(neg_key)) else 0.0
            return pos - neg
        except Exception:
            return 0.0

    @staticmethod
    def _clamp(v: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, v))

    def _read_keyboard(self) -> tuple[float, float]:
        kb_x = (held_keys["d"] - held_keys["a"]) + self._raw_key_axis("d", "a")
        kb_z = (held_keys["w"] - held_keys["s"]) + self._raw_key_axis("w", "s")
        return (self._clamp(kb_x, -1.0, 1.0), self._clamp(kb_z, -1.0, 1.0))

    def _read_controller(self) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
        if not self.ctrl.available:
            now = time.time()
            if (now - self._last_reconnect_try) >= 2.0:
                self._last_reconnect_try = now
                self.ctrl = VRControllerInput()
            zero = (0.0, 0.0)
            return zero, zero, zero

        left = self.ctrl.get_thumbstick("left")
        right = self.ctrl.get_thumbstick("right")

        l_mag = left[0] * left[0] + left[1] * left[1]
        r_mag = right[0] * right[0] + right[1] * right[1]
        chosen = left if l_mag >= r_mag else right
        return left, right, chosen

    def _movement_basis(self) -> tuple[Vec3, Vec3]:
        fwd = Vec3(camera.forward.x, 0, camera.forward.z)
        right = Vec3(camera.right.x, 0, camera.right.z)

        # Fallback when camera basis degenerates in some VR frames.
        if fwd.length_squared() < 1e-6 or right.length_squared() < 1e-6:
            fwd = Vec3(self.forward.x, 0, self.forward.z)
            right = Vec3(self.right.x, 0, self.right.z)

        if fwd.length_squared() > 0:
            fwd.normalize()
        if right.length_squared() > 0:
            right.normalize()
        return fwd, right

    def update(self):
        if not self.enabled:
            return

        kb = self._read_keyboard()
        left, right, ctrl = self._read_controller()

        dx = self._clamp(kb[0] + ctrl[0], -1.0, 1.0)
        dz = self._clamp(kb[1] + ctrl[1], -1.0, 1.0)

        fwd, right_v = self._movement_basis()
        move = (fwd * dz + right_v * dx)

        self.last_kb = kb
        self.last_left = left
        self.last_right = right
        self.last_ctrl = ctrl
        self.last_combined = (dx, dz)
        self.last_move_len = move.length()

        if move.length_squared() > 1e-8:
            delta = move.normalized() * self.speed * time.dt
            if self._move_vr_rig(delta):
                self.position += delta
            else:
                self._move_fallback_view(delta)
                self.position += delta

        if self.log_enabled and (time.time() - self.last_report) >= 0.25:
            self.last_report = time.time()
            print(
                "[Probe] "
                f"kb=({kb[0]:+.2f},{kb[1]:+.2f}) "
                f"L=({left[0]:+.2f},{left[1]:+.2f}) "
                f"R=({right[0]:+.2f},{right[1]:+.2f}) "
                f"use=({ctrl[0]:+.2f},{ctrl[1]:+.2f}) "
                f"mix=({dx:+.2f},{dz:+.2f}) "
                f"pos=({self.position.x:+.2f},{self.position.z:+.2f})"
            )

    def adjust_speed(self, delta: float):
        self.speed = self._clamp(self.speed + delta, 1.0, 30.0)
        print(f"[Probe] Speed set to {self.speed:.1f}")

    def reset_speed(self):
        self.speed = self.DEFAULT_SPEED
        print(f"[Probe] Speed reset to {self.speed:.1f}")


def setup_scene():
    Sky()
    sun = DirectionalLight(shadows=False)
    sun.look_at(Vec3(1, -1, -1))
    AmbientLight(color=color.rgba(0.35, 0.35, 0.35, 1.0))

    Entity(
        model="plane",
        scale=(80, 1, 80),
        position=(0, 0, 0),
        texture="white_cube",
        texture_scale=(40, 40),
        color=color.rgba(170, 170, 170, 255),
        collider="box",
    )

    # Visual movement markers.
    for x in range(-20, 21, 10):
        for z in range(-20, 21, 10):
            Entity(
                model="cube",
                position=(x, 0.25, z),
                scale=(0.5, 0.5, 0.5),
                color=color.azure,
            )


enable_vr(render_scale=0.8)
app = Ursina()
setup_scene()

player = LocomotionProbePlayer(speed=LocomotionProbePlayer.DEFAULT_SPEED)

hud_title = Text(
    text="Locomotion Probe (Keyboard + Controller)",
    position=(-0.82, 0.46),
    scale=1.8,
    parent=camera.ui,
)

hud_help = Text(
    text="WASD + Left/Right stick | [/] speed | R reset | L log | Shift+Q quit",
    position=(-0.82, 0.41),
    scale=1.2,
    parent=camera.ui,
)

hud_data = Text(
    text="",
    position=(-0.82, 0.33),
    scale=1.2,
    parent=camera.ui,
)


def update():
    hud_data.text = (
        f"kb: ({player.last_kb[0]:+.2f}, {player.last_kb[1]:+.2f})\n"
        f"left: ({player.last_left[0]:+.2f}, {player.last_left[1]:+.2f})\n"
        f"right: ({player.last_right[0]:+.2f}, {player.last_right[1]:+.2f})\n"
        f"chosen: ({player.last_ctrl[0]:+.2f}, {player.last_ctrl[1]:+.2f})\n"
        f"mix: ({player.last_combined[0]:+.2f}, {player.last_combined[1]:+.2f})\n"
        f"speed: {player.speed:.1f}\n"
        f"controller: {'OK' if player.ctrl.available else 'NOT READY'}\n"
        f"move_len: {player.last_move_len:.3f}\n"
        f"pos: ({player.position.x:+.2f}, {player.position.z:+.2f})"
    )


def input(key):
    if key == "r":
        player.position = Vec3(0.0, 1.0, 0.0)
        print("[Probe] Position reset.")
    elif key == "l":
        player.log_enabled = not player.log_enabled
        print(f"[Probe] Logging {'ON' if player.log_enabled else 'OFF'}.")
    elif key == "left bracket":
        player.adjust_speed(-1.0)
    elif key == "right bracket":
        player.adjust_speed(1.0)
    elif key == "0":
        player.reset_speed()
    elif key == "q" and held_keys["shift"]:
        application.quit()


app.run()
