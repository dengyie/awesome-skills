# GPUI Liquid Glass

Use `gpui-liquid-glass` when implementing, repairing, or analyzing Apple Native Liquid Glass and vibrancy effects in Rust GPUI desktop applications.

The skill guides agents to select AppKit materials (`NSGlassEffectView` for macOS 26+ and `NSVisualEffectView` for legacy fallbacks), structure transparent windows and background composition, synchronize dynamic layout geometries, and maintain accessibility and graceful cross-platform degradation.

## What it covers

- macOS 26+ `NSGlassEffectView` and `NSGlassEffectContainerView` native glass materials.
- Legacy macOS vibrancy fallback with `NSVisualEffectView`.
- Glass sidebars, floating toolbar capsules, HUD cards, and GPUI interactive states.
- Background sources (desktop sampling vs within-window content refraction).
- Native view lifecycles, clipping masks, window resizing, animations, and clean teardown.
- Runtime class availability guards to prevent crashes on older macOS versions.
- Real-window verification methods for visual sampling, theme harmony, and accessibility settings.

If you are still choosing among skills, go back to the [Skill Matrix](skill-matrix.md). If you only need installation help, use the [Quickstart](quickstart.md).

## Related docs

- [Skill Matrix](skill-matrix.md)
- [Quickstart](quickstart.md)
- [Examples](examples.md)
- [Troubleshooting](troubleshooting.md)

## Read What Where

- `gpui-liquid-glass/SKILL.md`: agent-facing workflow entrypoint and composition boundaries
- `gpui-liquid-glass/references/macos-bridge.md`: Rust AppKit bridge examples, runtime availability checks, and Cargo features
- `gpui-liquid-glass/references/verification.md`: real-window sampling verification and debugging checklist
