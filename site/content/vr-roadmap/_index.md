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

## Panda3D VR Integration

Ursina is built on [Panda3D](https://www.panda3d.org/), which supports VR through community plugins. Two options are available, both by the same author ([el-dee](https://github.com/el-dee)):

| Package | Standard | Install | Best for |
|---------|----------|---------|----------|
| [panda3d-openxr](https://github.com/el-dee/panda3d-openxr) | OpenXR | `pip install panda3d-openxr` | New projects (industry standard) |
| [panda3d-openvr](https://github.com/el-dee/panda3d-openvr) | OpenVR/SteamVR | `pip install panda3d-openvr` | More mature, action manifests, hand skeleton tracking |

Both require a **PC-tethered** headset. Standalone Quest apps are not supported -- the Quest must be connected via USB (Quest Link) or wirelessly (Air Link) so it acts as a PCVR display.

The integration works by:

1. Initializing an OpenXR (or OpenVR) session alongside the Panda3D window.
2. Creating a stereo camera rig that renders left and right eye views.
3. Submitting each frame to the headset compositor.
4. Providing anchor nodes for the headset and each hand controller that update their pose every frame.

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

# Desktop camera and movement
player = FirstPersonController()
player.gravity = 0

app.run()
```

### VR with panda3d-openxr (what changes)

```python
from ursina import *
from p3dopenxr.p3dopenxr import P3DOpenXR

app = Ursina()

# Scene building -- identical to desktop
floor = Entity(model='quad', scale=(20, 20), rotation_x=90,
               texture='grass', collider='box')
Sky()

# Initialize OpenXR -- connects to headset, starts stereo rendering
xr = P3DOpenXR()
xr.init()

# Attach visible models to tracked hand controllers
left_hand = Entity(model='cube', scale=0.1, color=color.azure)
left_hand.reparent_to(xr.left_hand_anchor)

right_hand = Entity(model='cube', scale=0.1, color=color.orange)
right_hand.reparent_to(xr.right_hand_anchor)

# Head tracking is automatic -- xr.hmd_anchor follows the headset

app.run()
```

### VR with panda3d-openvr (alternative, more features)

```python
from ursina import *
from p3dopenvr.p3dopenvr import P3DOpenVR

app = Ursina()

# Scene building -- identical
floor = Entity(model='quad', scale=(20, 20), rotation_x=90,
               texture='grass', collider='box')
Sky()

# Initialize OpenVR -- requires SteamVR running
ovr = P3DOpenVR()
ovr.init()

# When a controller is detected, attach a model to it
def on_new_device(device_index, device_anchor):
    marker = Entity(model='cube', scale=0.1, color=color.orange)
    marker.reparent_to(device_anchor)

ovr.set_new_tracked_device_handler(on_new_device)

app.run()
```

The scene-building code is unchanged across all three versions. The state machine, data logging, and trigger code are unchanged. Only initialization and input handling differ.

## Alternative Paths

### WebXR

[WebXR](https://immersiveweb.dev/) runs VR experiences in a web browser. Libraries like [A-Frame](https://aframe.io/) or [Three.js](https://threejs.org/) make it easy to create browser-based VR. The trade-off: less precise timing and harder EEG synchronization, but excellent for online studies and demonstrations.

### Unity and Unreal Engine

For projects that outgrow Python -- large environments, complex physics, photorealistic rendering -- Unity (C#) and Unreal Engine (C++/Blueprints) are industry standards. The experiment design patterns (state machine, trial sequencing, data logging) transfer directly; only the programming language and engine API change.

## Recommended VR Hardware for Research

| Headset              | Standalone | PC-Tethered | Eye Tracking | Best For                     |
|----------------------|:----------:|:-----------:|:------------:|------------------------------|
| Meta Quest 3/3S      | Yes        | Yes         | No           | General-purpose, affordable  |
| Meta Quest Pro       | Yes        | Yes         | Yes          | Eye tracking research        |
| HTC Vive Pro Eye     | No         | Yes         | Yes          | Lab-based EEG + eye tracking |
| Valve Index          | No         | Yes         | No           | High refresh rate, finger tracking |
| Pimax Crystal Super  | No         | Yes         | Yes          | Wide FOV, high resolution    |
| Varjo XR-4           | No         | Yes         | Yes          | Highest visual fidelity      |

**For getting started**: Meta Quest 3 offers the best balance of cost, quality, and compatibility. It works standalone (no PC required) and tethered (for Panda3D/OpenXR integration).

**For EEG research**: HTC Vive Pro Eye or Meta Quest Pro provide eye tracking alongside head tracking. The Vive's rigid strap design is more compatible with EEG caps.

**For maximum quality**: Varjo Aero offers near-retinal resolution, but at a significantly higher price point.
