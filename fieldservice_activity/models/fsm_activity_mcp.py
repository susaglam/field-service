# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for fsm.activity (order checklist activities)."""

from odoo import models
try:
    from odoo.addons.cs_mcp_bridge.tools import ai_tool
except ImportError:
    # No-op fallback when cs_mcp_bridge is not installed.
    # AI/MCP surface unavailable; methods stay normal callable Python.
    def ai_tool(**_kwargs):
        def _decorator(fn):
            return fn
        return _decorator


class FsmActivityMcp(models.Model):
    _inherit = "fsm.activity"

    @ai_tool(
        name="fsm_activity.list_for_order",
        description=(
            "List the checklist activities attached to an FSM order, with "
            "their state (todo / done / cancel) and completion metadata."
        ),
        input_schema={
            "type": "object",
            "properties": {"order_id": {"type": "integer"}},
            "required": ["order_id"],
        },
        risk="low",
    )
    def action_mcp_list(self, order_id):
        rows = self.search([("fsm_order_id", "=", order_id)])
        return {
            "order_id": order_id,
            "activities": [
                {
                    "id": a.id,
                    "name": a.name,
                    "state": a.state,
                    "completed": a.completed,
                    "completed_by": a.completed_by.name if a.completed_by else None,
                    "completed_on": a.completed_on.isoformat()
                    if a.completed_on
                    else None,
                    "required": a.required,
                }
                for a in rows
            ],
        }

    @ai_tool(
        name="fsm_activity.complete",
        description=(
            "Mark a single checklist activity on an FSM order as completed."
        ),
        input_schema={
            "type": "object",
            "properties": {"activity_id": {"type": "integer"}},
            "required": ["activity_id"],
        },
        risk="medium",
    )
    def action_mcp_complete(self, activity_id):
        a = self.browse(activity_id).exists()
        if not a:
            return {"error": f"Activity {activity_id} not found"}
        a.write({"state": "done", "completed": True})
        return {"id": a.id, "name": a.name, "state": a.state}
