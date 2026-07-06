# Blender Python Automated New Year Animation

A Python-scripted 3D physics animation built entirely within Blender via the `bpy` (Blender Python) API. The project implements a dynamic dual-layered particle and rigid body simulation where stylized "2026" rigid bodies undergo realistic gravitational decay while ambient snowflakes are subjected to turbulent vector force fields (wind and vortex effects), creating a visually engaging New Year celebration sequence.

---

## 🚀 Features

* **Procedural Scene Generation:** Instantiates 3D typography, environmental elements, and lighting arrays entirely via Python scripts.
* **Rigid Body Dynamics (2026 Typography):** Simulates mass, friction, and collision bounds for volumetric text meshes as they drop into the scene under gravitational acceleration.
* **Complex Force Field Interactions:** Utilizes localized Vector Fields (Wind and Vortex forces) to drive high-fidelity turbulence, swirling, and drifting patterns into a customized particle system simulating snow.
* **Automated Rendering Pipeline:** Programmatically configures camera focal tracking, cycles/eevee engine parameters, output resolution, and frame ranges before executing a batch render.

---

## 🛠️ Project Structure

To mirror professional standards, arrange your repository files as follows:

```text
Blender-NewYear-Animation/
├── assets/
│   ├── snowy.png
│   └── snowyDark.png
│   └── snowyFog.png
│   └── snowFlakeXobj.mtl
│   └── snowFlakeXobj.obj
│   └── NewYear2026.mp4         # Rendered MP4 output or loop GIF showing physics in action
├── src/
│   └── CreateNewYearScene.py   # The core Python script executed inside Blender's scripting console
│   └── bco602tk.py             # Toolkit
├── .gitignore                  # Ignores local .blend1 backups and temporary cash files
└── README.md                   # Project landing page documentation