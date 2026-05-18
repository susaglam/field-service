# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for fsm.recurring."""

from odoo import models
from odoo.addons.cs_mcp_bridge.tools import ai_tool


class FsmRecurringMcp(models.Model):
    _inherit = "fsm.recurring"

    @ai_tool(
        name="fsm_recurring.search",
        description=(
            "Search recurring FSM orders by name, location, state, or "
            "team. Returns id, name, state, location, frequency set, "
            "start/end dates."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "name_contains": {"type": "string"},
                "location_id": {"type": "integer"},
                "state": {
                    "type": "string",
                    "enum": ["draft", "progress", "suspend", "close"],
                },
                "team_id": {"type": "integer"},
                "limit": {"type": "integer", "default": 30},
            },
        },
        risk="low",
    )
    def action_mcp_search(
        self,
        name_contains=None,
        location_id=None,
        state=None,
        team_id=None,
        limit=30,
    ):
        domain = []
        if name_contains:
            domain.append(("name", "ilike", name_contains))
        if location_id:
            domain.append(("location_id", "=", location_id))
        if state:
            domain.append(("state", "=", state))
        if team_id:
            domain.append(("team_id", "=", team_id))
        records = self.search(domain, limit=limit)
        return {
            "count": len(records),
            "recurring_orders": [
                {
                    "id": r.id,
                    "name": r.name,
                    "state": r.state,
                    "location": r.location_id.display_name,
                    "frequency_set": r.fsm_frequency_set_id.name
                    if r.fsm_frequency_set_id
                    else None,
                    "start_date": r.start_date.isoformat()
                    if r.start_date
                    else None,
                    "end_date": r.end_date.isoformat() if r.end_date else None,
                    "order_count": r.fsm_order_count,
                }
                for r in records
            ],
        }

    @ai_tool(
        name="fsm_recurring.suspend",
        description=(
            "Suspend a recurring FSM order — no new orders will be "
            "generated until resumed."
        ),
        input_schema={
            "type": "object",
            "properties": {"recurring_id": {"type": "integer"}},
            "required": ["recurring_id"],
        },
        risk="medium",
    )
    def action_mcp_suspend(self, recurring_id):
        rec = self.browse(recurring_id).exists()
        if not rec:
            return {"error": f"Recurring {recurring_id} not found"}
        rec.write({"state": "suspend"})
        return {"id": rec.id, "name": rec.name, "state": rec.state}

    @ai_tool(
        name="fsm_recurring.resume",
        description=(
            "Resume a previously-suspended recurring FSM order. New "
            "orders will start being generated again according to its "
            "frequency rules."
        ),
        input_schema={
            "type": "object",
            "properties": {"recurring_id": {"type": "integer"}},
            "required": ["recurring_id"],
        },
        risk="medium",
    )
    def action_mcp_resume(self, recurring_id):
        rec = self.browse(recurring_id).exists()
        if not rec:
            return {"error": f"Recurring {recurring_id} not found"}
        rec.write({"state": "progress"})
        return {"id": rec.id, "name": rec.name, "state": rec.state}
