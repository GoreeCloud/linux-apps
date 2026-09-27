"""Deterministic GoreeCloud Care adapter for GLAZE UI V1.4.1 Optical Intelligence.

The V1.4.0 resolver remains the bounded optical foundation. V1.4.1 adds a
fail-safe consumer-adapter boundary plus bounded downgrade-only performance
governance. Care does not collect environmental signals itself. Its default
runtime uses only already-known local UI state and requires no camera, wallpaper
inspection, telemetry, analytics, network, remote context, or device identity.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Protocol

LUMINANCE = frozenset({"dark", "mid", "bright", "unknown"})
COMPLEXITY = frozenset({"simple", "moderate", "complex", "unknown"})
DEPTH = frozenset({"base", "raised", "overlay", "modal"})
DAYPART = frozenset({"dawn", "day", "dusk", "night", "unknown"})
APPEARANCE = frozenset({"light", "dark", "deep-dark"})
PERFORMANCE_LEVELS = ("full", "balanced", "efficient", "durable")
MAX_MEMORY_TINT_INFLUENCE = 0.08


def _clamp(value: Any, minimum: float = 0.0, maximum: float = 1.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return minimum
    if number != number or number in (float("inf"), float("-inf")):
        return minimum
    return min(maximum, max(minimum, number))


def _bounded(value: Any, allowed: frozenset[str], fallback: str) -> str:
    return value if isinstance(value, str) and value in allowed else fallback


def _complexity_variance(value: str) -> float:
    return {"complex": 0.90, "moderate": 0.55, "simple": 0.18}.get(value, 0.45)


def _luminance_variance(value: str) -> float:
    return {"bright": 0.12, "dark": 0.06, "mid": 0.02}.get(value, 0.04)


def _depth_hue_shift(value: str) -> float:
    return {"raised": 0.012, "overlay": 0.022, "modal": 0.030}.get(value, 0.0)


def _warmth_for_daypart(value: str) -> float:
    return {"dawn": 0.035, "dusk": 0.045, "night": -0.018}.get(value, 0.0)


@dataclass(frozen=True)
class OpticalAccessibility:
    forced_colors: bool = False
    reduced_transparency: bool = False
    increased_contrast: bool = False
    reduced_motion: bool = False


@dataclass(frozen=True)
class MemoryTint:
    css: str
    influence: float


@dataclass(frozen=True)
class OpticalState:
    mode: str
    appearance: str
    background_complexity: str
    background_luminance: str
    depth: str
    daypart: str
    frost_strength: float
    blur_scale: float
    semantic_protection: float
    depth_hue_shift: float
    warmth: float
    memory_tint: MemoryTint | None
    decorative_tint_allowed: bool
    accessibility: OpticalAccessibility


@dataclass(frozen=True)
class OpticalResolution:
    state: OpticalState
    adapter_status: str
    requested_performance_level: str
    accepted_performance_level: str
    downgrade_reason: str | None


class SignalAdapter(Protocol):
    def resolve(self) -> Mapping[str, Any]:
        ...


def _normalize_accessibility(value: Any) -> OpticalAccessibility:
    source = value if isinstance(value, Mapping) else {}
    return OpticalAccessibility(
        forced_colors=bool(source.get("forcedColors", source.get("forced_colors", False))),
        reduced_transparency=bool(
            source.get("reducedTransparency", source.get("reduced_transparency", False))
        ),
        increased_contrast=bool(
            source.get("increasedContrast", source.get("increased_contrast", False))
        ),
        reduced_motion=bool(source.get("reducedMotion", source.get("reduced_motion", False))),
    )


def _normalize_memory_tint(value: Any) -> MemoryTint | None:
    if not isinstance(value, Mapping):
        return None
    css = value.get("css")
    if not isinstance(css, str) or not 1 <= len(css) <= 160:
        return None
    influence = _clamp(value.get("influence", 0.04), 0.0, MAX_MEMORY_TINT_INFLUENCE)
    if influence == 0:
        return None
    return MemoryTint(css=css, influence=influence)


def resolve_glaze_optics(options: Mapping[str, Any] | None = None) -> OpticalState:
    """Resolve the bounded V1.4 optical foundation without collecting context."""
    source: Mapping[str, Any] = options if isinstance(options, Mapping) else {}
    complexity = _bounded(source.get("backgroundComplexity"), COMPLEXITY, "unknown")
    luminance = _bounded(source.get("backgroundLuminance"), LUMINANCE, "unknown")
    depth = _bounded(source.get("depth"), DEPTH, "base")
    daypart = _bounded(source.get("daypart"), DAYPART, "unknown")
    appearance = _bounded(source.get("appearance"), APPEARANCE, "light")
    accessibility = _normalize_accessibility(source.get("accessibility"))

    if accessibility.forced_colors or accessibility.reduced_transparency:
        return OpticalState(
            mode="solid-accessible",
            appearance=appearance,
            background_complexity=complexity,
            background_luminance=luminance,
            depth=depth,
            daypart=daypart,
            frost_strength=1.0,
            blur_scale=0.0,
            semantic_protection=1.0,
            depth_hue_shift=0.0,
            warmth=0.0,
            memory_tint=None,
            decorative_tint_allowed=False,
            accessibility=accessibility,
        )

    base_frost = _clamp(source.get("baseFrost", 0.34), 0.20, 0.72)
    sensitivity = _clamp(source.get("sensitivityFactor", 0.38), 0.0, 0.55)
    variance = _clamp(_complexity_variance(complexity) + _luminance_variance(luminance))
    frost_strength = _clamp(base_frost + variance * sensitivity, 0.20, 0.88)
    if accessibility.increased_contrast:
        frost_strength = _clamp(frost_strength + 0.10, 0.20, 0.92)

    semantic_importance = _clamp(source.get("semanticImportance", 0.65))
    semantic_protection = _clamp(
        0.50 + semantic_importance * 0.46 + (0.04 if accessibility.increased_contrast else 0.0),
        0.50,
        1.0,
    )
    blur_scale = _clamp(1.0 - semantic_protection * 0.42, 0.50, 0.80)
    memory_tint = None if accessibility.increased_contrast else _normalize_memory_tint(
        source.get("memoryTint")
    )
    warmth = 0.0 if accessibility.increased_contrast else _warmth_for_daypart(daypart)

    return OpticalState(
        mode="adaptive-optical",
        appearance=appearance,
        background_complexity=complexity,
        background_luminance=luminance,
        depth=depth,
        daypart=daypart,
        frost_strength=frost_strength,
        blur_scale=blur_scale,
        semantic_protection=semantic_protection,
        depth_hue_shift=_depth_hue_shift(depth),
        warmth=warmth,
        memory_tint=memory_tint,
        decorative_tint_allowed=not accessibility.increased_contrast,
        accessibility=accessibility,
    )


def _normalize_performance_level(value: Any, fallback: str = "full") -> str:
    if isinstance(value, str) and value in PERFORMANCE_LEVELS:
        return value
    return fallback


def accept_performance_level(
    requested: str,
    *,
    current: str = "full",
) -> tuple[str, str | None]:
    """Apply V1.4.1 downgrade-only in-session optical performance governance."""
    current_level = _normalize_performance_level(current)
    requested_level = _normalize_performance_level(requested, current_level)
    current_rank = PERFORMANCE_LEVELS.index(current_level)
    requested_rank = PERFORMANCE_LEVELS.index(requested_level)
    if requested_rank < current_rank:
        return current_level, "upgrade-blocked-downgrade-only"
    if requested_rank > current_rank:
        return requested_level, "capability-or-performance-downgrade"
    return current_level, None


def _apply_performance_level(state: OpticalState, level: str) -> OpticalState:
    if state.mode == "solid-accessible" or level == "full":
        return state
    semantic_floor = {
        "balanced": 0.88,
        "efficient": 0.94,
        "durable": 1.0,
    }[level]
    blur_cap = {
        "balanced": 0.58,
        "efficient": 0.30,
        "durable": 0.0,
    }[level]
    memory_tint = state.memory_tint if level == "balanced" else None
    decorative = state.decorative_tint_allowed and level == "balanced"
    frost_strength = max(state.frost_strength, 0.66 if level == "balanced" else 0.82)
    if level == "durable":
        return OpticalState(
            mode="solid-accessible",
            appearance=state.appearance,
            background_complexity=state.background_complexity,
            background_luminance=state.background_luminance,
            depth=state.depth,
            daypart=state.daypart,
            frost_strength=1.0,
            blur_scale=0.0,
            semantic_protection=1.0,
            depth_hue_shift=0.0,
            warmth=0.0,
            memory_tint=None,
            decorative_tint_allowed=False,
            accessibility=state.accessibility,
        )
    return OpticalState(
        mode=state.mode,
        appearance=state.appearance,
        background_complexity=state.background_complexity,
        background_luminance=state.background_luminance,
        depth=state.depth,
        daypart=state.daypart,
        frost_strength=_clamp(frost_strength, 0.20, 0.92),
        blur_scale=min(state.blur_scale, blur_cap),
        semantic_protection=max(state.semantic_protection, semantic_floor),
        depth_hue_shift=state.depth_hue_shift if level == "balanced" else 0.0,
        warmth=state.warmth if level == "balanced" else 0.0,
        memory_tint=memory_tint,
        decorative_tint_allowed=decorative,
        accessibility=state.accessibility,
    )


def resolve_glaze_optics_v141(
    *,
    signal_adapter: SignalAdapter | None = None,
    overrides: Mapping[str, Any] | None = None,
    on_adapter_error: Callable[[Exception], None] | None = None,
    requested_performance_level: str = "full",
    current_performance_level: str = "full",
) -> OpticalResolution:
    """Resolve V1.4.1 with fail-safe adapter handling and bounded performance.

    Raw adapter errors never appear in the returned resolution. Optional local
    diagnostics may observe the exception, but observer failures are swallowed.
    """
    override_map = dict(overrides) if isinstance(overrides, Mapping) else {}
    adapter_status = "not-configured"
    source: dict[str, Any] = {}

    if signal_adapter is not None:
        try:
            resolved = signal_adapter.resolve()
            if isinstance(resolved, Mapping):
                source.update(resolved)
                adapter_status = "resolved"
            else:
                adapter_status = "resolved-bounded"
        except Exception as exc:  # fail closed at the consumer adapter boundary
            if on_adapter_error is not None:
                try:
                    on_adapter_error(exc)
                except Exception:
                    pass
            source.update(override_map)
            accessibility = source.get("accessibility")
            accessibility_map = (
                dict(accessibility) if isinstance(accessibility, Mapping) else {}
            )
            accessibility_map["forcedColors"] = True
            accessibility_map["reducedTransparency"] = True
            source["accessibility"] = accessibility_map
            state = resolve_glaze_optics(source)
            accepted_level, downgrade_reason = accept_performance_level(
                requested_performance_level,
                current=current_performance_level,
            )
            return OpticalResolution(
                state=state,
                adapter_status="failed-safe",
                requested_performance_level=_normalize_performance_level(
                    requested_performance_level,
                    current_performance_level,
                ),
                accepted_performance_level=accepted_level,
                downgrade_reason=downgrade_reason or "adapter-failure-solid-accessible",
            )

    source.update(override_map)
    state = resolve_glaze_optics(source)
    accepted_level, downgrade_reason = accept_performance_level(
        requested_performance_level,
        current=current_performance_level,
    )
    state = _apply_performance_level(state, accepted_level)
    return OpticalResolution(
        state=state,
        adapter_status=adapter_status,
        requested_performance_level=_normalize_performance_level(
            requested_performance_level,
            current_performance_level,
        ),
        accepted_performance_level=accepted_level,
        downgrade_reason=downgrade_reason,
    )


def care_default_optical_state(
    *,
    appearance: str,
    reduced_transparency: bool,
    reduced_motion: bool,
    increased_contrast: bool = False,
    forced_colors: bool = False,
    depth: str = "base",
    semantic_importance: float = 0.80,
    performance_level: str = "full",
) -> OpticalState:
    """Resolve Care's privacy-safe default V1.4.1 state from local UI state."""
    resolution = resolve_glaze_optics_v141(
        overrides={
            "appearance": appearance,
            "backgroundComplexity": "unknown",
            "backgroundLuminance": "dark" if appearance in {"dark", "deep-dark"} else "bright",
            "depth": depth,
            "daypart": "unknown",
            "semanticImportance": semantic_importance,
            "accessibility": {
                "forcedColors": forced_colors,
                "reducedTransparency": reduced_transparency,
                "increasedContrast": increased_contrast,
                "reducedMotion": reduced_motion,
            },
        },
        requested_performance_level=performance_level,
        current_performance_level="full",
    )
    return resolution.state


def optical_css_classes(state: OpticalState) -> tuple[str, ...]:
    """Map numeric optical state to bounded native GTK semantic classes."""
    classes = [f"optical-{state.mode}"]
    if state.mode == "solid-accessible":
        return tuple(classes)
    if state.frost_strength < 0.45:
        classes.append("optical-frost-soft")
    elif state.frost_strength < 0.65:
        classes.append("optical-frost-balanced")
    else:
        classes.append("optical-frost-strong")
    if state.semantic_protection >= 0.80:
        classes.append("optical-semantic-protected")
    classes.append(f"optical-depth-{state.depth}")
    if not state.decorative_tint_allowed:
        classes.append("optical-no-decorative-tint")
    return tuple(classes)


GLAZE_OPTICAL_ENGINE_V14_1 = {
    "version": "1.4.1",
    "stable_baseline": "1.4.0",
    "lifecycle": "stable-adoption-target",
    "telemetry_required": False,
    "remote_context_required": False,
    "preserves_token_system": True,
    "additive_component_api": True,
    "max_memory_tint_influence": MAX_MEMORY_TINT_INFLUENCE,
    "performance_levels": PERFORMANCE_LEVELS,
    "performance_governance": "downgrade-only-in-session",
    "adapter_failure_mode": "solid-accessible",
    "adapter_failure_status": "failed-safe",
    "accessibility_precedence": (
        "forced-colors",
        "reduced-transparency",
        "increased-contrast",
    ),
}

GLAZE_OPTICAL_ENGINE_V14 = GLAZE_OPTICAL_ENGINE_V14_1
