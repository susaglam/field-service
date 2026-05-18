# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for repair.order ↔ FSM-order link."""

from odoo import models
from odoo.addons.cs_mcp_bridge.tools import ai_tool


class FsmOrderRepairMcp(models.Model):
    _inherit = "fsm.order"

    @ai_tool(
        name="fsm_repair.list_repairs",
        description=(
            "List MRP repair orders linked to an FSM order. Returns id, "
            "name, state, product, location."
        ),
        input_schema={
            "type": "object",
            "properties": {"order_id": {"type": "integer"}},
            "required": ["order_id"],
        },
        risk="low",
    )
    def action_mcp_list_repairs(self, order_id):
        order = self.browse(order_id).exists()
        if not order:
            return {"error": f"Order {order_id} not found"}
        return {
            "order_id": order.id,
            "order_name": order.name,
            "repair_count": order.repair_count,
            "repairs": [
                {
                    "id": r.id,
                    "name": r.name,
                    "state": r.state,
                    "product": r.product_id.display_name
                    if r.product_id
                    else None,
                    "location": r.location_id.display_name
                    if r.location_id
                    else None,
                }
                for r in order.repair_ids
            ],
        }
