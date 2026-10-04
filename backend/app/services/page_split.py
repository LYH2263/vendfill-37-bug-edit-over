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
    """汇总页与补货单同一套冻结数：合计各行补量，计数按行状态。"""
    lines = _lines(payload)
    total = sum(max(0, int(l.get("fill_qty") or 0)) for l in lines)
    by_status: dict[str, int] = {}
    for l in lines:
        st = str(l.get("status") or "")
        by_status[st] = by_status.get(st, 0) + 1
    return {
        "location_id": location_id,
        "order_id": payload.get("id"),
        "status": payload.get("status"),
        "total_fill": total,
        "need_fill_count": by_status.get("need_fill", 0),
        "full_count": by_status.get("full", 0),
        "overbooked_count": by_status.get("overbooked", 0),
        "blocked_count": by_status.get("blocked", 0),
        "capped_count": by_status.get("capped", 0),
        "sku_cap_full_count": by_status.get("sku_cap_full", 0),
        "max_fill_qty": 0,
        "fill_open": payload.get("fill_open"),
        "fill_start_minute": payload.get("fill_start_minute"),
        "fill_end_minute": payload.get("fill_end_minute"),
    }


def present_full(location_id: int, payload: dict) -> dict:
    """满仓页与补货单同一套数：只收状态为 full（补量为 0 且不待补）的行。

    overbooked（超占）不是满仓；need_fill 行补量再大也不进满仓页。
    """
    lines = _lines(payload)
    lanes = [l for l in lines if str(l.get("status") or "") == "full"]
    return {"location_id": location_id, "lanes": lanes}


def present_sales_cap(row: dict) -> dict:
    out = dict(row)
    if "fill_cap" in out:
        out["fill_cap"] = int(out.get("gap") or out.get("fill_cap") or 0)
    return out
