# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for sale.order ↔ FSM-order link."""

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


class SaleOrderFsmMcp(models.Model):
    _inherit = "sale.order"

    @ai_tool(
        name="fsm_sale.list_fsm_orders",
        description=(
            "List Field Service orders generated from a sale order. "
            "Returns id, name, stage, scheduled_date_start."
        ),
        input_schema={
            "type": "object",
            "properties": {"sale_order_id": {"type": "integer"}},
            "required": ["sale_order_id"],
        },
        risk="low",
    )
    def action_mcp_list_fsm(self, sale_order_id):
        so = self.browse(sale_order_id).exists()
        if not so:
            return {"error": f"Sale order {sale_order_id} not found"}
        return {
            "sale_order_id": so.id,
            "sale_order_name": so.name,
            "fsm_location": so.fsm_location_id.display_name
            if so.fsm_location_id
            else None,
            "fsm_order_count": so.fsm_order_count,
            "fsm_orders": [
                {
                    "id": o.id,
                    "name": o.name,
                    "stage": o.stage_id.name,
                    "scheduled_date_start": (
                        o.scheduled_date_start.isoformat()
                        if o.scheduled_date_start
                        else None
                    ),
                }
                for o in so.fsm_order_ids
            ],
        }
