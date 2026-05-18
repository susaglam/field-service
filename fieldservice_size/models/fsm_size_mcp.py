# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for fsm.size."""

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


class FsmSizeMcp(models.Model):
    _inherit = "fsm.size"

    @ai_tool(
        name="fsm_size.search",
        description=(
            "Search FSM sizes (order or location size definitions). "
            "Returns id, name, order_type, uom, parent."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "name_contains": {"type": "string"},
                "limit": {"type": "integer", "default": 30},
            },
        },
        risk="low",
    )
    def action_mcp_search(self, name_contains=None, limit=30):
        domain = []
        if name_contains:
            domain.append(("name", "ilike", name_contains))
        records = self.search(domain, limit=limit)
        return {
            "count": len(records),
            "sizes": [
                {
                    "id": s.id,
                    "name": s.name,
                    "order_type": s.type_id.name if s.type_id else None,
                    "uom": s.uom_id.name if s.uom_id else None,
                    "parent": s.parent_id.name if s.parent_id else None,
                    "is_order_size": s.is_order_size,
                }
                for s in records
            ],
        }
