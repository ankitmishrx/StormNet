"""Temporal Alignment and Synchronization Engine with Strict Causal Anti-Leakage Rules."""

from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional, TypeVar
from ml.preprocessing.fusion.interfaces import TemporalWindow, QualityFlag

T = TypeVar("T")


class TemporalLeakageError(ValueError):
    """Raised when an observation timestamp violates causal ordering rules."""
    pass


class TemporalAligner:
    """Synchronizes multi-source sensor observations into common discrete observation windows."""

    def __init__(self, default_window_seconds: int = 300, strict_causal: bool = True):
        self.window_duration_seconds = default_window_seconds
        self.strict_causal = strict_causal

    def create_window(
        self, anchor_timestamp: datetime, duration_seconds: Optional[int] = None
    ) -> TemporalWindow:
        """Constructs a backward-looking causal observation window [T - delta_t, T]."""
        duration = duration_seconds or self.window_duration_seconds
        window_start = anchor_timestamp - timedelta(seconds=duration)
        return TemporalWindow(
            window_start=window_start,
            window_end=anchor_timestamp,
            anchor_timestamp=anchor_timestamp,
            duration_seconds=duration,
        )

    def filter_and_align(
        self, observations: List[T], window: TemporalWindow
    ) -> List[T]:
        """Filters observations that strictly fall within [window_start, window_end].

        Enforces causal constraint: No observation where timestamp > window_end is permitted.
        """
        aligned: List[T] = []

        for obs in observations:
            ts: datetime = getattr(obs, "timestamp", None)
            if ts is None:
                continue

            # Ensure timezone awareness for safe comparison
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            anchor = (
                window.window_end
                if window.window_end.tzinfo is not None
                else window.window_end.replace(tzinfo=timezone.utc)
            )
            w_start = (
                window.window_start
                if window.window_start.tzinfo is not None
                else window.window_start.replace(tzinfo=timezone.utc)
            )

            # Causal assertion: Lookahead violation check
            if ts > anchor:
                if self.strict_causal:
                    raise TemporalLeakageError(
                        f"Temporal Leakage Violation: Observation timestamp {ts.isoformat()} "
                        f"exceeds anchor window limit {anchor.isoformat()}."
                    )
                else:
                    continue

            # Check if within window
            if w_start <= ts <= anchor:
                aligned.append(obs)

        return aligned

    def find_nearest_preceding(
        self, observations: List[T], anchor_timestamp: datetime, max_latency_seconds: int = 1800
    ) -> Optional[T]:
        """Finds the most recent observation strictly before or at anchor timestamp within latency SLA."""
        anchor = (
            anchor_timestamp
            if anchor_timestamp.tzinfo is not None
            else anchor_timestamp.replace(tzinfo=timezone.utc)
        )
        candidates: List[T] = []

        for obs in observations:
            ts: datetime = getattr(obs, "timestamp", None)
            if ts is None:
                continue
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)

            # Anti-leakage: must be <= anchor
            if ts <= anchor:
                latency = (anchor - ts).total_seconds()
                if latency <= max_latency_seconds:
                    candidates.append((obs, latency))

        if not candidates:
            return None

        # Return candidate with minimal latency (most recent preceding)
        candidates.sort(key=lambda x: x[1])
        return candidates[0][0]
