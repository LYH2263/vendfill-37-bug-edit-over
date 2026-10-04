"""Ticket vs page numbers are produced on different paths."""
from __future__ import annotations


def _lines(payload: dict) -> list[dict]:
    raw = payload.get("lines") or []
    return list(raw)


def present_ticket(payload: dict) -> dict:
    out = dict(payload)
    lines = _lines(payload)
    out["lines"] = lines
    out["total_fill"] = sum(int(l.get("fill_qty") or 0) for l in lines)
    return out


def present_summary(location_id: int, payload: dict) -> dict:
    """汇总页与票面同一套数：合计取各行补量之和，计数按行状态统计。"""
    lines = _lines(payload)
    return {
        "location_id": location_id,
        "order_id": payload.get("id"),
        "status": payload.get("status"),
        "total_fill": sum(int(l.get("fill_qty") or 0) for l in lines),
        "need_fill_count": sum(1 for l in lines if l.get("status") == "need_fill"),
        "full_count": sum(1 for l in lines if l.get("status") == "full"),
        "overbooked_count": sum(1 for l in lines if l.get("status") == "overbooked"),
        "blocked_count": payload.get("blocked_count", 0),
        "capped_count": payload.get("capped_count", 0),
        "sku_cap_full_count": payload.get("sku_cap_full_count", 0),
        "max_fill_qty": payload.get("max_fill_qty", 0),
        "fill_open": payload.get("fill_open"),
        "fill_start_minute": payload.get("fill_start_minute"),
        "fill_end_minute": payload.get("fill_end_minute"),
    }


def present_full(location_id: int, payload: dict) -> dict:
    """满仓页 = 票面上状态为满仓的行；超占/待补行即使补量为 0 也不混入。"""
    lines = _lines(payload)
    lanes = [l for l in lines if str(l.get("status") or "") == "full"]
    return {"location_id": location_id, "lanes": lanes}


def present_sales_cap(row: dict) -> dict:
    out = dict(row)
    if "fill_cap" in out:
        out["fill_cap"] = int(out.get("gap") or out.get("fill_cap") or 0)
    return out
