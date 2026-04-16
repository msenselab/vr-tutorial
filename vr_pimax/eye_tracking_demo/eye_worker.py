"""
eye_worker.py — OpenXR eye gaze subprocess
===========================================
Launched as a child process by EyeTracker (vr_utils.py).
Reads eye gaze via XR_EXT_eye_gaze_interaction and writes
to a named shared memory block every frame (~90 Hz).

Install dependency:
    pip install pyopenxr

Shared memory layout (GAZE_FMT, little-endian):
    gx  gy  gz          float32 × 3   gaze direction unit vector (Ursina space)
    pupil_l  pupil_r    float32 × 2   pupil diameter in mm  (0 if unavailable)
    confidence          float32 × 1   0.0–1.0
    status              int32  × 1    0=idle 1=ok 2=error
Total: 28 bytes
"""

import ctypes
import math
import mmap
import struct
import sys
import time

SHM_NAME  = "pimax_gaze_v1"
GAZE_FMT  = "<ffffffi"                 # gx gy gz pl pr conf status
GAZE_SIZE = struct.calcsize(GAZE_FMT)  # 28 bytes

STATUS_IDLE  = 0
STATUS_OK    = 1
STATUS_ERROR = 2


def _write(shm, gx=0., gy=0., gz=1., pl=0., pr=0., conf=0., status=STATUS_IDLE):
    shm.seek(0)
    shm.write(struct.pack(GAZE_FMT, gx, gy, gz, pl, pr, conf, status))
    shm.flush()


# ---------------------------------------------------------------------------
# Minimal Win32 OpenGL context — zero extra pip packages
# ---------------------------------------------------------------------------

def _create_wgl_context():
    """Create a hidden 1×1 OpenGL window so OpenXR has a graphics binding."""
    from ctypes import wintypes

    user32   = ctypes.WinDLL("user32",   use_last_error=True)
    gdi32    = ctypes.WinDLL("gdi32",    use_last_error=True)
    opengl32 = ctypes.WinDLL("opengl32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    WNDPROC = ctypes.WINFUNCTYPE(
        ctypes.c_long, wintypes.HWND, wintypes.UINT,
        wintypes.WPARAM, wintypes.LPARAM,
    )
    _def = user32.DefWindowProcW
    _def.restype  = ctypes.c_long
    _wnd_proc = WNDPROC(lambda h, m, w, l: _def(h, m, w, l))

    class WNDCLASSW(ctypes.Structure):
        _fields_ = [
            ("style",         wintypes.UINT),
            ("lpfnWndProc",   WNDPROC),
            ("cbClsExtra",    ctypes.c_int),
            ("cbWndExtra",    ctypes.c_int),
            ("hInstance",     wintypes.HINSTANCE),
            ("hIcon",         wintypes.HANDLE),
            ("hCursor",       wintypes.HANDLE),
            ("hbrBackground", wintypes.HANDLE),
            ("lpszMenuName",  wintypes.LPCWSTR),
            ("lpszClassName", wintypes.LPCWSTR),
        ]

    wc = WNDCLASSW()
    wc.lpfnWndProc   = _wnd_proc
    wc.hInstance     = kernel32.GetModuleHandleW(None)
    wc.lpszClassName = "GazeGL"
    user32.RegisterClassW(ctypes.byref(wc))

    hwnd = user32.CreateWindowExW(
        0, "GazeGL", "GazeGL", 0,
        0, 0, 1, 1, None, None, wc.hInstance, None,
    )
    hdc = user32.GetDC(hwnd)

    class PFD(ctypes.Structure):
        _fields_ = [
            ("nSize",           wintypes.WORD),
            ("nVersion",        wintypes.WORD),
            ("dwFlags",         wintypes.DWORD),
            ("iPixelType",      ctypes.c_ubyte),
            ("cColorBits",      ctypes.c_ubyte),
            ("cRedBits",        ctypes.c_ubyte), ("cRedShift",        ctypes.c_ubyte),
            ("cGreenBits",      ctypes.c_ubyte), ("cGreenShift",      ctypes.c_ubyte),
            ("cBlueBits",       ctypes.c_ubyte), ("cBlueShift",       ctypes.c_ubyte),
            ("cAlphaBits",      ctypes.c_ubyte), ("cAlphaShift",      ctypes.c_ubyte),
            ("cAccumBits",      ctypes.c_ubyte),
            ("cAccumRedBits",   ctypes.c_ubyte), ("cAccumGreenBits",  ctypes.c_ubyte),
            ("cAccumBlueBits",  ctypes.c_ubyte), ("cAccumAlphaBits",  ctypes.c_ubyte),
            ("cDepthBits",      ctypes.c_ubyte), ("cStencilBits",     ctypes.c_ubyte),
            ("cAuxBuffers",     ctypes.c_ubyte), ("iLayerType",       ctypes.c_ubyte),
            ("bReserved",       ctypes.c_ubyte),
            ("dwLayerMask",     wintypes.DWORD),
            ("dwVisibleMask",   wintypes.DWORD),
            ("dwDamageMask",    wintypes.DWORD),
        ]

    pfd = PFD()
    pfd.nSize      = ctypes.sizeof(PFD)
    pfd.nVersion   = 1
    pfd.dwFlags    = 0x00000004 | 0x00000020 | 0x00000001  # DRAW_TO_WINDOW | SUPPORT_OGL | DOUBLEBUFFER
    pfd.cColorBits = 32
    pfd.cDepthBits = 24

    fmt = gdi32.ChoosePixelFormat(hdc, ctypes.byref(pfd))
    gdi32.SetPixelFormat(hdc, fmt, ctypes.byref(pfd))
    hglrc = opengl32.wglCreateContext(hdc)
    opengl32.wglMakeCurrent(hdc, hglrc)

    return int(hdc), int(hglrc)


# ---------------------------------------------------------------------------
# Quaternion → forward vector conversion
# OpenXR: right-handed, Y-up, -Z forward
# Ursina:  right-handed, Y-up, +Z forward  →  negate Z
# ---------------------------------------------------------------------------

def _quat_to_ursina_fwd(qx, qy, qz, qw):
    """Return the -Z basis vector of the quaternion, converted to Ursina +Z forward."""
    # Rotate (0, 0, -1) by quaternion
    fx = -2.0 * (qx * qz + qw * qy)
    fy = -2.0 * (qy * qz - qw * qx)
    fz = -(qw*qw - qx*qx - qy*qy + qz*qz)
    # OpenXR X = Ursina X,  OpenXR Y = Ursina Y,  OpenXR Z = −Ursina Z
    mag = math.sqrt(fx*fx + fy*fy + fz*fz) or 1.0
    return fx/mag, fy/mag, -fz/mag   # negate z for Ursina


# ---------------------------------------------------------------------------
# Main OpenXR loop
# ---------------------------------------------------------------------------

def _run(shm):
    try:
        import xr
    except ImportError:
        print("[EyeWorker] pyopenxr not installed -> pip install pyopenxr", flush=True)
        _write(shm, status=STATUS_ERROR)
        return

    # --- check available extensions ---
    # pyopenxr may return bytes for extension names on Windows.
    avail = set()
    for p in xr.enumerate_instance_extension_properties(None):
        name = p.extension_name
        if isinstance(name, bytes):
            name = name.decode("utf-8", errors="ignore")
        avail.add(name)

    print(f"[EyeWorker] Available extensions ({len(avail)}):", flush=True)
    for e in sorted(avail):
        print(f"  {e}", flush=True)

    EYE_EXT = "XR_EXT_eye_gaze_interaction"
    if EYE_EXT not in avail:
        print("[EyeWorker] XR_EXT_eye_gaze_interaction not available in this runtime.",
              flush=True)
        print("[EyeWorker] Possible causes:", flush=True)
        print("  1. SteamVR is not set as the default OpenXR runtime", flush=True)
        print("     Fix: SteamVR menu → Settings → OpenXR → Set SteamVR as OpenXR runtime", flush=True)
        print("  2. Eye tracking not enabled in Pimax Play", flush=True)
        print("     Fix: Pimax Play → Settings → Eye Tracking → Enable", flush=True)
        _write(shm, status=STATUS_ERROR)
        return

    exts      = [EYE_EXT]
    headless  = "XR_MND_headless" in avail
    use_gl    = False

    if headless:
        exts.append("XR_MND_headless")
        print("[EyeWorker] Using headless session (XR_MND_headless).", flush=True)
    elif "XR_KHR_opengl_enable" in avail:
        exts.append("XR_KHR_opengl_enable")
        use_gl = True
        print("[EyeWorker] Using OpenGL session binding.", flush=True)
    else:
        print("[EyeWorker] No suitable session backend found.", flush=True)
        _write(shm, status=STATUS_ERROR)
        return

    # --- instance ---
    instance = xr.create_instance(xr.InstanceCreateInfo(
        application_info=xr.ApplicationInfo(
            application_name="GazeWorker",
            application_version=1,
            engine_name="GazeWorker",
            engine_version=1,
            api_version=xr.Version(1, 0, 0),
        ),
        enabled_extension_names=exts,
    ))

    system_id = xr.get_system(instance, xr.SystemGetInfo(
        form_factor=xr.FormFactor.HEAD_MOUNTED_DISPLAY,
    ))

    # verify eye gaze support on this system
    if hasattr(xr, "SystemEyeGazeInteractionPropertiesEXT"):
        eye_props = xr.SystemEyeGazeInteractionPropertiesEXT()
    elif hasattr(xr, "EyeGazeInteractionSystemPropertiesEXT"):
        eye_props = xr.EyeGazeInteractionSystemPropertiesEXT()
    else:
        print("[EyeWorker] Runtime lacks eye-gaze system properties struct.", flush=True)
        _write(shm, status=STATUS_ERROR)
        return

    eye_supported = True
    sys_props = xr.SystemProperties(next=ctypes.pointer(eye_props))
    try:
        xr.get_system_properties(instance, system_id, ctypes.byref(sys_props))
        eye_supported = bool(getattr(eye_props, "supports_eye_gaze_interaction", False))
    except TypeError:
        # Some pyopenxr builds expose only the 2-arg form.
        xr.get_system_properties(instance, system_id)
        print("[EyeWorker] get_system_properties ext chain unavailable; proceeding.", flush=True)

    if not eye_supported:
        print("[EyeWorker] Headset reports no eye gaze interaction support.", flush=True)
        _write(shm, status=STATUS_ERROR)
        return

    # --- session ---
    if headless:
        session = xr.create_session(instance, xr.SessionCreateInfo(system_id=system_id))
    else:
        hdc, hglrc = _create_wgl_context()
        binding = xr.GraphicsBindingOpenGLWin32KHR(h_dc=hdc, h_glrc=hglrc)
        session = xr.create_session(instance, xr.SessionCreateInfo(
            system_id=system_id,
            next=ctypes.pointer(binding),
        ))

    # reference space (world)
    ref_space = xr.create_reference_space(session, xr.ReferenceSpaceCreateInfo(
        reference_space_type=xr.ReferenceSpaceType.LOCAL,
        pose_in_reference_space=xr.Posef(),
    ))

    # --- eye gaze action ---
    action_set = xr.create_action_set(instance, xr.ActionSetCreateInfo(
        action_set_name="gaze_set",
        localized_action_set_name="Gaze Set",
        priority=0,
    ))
    gaze_action = xr.create_action(action_set, xr.ActionCreateInfo(
        action_type=xr.ActionType.POSE_INPUT,
        action_name="eye_gaze",
        localized_action_name="Eye Gaze",
    ))

    gaze_path = xr.string_to_path(instance, "/user/eyes_ext/input/gaze_ext/pose")
    xr.suggest_interaction_profile_bindings(
        instance,
        xr.InteractionProfileSuggestedBinding(
            interaction_profile=xr.string_to_path(
                instance, "/interaction_profiles/ext/eye_gaze_interaction"
            ),
            suggested_bindings=[
                xr.ActionSuggestedBinding(action=gaze_action, binding=gaze_path),
            ],
        ),
    )
    xr.attach_session_action_sets(session, xr.SessionActionSetsAttachInfo(
        action_sets=[action_set],
    ))

    gaze_space = xr.create_action_space(session, xr.ActionSpaceCreateInfo(
        action=gaze_action,
        pose_in_action_space=xr.Posef(),
    ))

    # --- event + gaze loop ---
    session_state = xr.SessionState.IDLE
    running       = False

    print("[EyeWorker] Waiting for session FOCUSED...", flush=True)

    while True:
        # drain events
        try:
            while True:
                event = xr.poll_event(instance)
                etype = event.type
                if etype == xr.StructureType.EVENT_DATA_SESSION_STATE_CHANGED:
                    ev = ctypes.cast(
                        ctypes.pointer(event),
                        ctypes.POINTER(xr.EventDataSessionStateChanged),
                    ).contents
                    session_state = xr.SessionState(ev.state)
                    print(f"[EyeWorker] Session state -> {session_state.name}", flush=True)

                    if session_state == xr.SessionState.READY:
                        begin_ci = xr.SessionBeginInfo(
                            primary_view_configuration_type=xr.ViewConfigurationType.PRIMARY_STEREO,
                        )
                        if headless:
                            # headless sessions don't need a view config
                            begin_ci = xr.SessionBeginInfo()
                        xr.begin_session(session, begin_ci)
                        running = True

                    elif session_state in (
                        xr.SessionState.STOPPING,
                        xr.SessionState.LOSS_PENDING,
                        xr.SessionState.EXITING,
                    ):
                        if running:
                            xr.end_session(session)
                        _write(shm, status=STATUS_IDLE)
                        print("[EyeWorker] Session ended.", flush=True)
                        return

        except xr.exception.EventUnavailable:
            pass

        if not running or session_state not in (
            xr.SessionState.SYNCHRONIZED,
            xr.SessionState.VISIBLE,
            xr.SessionState.FOCUSED,
        ):
            time.sleep(0.005)
            continue

        # sync actions
        xr.sync_actions(session, xr.ActionsSyncInfo(
            active_action_sets=[xr.ActiveActionSet(action_set=action_set)],
        ))

        # get gaze pose — for non-headless we need a frame time
        if headless:
            display_time = xr.Time(int(time.perf_counter() * 1e9))
        else:
            try:
                frame_state = xr.wait_frame(session)
                xr.begin_frame(session)
                display_time = frame_state.predicted_display_time
            except Exception:
                time.sleep(0.005)
                continue

        try:
            loc   = xr.locate_space(gaze_space, ref_space, display_time)
            valid = bool(loc.location_flags & xr.SpaceLocationFlags.ORIENTATION_VALID_BIT)

            if valid:
                q = loc.pose.orientation
                gx, gy, gz = _quat_to_ursina_fwd(q.x, q.y, q.z, q.w)
                _write(shm, gx, gy, gz, conf=1.0, status=STATUS_OK)
            else:
                _write(shm, 0, 0, 1, conf=0.0, status=STATUS_OK)

        except Exception as e:
            print(f"[EyeWorker] locate_space error: {e}", flush=True)
            _write(shm, 0, 0, 1, conf=0.0, status=STATUS_OK)

        finally:
            if not headless:
                try:
                    xr.end_frame(session, xr.FrameEndInfo(
                        display_time=display_time,
                        environment_blend_mode=xr.EnvironmentBlendMode.OPAQUE,
                        layers=[],
                    ))
                except Exception:
                    pass


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    shm = mmap.mmap(-1, GAZE_SIZE, tagname=SHM_NAME)
    _write(shm, status=STATUS_IDLE)
    try:
        _run(shm)
    except Exception as e:
        print(f"[EyeWorker] Unhandled error: {e}", flush=True, file=sys.stderr)
        _write(shm, status=STATUS_ERROR)
    finally:
        shm.close()
