from app.services.page_split import present_full, present_summary, present_ticket


def test_summary_matches_ticket_fill_and_status_counts():
    payload = {
        "id": 9,
        "lines": [
            {"lane_id": 1, "gap": 7, "fill_qty": 4, "status": "need_fill"},
            {"lane_id": 2, "gap": 0, "fill_qty": 0, "status": "full"},
        ],
        "overbooked_count": 0,
    }
    s = present_summary(1, payload)
    assert s["total_fill"] == 4  # 与票面合计同一套数：各行补量之和
    assert s["need_fill_count"] == 1
    assert s["full_count"] == 1
    assert s["overbooked_count"] == 0


def test_full_list_only_status_full_lines():
    payload = {
        "lines": [
            {"lane_id": 1, "fill_qty": 0, "status": "full"},
            {"lane_id": 2, "fill_qty": 3, "status": "need_fill"},
            {"lane_id": 3, "fill_qty": 0, "status": "overbooked"},
        ]
    }
    body = present_full(1, payload)
    ids = {l["lane_id"] for l in body["lanes"]}
    assert ids == {1}  # 只收满仓行；超占/待补即使补量为 0 也不进满仓页


def test_ticket_keeps_row_fill_qty():
    payload = {"lines": [{"lane_id": 1, "fill_qty": 4, "gap": 9}]}
    t = present_ticket(payload)
    assert t["total_fill"] == 4
