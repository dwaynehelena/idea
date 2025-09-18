# Architecture

Key components in `astonish.py`:

- `Image` — a minimal float buffer (linear [0..1]) with tone mapping and PPM writer. 【F:astonish.py†L1-L120】
- `ValueNoise2D` — tileable value noise used to drive the flow-field. 【F:astonish.py†L122-L170】
- `render_flow_field` — particle integrator that deposits colored samples into the `Image`. Particles are initialized in a loose ring and follow a fractal noise-derived vector field. 【F:astonish.py†L172-L270】
- `render_orbit_trap` — Mandelbrot orbit trap renderer that colors pixels based on proximity to a chosen trap. 【F:astonish.py†L272-L356】
- `ascii_preview` — a downsampling luminance-based ASCII preview for quick terminal checks. 【F:astonish.py†L247-L318】

Design notes:

- The renderer uses simple multi-sample deposits per particle step to reduce aliasing.
- Tone mapping applies a filmic roll-off and gamma correction for visually pleasing colors.
