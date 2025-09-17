# Galaga3D — Feature Specifications

This document lists the features, acceptance criteria, edge cases, test plans, and API contract for the Galaga3D library and demo.

## Goals
- Provide a small, embeddable 3D Galaga-like library with a simple API.
- Ship a single-file bundle (`dist/galaga3d.bundle.js`) that works offline (no CDN at runtime).
- Offer a small demo page and an embed example for integration testing and demos.
- Provide minimal visual polish (explosions, bobbing enemies) and reliable core gameplay (movement, shooting, collisions, scoring).
- Be testable: include an automated smoke test and clear unit test targets for pure logic.

## Non-goals
- Be an exact remake of Galaga or include advanced physics. This is a lightweight demo library for embedding and educational use.
- Provide heavy assets, large audio packs or networked multiplayer in this initial iteration.

## High-level feature list

1. Core gameplay
   - Player ship with movement (left/right/up/down) and shooting. (Controls: arrow keys, Space)
   - Enemies arranged in formation, moving in a sweep and performing occasional breach/dive behaviors.
   - Bullets (player) with collision detection against enemies.
   - Scoring for destroyed enemies.
   - Restart/Reset and Pause/Start controls.

2. Visuals and effects
   - Simple low-poly player/enemy meshes using Three.js primitives.
   - Starfield background made with point cloud.
   - Explosion particle effect on enemy death.

3. Build & Distribution
   - ES module source in `src/` and a bundle built with esbuild into `dist/galaga3d.bundle.js`.
   - Demo page that loads the local bundle (no CDN reliance at runtime).

4. API
   - `new Galaga3D(container, opts)` — constructor. `container` can be DOM element or selector.
   - Instance methods: `start()`, `pause()`, `reset()`, `dispose()`.
   - Event hooks: `onScore` callback invoked with the new score.
   - Library should attach constructor to `window.Galaga3D` for non-module consumers.

5. Tests
   - Playwright smoke test that serves `dist/` and verifies `window.Galaga3D` is present.
   - Unit tests for pure logic items (collision distance, enemy spawn math, clamp behavior).

## Acceptance criteria (per feature)

- Player movement: Player responds to Arrow keys and remains within bounds X ∈ [-8,8], Y ∈ [-3,8]. Tests: automated keyboard simulation and position assertions.
- Shooting: Pressing Space creates a bullet mesh that travels forward and is removed after z < -200 or on collision. Tests: spawn bullet, advance simulation, assert removal.
- Enemy formation: On `spawnEnemies()` enemies are added (rows x cols). Acceptance: enemyList length equals rows*cols immediately after spawn.
- Collision: When bullet collides with enemy (distance < sum radii) the enemy is removed, score increases by 100, explosion effect created. Tests: unit test for distance vs. radii and smoke integration to visually confirm explosions appear.
- Scoring: `onScore` is called on score changes with correct cumulative total.
- Bundle: `npm run build` must produce `dist/galaga3d.bundle.js`. The Playwright smoke test must detect `window.Galaga3D` when loading the bundled demo. (Smoke test passes.)

## API contract (2–4 bullets)
- Inputs: `container` (DOM element | CSS selector), `opts` (object with optional fields: `onScore` callback). No network inputs required at runtime.
- Outputs: instance with methods `start()`, `pause()`, `reset()`, `dispose()`; side-effect updates on the DOM (canvas) and `onScore` callback.
- Errors: constructor should throw if WebGL is not available or Three.js cannot be resolved at runtime (module bundle ensures Three is present).
- Success: the game loop runs and `renderer.domElement` is attached to `container` and visible.

## Data shapes
- Enemy object (Three Mesh) — `mesh.userData` should contain at least: `{ radius: number, hit: boolean, basePos?: Vector3, bobPhase?: number, bobAmp?: number, bobFreq?: number }`.
- Bullet object — `mesh.userData` should contain `{ vel: Vector3, radius: number }`.
- Explosion effect — Points object with `userData = { life: number, update: function }`.

## Edge cases and error handling
- Multiple instances: ensure two Galaga3D instances can be constructed in different containers without global collision of event handlers. (Use instance-bound handlers or namespaced events.)
- Resize during run: the canvas and camera must update on window resize.
- Missing WebGL: detect WebGL and throw a clear error for environments without WebGL support.
- Very long runs: ensure memory doesn't leak; removed meshes are disposed and explosion particle systems self-clean after life expiration.

## Test matrix and cases (detailed)

Unit tests (suggested, pure js functions)
- collision.spec.js
  - test distance < sum radii => collision
  - test distance >= sum radii => no collision

- clamp.spec.js
  - test player clamp function clamps correctly for boundary inputs

Integration / smoke tests
- smoke/sanity (Playwright)
  - Start a simple HTTP server serving `dist/` and open `dist/index.html` in headless Chromium. Assert `window.Galaga3D` exists (already implemented at `test/smoke.js`).
  - Optional: take a screenshot after 1 second and ensure the canvas exists.

End-to-end behavior tests (run in headful mode manually or in CI with graphics)
- e2e/shooting.test.js (Playwright in headed browser)
  - Simulate ArrowRight + Space, assert score increased after hitting an enemy.

Performance tests
- Verify 60fps target on modern desktop browsers; add a benchmark harness that measures frame render time over 5 seconds and reports the 95th percentile.

CI and automation
- CI steps (GitHub Actions recommended):
  1. checkout
  2. npm ci
  3. npm run build
  4. npx playwright install --with-deps
  5. npm run test:smoke
  6. optional: run unit tests (jest) on logic files

## UX notes / controls
- Controls: Arrow keys for movement; Space to shoot; HUD buttons for Start/Pause/Reset.
- HUD should be minimal and unobtrusive; the demo currently exposes these elements for easy testing.

## Acceptance checklists for reviewers
- [ ] Build passes locally (produces `dist/galaga3d.bundle.js`).
- [ ] Smoke test passes (`test/smoke.js` prints `Galaga3D constructor exists: true`).
- [ ] Demo `dist/index.html` renders and a player can move and shoot.
- [ ] Basic visual effects (explosion) appear when enemies are destroyed.

## Next steps and backlog (short)
1. Add a CI workflow for build + smoke test.
2. Add unit tests for collision logic and enemy spawn math.
3. Add audio effects and concise asset pipeline if desired.
4. Polish visuals: better enemy/player meshes (low-poly models) and sprite textures.

---
Generated on: 2025-09-17
