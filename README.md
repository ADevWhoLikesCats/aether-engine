# web-engine

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

A hand-written 3D graphics engine that runs in a web browser. Written in C,
compiled to WebAssembly with Emscripten, rendering through WebGL2.

The current demo renders a Lamborghini Revuelto on a reflective ground
plane with full global illumination, real-time reflections, temporal
anti-aliasing, bloom, depth of field, and shadows — all running at
interactive framerates on integrated GPUs.

![Demo Image](demo.png)

## Features

**Rendering**
- Physically-based rendering (Cook-Torrance BRDF, split-sum IBL)
- HDR rendering into `RGBA16F` targets
- 4-attachment G-buffer (lit scene, albedo, normal+roughness, emissive)
  for downstream post-processing and screen-space effects
- ACES filmic tonemapping, sRGB output
- Deferred-style scene capture for post-processing

**Global illumination**
- Spherical Harmonic (SH L2) diffuse GI, prebaked into a 3D probe grid
- Spherical Gaussian (SG) specular GI — 32 lobes per probe, ray-traced
  against the actual car mesh with a uniform-triangle-grid acceleration
  structure
- Probe-grid parallax: reflections change as objects move through the world

**Reflections**
- Screen-space reflections (SSR) with Fresnel-weighted compositing
- SG probe reflections as off-screen fallback
- Reflective ground plane

**Anti-aliasing & post**
- TAA with Halton sub-pixel jitter, history buffer, neighborhood clamp
- SSAO with per-pixel hemisphere sampling and separable blur
- Bloom with a dual-filter additive pyramid
- Depth of field with adjustable focus and bokeh radius
- Volumetric fog with shadow-sampled god rays
- Directional shadow map

**Asset pipeline**
- glTF 2.0 model loading (.glb), materials, textures, and mesh merging
- HDRI environment loading (equirectangular .hdr)
- Procedural sky with sun disk and atmospheric gradient

## Architecture

- src/main.c        - engine setup, frame loop, input
- src/pass.c        - fullscreen-triangle "fake compute" abstraction
- src/framebuffer.c - FBO and float-texture helpers, G-buffer support
- src/mesh.c        - glTF loader + merge by material
- src/capture.c     - octahedral scene capture
- src/tri_grid.c    - uniform triangle grid for ray tracing
- src/probe_grid.c  - DDGI-style SH/SG probe bake
- src/sh.c, sg.c    - SH and SG utilities
- src/bloom.c       - dual-filter bloom pipeline
- src/shadow.c      - directional shadow map
- src/ground.c      - reflective ground plane mesh
- src/hdr_env.c     - equirectangular HDRI loader
- src/texture.c     - texture creation helpers
- src/asset.c       - virtual filesystem asset loading

Key shaders:
- shaders/fullscreen.vert     - gl_VertexID fullscreen triangle
- shaders/pbr.vert, pbr.frag  - main PBR shader with 4-output MRT
- shaders/probe_bake.frag     - ray-traced SG probe bake
- shaders/octa_capture.frag   - octahedral scene capture
- shaders/sh_project.frag     - SH projection
- shaders/sh_reconstruct.frag - SH reconstruction
- shaders/sg_fit.frag         - SG fitting
- shaders/sky_background.frag - procedural sky + HDRI
- shaders/ssr.frag, ssr_composite.frag
- shaders/ssao.frag, ssao_blur.frag
- shaders/taa_resolve.frag
- shaders/dof.frag
- shaders/fog_raymarch.frag, fog_composite.frag
- shaders/bloom_*.frag
- shaders/shadow_depth.vert, .frag

## Requirements

- Emscripten SDK (emsdk): https://emscripten.org/docs/getting_started/downloads.html
- Python 3 (for the local development server)
- A browser with WebGL2 support and `EXT_color_buffer_float`
  (Chrome, Firefox, Edge, Safari 15+)

## Build

Set up emsdk once:

    git clone https://github.com/emscripten-core/emsdk.git
    cd emsdk
    ./emsdk install latest
    ./emsdk activate latest
    source ./emsdk_env.sh

Then build and run:

    make
    make serve

Open http://localhost:8000/triangle.html

## Controls

- M: cycle debug modes (0-15)
- T: toggle TAA
- F: toggle fog
- O: toggle depth of field
- V: toggle debug overlays
- [ / ]: lower / raise roughness scale
- - / =: pull / push DOF focus distance
- ; / ': decrease / increase DOF blur radius

## Debug modes

- 0: Full PBR render
- 1: Diffuse only
- 2: Specular only
- 3: Fresnel term
- 4: Roughness
- 5: Metalness
- 6: SH irradiance (indirect diffuse)
- 7: World-space normals
- 8: SG reflections (indirect specular)
- 9: Reflection vector
- 10: Shadow factor
- 11: Grid coordinates
- 12: SSR buffer
- 13: Bloom pyramid
- 14: G-buffer albedo
- 15: SSGI output

## WebGL2 notes

The engine relies on a few WebGL2 features that aren't universally
available and need explicit handling:

- **`EXT_color_buffer_float`** must be enabled on the context for
  `RGBA16F` and `RGBA32F` framebuffers to be color-renderable. Without it,
  framebuffer creation silently returns
  `GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT (0x8CD6)`. The engine calls
  `emscripten_webgl_enable_extension` for this at context creation.
- **`glDrawBuffers` is per-context, not per-FBO.** When switching between
  a multi-attachment G-buffer and a single-attachment FBO, the draw buffer
  list must be reset on every bind. Otherwise the next draw raises
  `GL_INVALID_OPERATION (0x0502)`.
- **Depth textures, not renderbuffers, for any FBO whose depth is
  sampled.** SSAO, SSR, fog, and DOF all read scene depth as a texture.
  A renderbuffer cannot be bound as a sampler.

## Performance notes

The engine is designed to run on modest hardware. It targets 60 fps at
1080p on Intel HD Graphics 400 (2012 integrated GPU) with the following
optimizations:

- Prebaked GI: SH probes and SG reflections are computed once at startup,
  not per frame
- Mesh merging: glTF primitives with identical materials are merged into
  a single draw call (560 to about 10 draws for the demo car)
- Triangle grid: a uniform 32x16x32 grid accelerates the SG bake's
  ray-scene intersection
- TAA: sub-pixel jitter lets the pipeline average multiple samples over
  time instead of paying for them per frame

Startup time is dominated by the SG bake (about 2 s on Intel HD 400) and
mesh merging.

## The demo

- Car: Lamborghini Revuelto (free low-poly 3D model) by AnatolianStudios
  on CGTrader: https://www.cgtrader.com/items/7588572
- HDRI: studio_small_09 from Poly Haven (CC0):
  https://polyhaven.com/a/studio_small_09

See NOTICE for full attribution.

## Downstream forks

- **Afterburn** — a flight simulator built on this engine. Adds
  International Standard Atmosphere, real aerodynamic moment equations,
  fly-by-wire rate command, deterministic 240 Hz physics, enemy AI,
  missiles, and a full F-16 HUD.
  https://github.com/ADevWhoLikesCats/Afterburn

## License

The engine source is licensed under the Apache License, Version 2.0. See
LICENSE for the full text.

Third-party software and asset attributions are listed in NOTICE.

## Contributing

Issues and pull requests are welcome. By submitting a contribution, you
agree to license it under the Apache License, Version 2.0 (per Section 5
of the license).
