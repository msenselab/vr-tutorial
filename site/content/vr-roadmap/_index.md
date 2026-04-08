---
title: "VR Roadmap"
description: "The path from desktop 3D to headset VR"
weight: 4
---

Everything you have built in this tutorial runs on a regular monitor. This page explains what changes when you move to a VR headset -- and what stays the same.

## When Desktop 3D Is Enough

Desktop 3D is sufficient for many research questions:

- **Spatial navigation studies** where participants use keyboard/gamepad to move through environments.
- **3D visual search** where stimuli are placed in a scene and responses are collected via button press.
- **Experiment prototyping** -- test your paradigm on a monitor before investing in VR hardware.

Desktop 3D gives you full control over timing, synchronization, and data logging without the complexity of headset management.

## When You Need a Headset

Move to VR when your research question requires:

- **Head tracking** -- measuring where participants look with 6 degrees of freedom.
- **Stereoscopic depth** -- true binocular disparity that a flat monitor cannot provide.
- **Hand/controller tracking** -- reaching, grasping, or pointing in 3D space.
- **Immersion/presence** as an independent variable -- comparing conditions with and without embodiment.
- **Ecological validity** -- creating environments that feel spatially real.

## What Changes for VR

### Rendering

A VR headset requires **stereoscopic rendering**: two slightly offset camera views, one for each eye. The engine must render the scene twice per frame at a high refresh rate (72-120 Hz, depending on the headset). This is the biggest technical change.

### Head Tracking

The headset reports its position and orientation every frame. The camera must follow the headset's pose instead of being controlled by the mouse. This replaces `FirstPersonController` with a VR-aware camera rig.

### Controller Tracking

VR controllers replace keyboard and gamepad. Each controller provides position, orientation, and button states. The input handling logic changes, but the principle is the same: poll the device, apply dead zones, translate to player actions.

### Performance

VR demands consistent frame rates. Dropped frames cause motion sickness. You may need to:

- Simplify geometry (fewer polygons per scene).
- Reduce texture resolution.
- Limit the number of dynamic objects.
- Profile and optimize your update loop.

## What Stays the Same

The good news: most of your experiment code is unaffected.

- **Scene building** -- walls, floors, objects, textures, and lighting work identically. An `Entity(model='cube', ...)` is the same in VR and on a monitor.
- **State machine** -- the experiment flow (INSTRUCTION, FIXATION, TASK, FEEDBACK) does not change.
- **Data logging** -- CSV writing, timing, and trigger codes are independent of the display.
- **Trial sequencing** -- conditions, repeats, randomization, and counterbalancing are pure logic.
- **Trigger codes** -- EEG synchronization is a hardware signal, unrelated to display mode.

Roughly 80% of a well-structured experiment codebase transfers directly from desktop to VR.

## Panda3D OpenXR Integration

Ursina is built on [Panda3D](https://www.panda3d.org/), which supports VR through the [OpenXR](https://www.khronos.org/openxr/) standard. OpenXR is the cross-platform API for VR and AR headsets, supported by Meta Quest, Valve Index, HTC Vive, and others.

The integration works by:

1. Initializing an OpenXR session instead of a regular window.
2. Creating a stereo camera rig that renders left and right eye views.
3. Submitting each frame to the headset compositor.
4. Reading headset and controller poses each frame.

Panda3D's OpenXR support is available through community plugins. The most active implementation is [panda3d-simplepbr](https://github.com/Moguri/panda3d-simplepbr) combined with [panda3d-openxr](https://github.com/nicoco007/panda3d-openxr).

## Code Comparison: Desktop vs VR

The changes are concentrated in initialization and camera setup. Here is a simplified comparison:

### Desktop (what you built)

```python
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Scene building -- identical in VR
floor = Entity(model='quad', scale=(20, 20), rotation_x=90,
               texture='grass', collider='box')
Sky()

# Desktop camera
player = FirstPersonController()
player.gravity = 0

app.run()
```

### VR (what changes)

```python
from ursina import *
from panda3d_openxr import OpenXRSession

app = Ursina()

# Scene building -- identical to desktop
floor = Entity(model='quad', scale=(20, 20), rotation_x=90,
               texture='grass', collider='box')
Sky()

# VR camera rig (replaces FirstPersonController)
xr_session = OpenXRSession()
xr_session.attach_to(app)

def update():
    # Read headset pose
    head_pos, head_rot = xr_session.get_head_pose()
    camera.position = head_pos
    camera.rotation = head_rot

    # Read controller input
    left_stick = xr_session.get_controller_axis('left', 'thumbstick')
    # ... move player based on stick input ...

app.run()
```

The scene-building code is unchanged. The state machine, data logging, and trigger code are unchanged. Only the input and camera sections differ.

## Alternative Paths

### OpenHMD

[OpenHMD](http://www.openhmd.net/) is an older, lightweight library for headset access. It supports fewer headsets than OpenXR but may be simpler for specific hardware. Suitable when you need basic head tracking without full controller support.

### WebXR

[WebXR](https://immersiveweb.dev/) runs VR experiences in a web browser. Libraries like [A-Frame](https://aframe.io/) or [Three.js](https://threejs.org/) make it easy to create browser-based VR. The trade-off: less precise timing and harder EEG synchronization, but excellent for online studies and demonstrations.

### Unity and Unreal Engine

For projects that outgrow Python -- large environments, complex physics, photorealistic rendering -- Unity (C#) and Unreal Engine (C++/Blueprints) are industry standards. The experiment design patterns (state machine, trial sequencing, data logging) transfer directly; only the programming language and engine API change.

## Recommended VR Hardware for Research

| Headset         | Standalone | PC-Tethered | Eye Tracking | Best For                     |
|-----------------|:----------:|:-----------:|:------------:|------------------------------|
| Meta Quest 3    | Yes        | Yes         | No           | General-purpose, affordable  |
| Meta Quest Pro  | Yes        | Yes         | Yes          | Eye tracking research        |
| HTC Vive Pro Eye| No         | Yes         | Yes          | Lab-based EEG + eye tracking |
| Valve Index     | No         | Yes         | No           | High refresh rate, finger tracking |
| Varjo Aero      | No         | Yes         | Yes          | Highest visual fidelity      |

**For getting started**: Meta Quest 3 offers the best balance of cost, quality, and compatibility. It works standalone (no PC required) and tethered (for Panda3D/OpenXR integration).

**For EEG research**: HTC Vive Pro Eye or Meta Quest Pro provide eye tracking alongside head tracking. The Vive's rigid strap design is more compatible with EEG caps.

**For maximum quality**: Varjo Aero offers near-retinal resolution, but at a significantly higher price point.
