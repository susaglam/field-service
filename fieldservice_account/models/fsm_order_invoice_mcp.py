# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for the account ↔ FSM-order link."""

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


class FsmOrderInvoiceMcp(models.Model):
    _inherit = "fsm.order"

    @ai_tool(
        name="fsm_account.list_invoices",
        description=(
            "List customer invoices generated from an FSM order. Returns "
            "id, name, state, amount, partner."
        ),
        input_schema={
            "type": "object",
            "properties": {"order_id": {"type": "integer"}},
            "required": ["order_id"],
        },
        risk="low",
    )
    def action_mcp_list_invoices(self, order_id):
        order = self.browse(order_id).exists()
        if not order:
            return {"error": f"Order {order_id} not found"}
        return {
            "order_id": order_id,
            "order_name": order.name,
            "invoice_count": order.invoice_count,
            "invoices": [
                {
                    "id": inv.id,
                    "name": inv.name,
                    "state": inv.state,
                    "amount_total": inv.amount_total,
                    "partner": inv.partner_id.name if inv.partner_id else None,
                }
                for inv in order.invoice_ids
            ],
        }
