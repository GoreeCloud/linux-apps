from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PrivilegedOutcome:
    completed: bool
    cancelled: bool
    message: str


_CANCELLED_STDERR_MARKERS = (
    "request dismissed",
    "authentication cancelled",
    "authentication canceled",
    "authorization cancelled",
    "authorization canceled",
    "cancelled by user",
    "canceled by user",
)


def interpret_pkexec_result(returncode: int, stderr: str, action_label: str) -> PrivilegedOutcome:
    """Translate pkexec/helper completion into explicit user-facing state.

    pkexec commonly uses exit code 126 when authorization is dismissed, but
    PolicyKit agents/distributions can also surface dismissal through stderr.
    Treat an observed dismissal message as cancellation regardless of the exact
    non-zero code so cancellation is never misreported as an opaque failure.
    """
    if returncode == 0:
        return PrivilegedOutcome(
            completed=True,
            cancelled=False,
            message=f"{action_label} completed successfully.",
        )

    detail = (stderr or "").strip()
    detail_lower = detail.lower()
    dismissed = returncode == 126 or any(marker in detail_lower for marker in _CANCELLED_STDERR_MARKERS)

    if dismissed:
        return PrivilegedOutcome(
            completed=False,
            cancelled=True,
            message=(
                f"{action_label} was cancelled. The privileged maintenance command "
                "was not run, so GoreeCloud Care made no privileged changes."
            ),
        )

    if returncode == 127:
        message = (
            f"{action_label} did not run because administrator authorization was not obtained "
            "or PolicyKit reported an error. No successful privileged change is claimed."
        )
    else:
        message = (
            f"{action_label} did not complete (exit status {returncode}). "
            "No successful privileged change is claimed."
        )

    if detail:
        message = f"{message} Details: {detail}"

    return PrivilegedOutcome(completed=False, cancelled=False, message=message)
