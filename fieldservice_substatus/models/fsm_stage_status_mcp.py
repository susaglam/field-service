# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for fsm.stage.status (sub-statuses)."""

from odoo import models
from odoo.addons.cs_mcp_bridge.tools import ai_tool


class FsmStageStatusMcp(models.Model):
    _inherit = "fsm.stage.status"

    @ai_tool(
        name="fsm_substatus.list_all",
        description="List all available FSM order sub-statuses.",
        input_schema={"type": "object", "properties": {}},
        risk="low",
    )
    def action_mcp_list(self):
        rows = self.search([])
        return {
            "count": len(rows),
            "substatuses": [{"id": r.id, "name": r.name} for r in rows],
        }


class FsmOrderSubstatusMcp(models.Model):
    _inherit = "fsm.order"

    @ai_tool(
        name="fsm_substatus.set_on_order",
        description=(
            "Set the sub-status of an FSM order. Sub-statuses give "
            "fine-grained progress info within a stage (e.g. 'Awaiting "
            "parts', 'Customer not home')."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "order_id": {"type": "integer"},
                "sub_status_id": {"type": "integer"},
            },
            "required": ["order_id", "sub_status_id"],
        },
        risk="medium",
    )
    def action_mcp_set_substatus(self, order_id, sub_status_id):
        order = self.browse(order_id).exists()
        if not order:
            return {"error": f"Order {order_id} not found"}
        order.write({"sub_stage_id": sub_status_id})
        return {
            "id": order.id,
            "name": order.name,
            "stage": order.stage_id.name,
            "sub_status": order.sub_stage_id.name if order.sub_stage_id else None,
        }
