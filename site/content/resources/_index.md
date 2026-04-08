---
title: "Resources"
description: "Links, documentation, and further reading"
weight: 5
---

## Documentation

| Resource | URL | Description |
|----------|-----|-------------|
| Ursina Engine | [ursinaengine.org](https://www.ursinaengine.org/) | Official docs, API reference, examples |
| Panda3D Manual | [docs.panda3d.org](https://docs.panda3d.org/1.10/python/) | Ursina's rendering backend; deep technical reference |
| pygame Documentation | [pygame.org/docs](https://www.pygame.org/docs/) | Joystick, audio, and event handling |
| OpenXR Specification | [khronos.org/openxr](https://www.khronos.org/openxr/) | The cross-platform VR/AR standard |

## Tutorial Materials

| Resource | URL | Description |
|----------|-----|-------------|
| Tutorial Repository | [github.com/strongway/vr-tutorial](https://github.com/strongway/vr-tutorial) | All exercises, slides, and this site |
| MazeWalker-Py | [github.com/strongway/mazewalker-py](https://github.com/strongway/mazewalker-py) | Production experiment codebase (capstone) |

## VR in Research

### Key Papers

- **Parsons, T. D. (2015).** Virtual Reality for Enhanced Ecological Validity and Experimental Control in the Clinical, Affective and Social Neurosciences. *Frontiers in Human Neuroscience*, 9, 660. -- A comprehensive overview of VR applications in neuroscience research.

- **Pan, X., & Hamilton, A. F. de C. (2018).** Why and how to use virtual reality to study human social interaction. *British Journal of Psychology*, 109(3), 395-417. -- Practical guidance on using VR for social cognition experiments.

- **Hofmann, S. M., et al. (2021).** Decoding subjective emotional arousal during a naturalistic VR experience from EEG signals. *Brain-Computer Interfaces*, 8(4), 154-163. -- Combining VR with EEG for naturalistic neuroscience.

- **Makeig, S., et al. (2009).** Linking brain, mind and behavior. *International Journal of Psychophysiology*, 73(2), 95-100. -- The Mobile Brain/Body Imaging (MoBI) framework for studying brain activity during natural movement, foundational for VR-EEG research.

### VR Experiment Toolkits

| Toolkit | Language | Strengths |
|---------|----------|-----------|
| Ursina + pygame (this tutorial) | Python | Rapid prototyping, accessible, good for researchers who know Python |
| [Vizard](https://www.worldviz.com/vizard-virtual-reality-software) | Python | Commercial VR toolkit with built-in eye tracking and motion capture |
| [PsychoPy](https://www.psychopy.org/) | Python | Established experiment framework, VR support via plugins |
| [OpenSesame](https://osdoc.cogsci.nl/) | Python | GUI-based experiment builder with VR extensions |
| [Unity](https://unity.com/) | C# | Industry standard, massive ecosystem, steep learning curve |
| [Unreal Engine](https://www.unrealengine.com/) | C++/Blueprints | Photorealistic rendering, high complexity |

## Community

| Community | URL | Topic |
|-----------|-----|-------|
| Ursina Discord | [discord.gg/ursina](https://discord.gg/ursina) | Ursina engine help and discussion |
| Panda3D Forums | [discourse.panda3d.org](https://discourse.panda3d.org/) | Technical questions about the rendering backend |
| pygame Community | [pygame.org/wiki/community](https://www.pygame.org/wiki/community) | Input handling, audio, general pygame |
| r/VRresearch | [reddit.com/r/VRresearch](https://www.reddit.com/r/VRresearch/) | VR methodology and research discussion |
| OpenXR Working Group | [khronos.org/openxr](https://www.khronos.org/openxr/) | VR standard development and specifications |

## Recommended Reading

### For Going Deeper with Python Game Engines

- **Panda3D Programming** -- The official Panda3D manual covers scene graphs, shaders, physics, and networking in depth. Since Ursina is built on Panda3D, understanding the backend gives you more control.

- **Real-Time Rendering** (Akenine-Moller, Haines, Hoffman) -- The definitive reference for understanding how 3D graphics work under the hood. Useful when optimizing VR performance.

### For Experiment Design

- **Mathot, S. (2017).** *Building Experiments in PsychoPy.* -- While focused on PsychoPy, the experiment design patterns (state machines, trial sequencing, counterbalancing) apply directly to Ursina-based experiments.

- **Brysbaert, M. & Stevens, M. (2018).** Power analysis and effect size in mixed-effects models. *Journal of Cognition*, 1(1), 9. -- Essential for planning VR experiments where repeated measures and between-subject comparisons are common.

### For VR Development

- **LaViola, J., et al. (2017).** *3D User Interfaces: Theory and Practice* (2nd ed.). -- Covers interaction design for VR, including navigation, selection, and manipulation techniques relevant to experiment design.

- **Jerald, J. (2015).** *The VR Book: Human-Centered Design for Virtual Reality.* -- Practical guidance on avoiding simulator sickness, designing comfortable experiences, and understanding perceptual factors.
