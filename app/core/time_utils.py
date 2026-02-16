# app/core/time_utils.py
from __future__ import annotations

from typing import Iterable, Any
from datetime import time


def overlaps_time_ranges(start_a: time, end_a: time, start_b: time, end_b: time) -> bool:
    """
    True si dos rangos [start, end) se traslapan.
    Nota: end es exclusivo. Ej: (10:00-14:00) NO traslapa con (14:00-18:00)
    """
    return start_a < end_b and start_b < end_a


def merge_availability_windows(rules: Iterable[Any]) -> list[dict]:
    """
    Recibe rules (mismo barber + día) y devuelve ventanas fusionadas.
    Fusiona si se traslapan O si se pegan, PERO solo si slot_minutes coincide.

    Retorna lista de dicts: {start_time, end_time, slot_minutes}
    """
    rules_sorted = sorted(rules, key=lambda r: (r.start_time, r.end_time))

    merged: list[dict] = []
    for r in rules_sorted:
        cur = {
            "start_time": r.start_time,
            "end_time": r.end_time,
            "slot_minutes": r.slot_minutes,
        }

        if not merged:
            merged.append(cur)
            continue

        last = merged[-1]

        same_step = last["slot_minutes"] == cur["slot_minutes"]
        overlaps_or_touches = cur["start_time"] <= last["end_time"]  # incluye pegado

        if same_step and overlaps_or_touches:
            if cur["end_time"] > last["end_time"]:
                last["end_time"] = cur["end_time"]
        else:
            merged.append(cur)

    return merged
