"""Bounded GLAZE UI V1.5 presentation resolution for GoreeCloud Care.

V1.5.0 retains Care's existing V1.4.1 optical implementation and adds a
presentation-only context/capability layer. This module never grants authority,
requests permission, executes maintenance, or invents capability truth. Inputs
must come from the application or another authoritative provider. Conflicting
provider facts fail closed to an unknown presentation state.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .glaze_v14 import layout_environment

GLAZE_UI_LABEL = "GLAZE UI V1.5 — Contextual + Capability Awareness"
GLAZE_UI_TARGET_VERSION = "1.5.0"
GLAZE_UI_STABLE_BASELINE = "1.4.1"
GLAZE_UI_ADOPTION_STATE = "development"
GLAZE_UI_CONSUMER_ELIGIBLE = False
GLAZE_UI_SOURCE_REVISION = "b7fa8164bfdeaa1dc0acb21b770e7601120da04e"
GLAZE_UI_REVIEWED_IMPLEMENTATION_ANCHOR = "ee1032a0822ab8e103f8afe48e5c1859fde65cc9"

CAPABILITY_STATES = {"available", "degraded", "unavailable", "unknown"}
RUNTIME_PRESSURE_STATES = {"normal", "reduced", "critical"}
CONNECTIVITY_STATES = {"online", "offline", "unknown"}


@dataclass(frozen=True)
class CapabilityFact:
    domain: str
    provider: str
    state: str
    reason: str
    provenance: str

    def normalized(self) -> "CapabilityFact":
        state = self.state if self.state in CAPABILITY_STATES else "unknown"
        return CapabilityFact(
            domain=self.domain.strip() or "unknown",
            provider=self.provider.strip() or "unknown",
            state=state,
            reason=self.reason.strip() or "Capability state is not established.",
            provenance=self.provenance.strip() or "unverified",
        )


@dataclass(frozen=True)
class PresentationContext:
    runtime_pressure: str = "normal"
    connectivity: str = "unknown"
    reduced_motion: bool = False
    reduced_transparency: bool = False
    increased_contrast: bool = False


@dataclass(frozen=True)
class CapabilityPresentation:
    state: str
    enabled: bool
    explanation: str
    provenance: str
    css_classes: tuple[str, ...]
    automatic_fallback_allowed: bool = False
    automatic_execution_allowed: bool = False


def _rank(state: str) -> int:
    return {"unknown": 0, "unavailable": 1, "degraded": 2, "available": 3}.get(state, 0)


def resolve_capability_facts(facts: Iterable[CapabilityFact]) -> CapabilityFact:
    """Resolve one capability domain without manufacturing provider precedence.

    Multiple providers may agree. If they disagree on state, presentation fails
    closed to ``unknown`` rather than choosing an inferred winner.
    """
    normalized = tuple(fact.normalized() for fact in facts)
    if not normalized:
        return CapabilityFact(
            domain="unknown",
            provider="none",
            state="unknown",
            reason="Capability state is not established.",
            provenance="unverified",
        )

    domains = {fact.domain for fact in normalized}
    states = {fact.state for fact in normalized}
    if len(domains) != 1 or len(states) != 1:
        return CapabilityFact(
            domain=next(iter(domains)) if len(domains) == 1 else "conflict",
            provider="conflict",
            state="unknown",
            reason="Authoritative capability facts conflict; presentation failed closed.",
            provenance="conflict",
        )

    # Providers agree on state. Keep the most restrictive fact's explanation
    # deterministically without turning provider order into authority precedence.
    chosen = sorted(
        normalized,
        key=lambda fact: (_rank(fact.state), fact.provider, fact.provenance, fact.reason),
    )[0]
    providers = ",".join(sorted({fact.provider for fact in normalized}))
    provenance = ",".join(sorted({fact.provenance for fact in normalized}))
    return CapabilityFact(
        domain=chosen.domain,
        provider=providers,
        state=chosen.state,
        reason=chosen.reason,
        provenance=provenance,
    )


def resolve_presentation(
    fact: CapabilityFact,
    context: PresentationContext = PresentationContext(),
) -> CapabilityPresentation:
    """Map authoritative capability truth to presentation only."""
    normalized = fact.normalized()
    pressure = context.runtime_pressure if context.runtime_pressure in RUNTIME_PRESSURE_STATES else "critical"
    connectivity = context.connectivity if context.connectivity in CONNECTIVITY_STATES else "unknown"

    classes = [
        "glaze-v15",
        f"capability-{normalized.state}",
        f"runtime-pressure-{pressure}",
        f"connectivity-{connectivity}",
    ]
    if context.reduced_motion:
        classes.append("accessibility-reduced-motion")
    if context.reduced_transparency:
        classes.append("accessibility-reduced-transparency")
    if context.increased_contrast:
        classes.append("accessibility-increased-contrast")
    if context.reduced_motion or context.reduced_transparency or context.increased_contrast:
        classes.append("accessibility-priority")

    enabled = normalized.state in {"available", "degraded"}
    explanation = normalized.reason
    if normalized.state == "available":
        explanation = normalized.reason or "Capability is available."
    elif normalized.state == "degraded":
        explanation = f"Limited capability: {normalized.reason}"
    elif normalized.state == "unavailable":
        explanation = f"Unavailable: {normalized.reason}"
    else:
        explanation = f"Availability unknown: {normalized.reason}"

    return CapabilityPresentation(
        state=normalized.state,
        enabled=enabled,
        explanation=explanation,
        provenance=normalized.provenance,
        css_classes=tuple(classes),
        automatic_fallback_allowed=False,
        automatic_execution_allowed=False,
    )


def privileged_maintenance_capability(
    *,
    helper_executable: bool,
    pkexec_available: bool,
) -> CapabilityFact:
    """Describe execution-path availability without granting authorization."""
    if not helper_executable:
        return CapabilityFact(
            domain="privileged-maintenance",
            provider="goreecloud-care",
            state="unavailable",
            reason="The GoreeCloud Care privileged helper is not installed or executable.",
            provenance="local-helper-check",
        )
    if not pkexec_available:
        return CapabilityFact(
            domain="privileged-maintenance",
            provider="goreecloud-care",
            state="unavailable",
            reason="PolicyKit pkexec is not available on this system.",
            provenance="local-pkexec-check",
        )
    return CapabilityFact(
        domain="privileged-maintenance",
        provider="goreecloud-care",
        state="available",
        reason="Privileged maintenance can request administrator authorization when you choose an action.",
        provenance="local-helper-and-pkexec-check",
    )
