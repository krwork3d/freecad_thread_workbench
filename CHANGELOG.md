# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.1] — 2026-07-01

### Added
- BSP (Whitworth 55°) thread profile support with presets (`G` series).
- Semi-transparent shaded mesh preview via the thread surface builder.
- `resolve_thread_frame()` — unified function for consistent thread direction and origin calculation across the builder and preview pipeline.

### Changed
- **Major refactor:** project restructured from flat layout to a modular package under [`freecad/ThreadWorkbench/`](freecad/ThreadWorkbench/__init__.py:1).
- Helix line and thread surface builders now share a unified twist‑sign convention for consistent winding direction.
- Helix and profile‑line functions accept an explicit `axis` parameter instead of the previous `cut_dir`.
- Edge‑selection handling in the creation mixin has been improved for robustness.

### Fixed
- Edge‑to‑edge thread length and pocket runout boundary now match the actual geometry.
- Gaps caused by the `clearance` parameter in `fill_pocket` eliminated; radii are now calculated directly without a separate clearance value.
- Thread direction logic simplified; UI edge‑selection reset on direction change fixed.

### Removed
- `clearance` parameter from [`fill_pocket()`](freecad/ThreadWorkbench/geometry/runout/pocket.py:1) — no longer needed with the updated radius calculations.

## [0.2.0] — 2025-06-07

### Changed
- Project restructured to a modern modular package layout.
- README and `package.xml` updated for clarity and accuracy.

## [0.1.3] — 2025-05-12

### Fixed
- Translations updated for consistency and clarity.

### Changed
- First round of internal refactoring.
- Added `.gitattributes` for consistent line endings across platforms.

## [0.1.2] — 2025-05-05

### Changed
- Version bumped across `Init.py`, `package.xml`, and `README.md`.

## [0.1.1] — 2025-05-03

### Added
- English translation file (`translations/ThreadWorkbench_en.ts`).
- Screenshots and example GIF added to README.

### Changed
- Package metadata and README version bumped to 0.1.1.

## [0.1.0] — 2025-05-01

### Added
- Initial release of Thread Workbench.
- Metric and inch thread creation (ISO 68-1 and ASME B1.1 profiles).
- Automatic diameter / pitch selection from standard series.
- External and internal thread support.
- Edge offset, left‑hand thread, reverse direction options.
- Smooth runout (additive revolution) at the thread end.
- Live geometry preview before committing.
- Russian UI translation.

[Unreleased]: https://github.com/krwork3d/freecad_thread_workbench/compare/v0.3.1...HEAD
[0.3.1]: https://github.com/krwork3d/freecad_thread_workbench/compare/v0.2.0...v0.3.1
[0.2.0]: https://github.com/krwork3d/freecad_thread_workbench/compare/v0.1.3...v0.2.0
[0.1.3]: https://github.com/krwork3d/freecad_thread_workbench/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/krwork3d/freecad_thread_workbench/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/krwork3d/freecad_thread_workbench/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/krwork3d/freecad_thread_workbench/releases/tag/v0.1.0
