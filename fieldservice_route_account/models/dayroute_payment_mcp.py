# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for fsm.route.dayroute.payment."""

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


class DayroutePaymentMcp(models.Model):
    _inherit = "fsm.route.dayroute.payment"

    @ai_tool(
        name="route_account.payment_summary",
        description=(
            "Get cash reconciliation summary for a day-route: per-journal "
            "rows with collected vs counted vs difference."
        ),
        input_schema={
            "type": "object",
            "properties": {"dayroute_id": {"type": "integer"}},
            "required": ["dayroute_id"],
        },
        risk="low",
    )
    def action_mcp_summary(self, dayroute_id):
        rows = self.search([("dayroute_id", "=", dayroute_id)])
        return {
            "dayroute_id": dayroute_id,
            "rows": [
                {
                    "journal": r.journal_id.name,
                    "collected": r.amount_collected,
                    "counted": r.amount_counted,
                    "difference": r.difference,
                    "move_posted": bool(r.move_id),
                }
                for r in rows
            ],
        }

    @ai_tool(
        name="route_account.set_counted",
        description=(
            "Set the physically-counted cash amount on a day-route "
            "payment row. The difference vs collected is auto-computed."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "payment_id": {"type": "integer"},
                "amount_counted": {"type": "number"},
            },
            "required": ["payment_id", "amount_counted"],
        },
        risk="medium",
    )
    def action_mcp_set_counted(self, payment_id, amount_counted):
        row = self.browse(payment_id).exists()
        if not row:
            return {"error": f"Payment row {payment_id} not found"}
        row.write({"amount_counted": amount_counted})
        return {
            "id": row.id,
            "journal": row.journal_id.name,
            "collected": row.amount_collected,
            "counted": row.amount_counted,
            "difference": row.difference,
        }
