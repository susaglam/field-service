# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for turning contacts into Field Service records.

Thin JSON wrappers around res.partner.action_fsm_convert_to_location and
action_fsm_convert_to_person (the "Convert to FS ..." buttons on the contact
form). They answer with the created record instead of raising when the
contact is already converted, so an agent can call them idempotently.
"""

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


class ResPartnerMcp(models.Model):
    _inherit = "res.partner"

    def _mcp_fsm_location_dict(self, location):
        return {
            "location_id": location.id,
            "location": location.display_name,
            "owner": location.owner_id.display_name,
            "parent_location": location.parent_id.display_name or None,
        }

    @ai_tool(
        name="fieldservice.partner_convert_to_location",
        description=(
            "Make an existing contact a Field Service location, so work "
            "orders can be planned at its address. Example: before planning "
            "a visit to the customer 'Jansen B.V.', convert that contact. A "
            "child contact is owned by its parent company and placed under "
            "the company's location. Returns the location; calling it again "
            "returns the existing one."
        ),
        input_schema={
            "type": "object",
            "properties": {"partner_id": {"type": "integer"}},
            "required": ["partner_id"],
        },
        risk="medium",
        examples=[
            {
                "goal": "Make a customer's site plannable for field service",
                "steps": [
                    {
                        "tool": "fieldservice.partner_convert_to_location",
                        "args": {"partner_id": 57},
                    }
                ],
            }
        ],
    )
    def action_mcp_convert_to_location(self, partner_id):
        partner = self.browse(partner_id).exists()
        if not partner:
            return {"error": f"Contact {partner_id} not found"}
        existing = partner.fsm_location_ids[:1]
        if existing:
            return {"created": False, **self._mcp_fsm_location_dict(existing)}
        partner.action_fsm_convert_to_location()
        location = partner.fsm_location_ids[:1]
        return {"created": True, **self._mcp_fsm_location_dict(location)}

    @ai_tool(
        name="fieldservice.partner_convert_to_worker",
        description=(
            "Make an existing contact a Field Service worker, so work orders "
            "can be assigned to them. Example: a new subcontractor 'P. de "
            "Vries' was added as a contact and should receive installation "
            "jobs. Returns the worker; calling it again returns the existing "
            "one."
        ),
        input_schema={
            "type": "object",
            "properties": {"partner_id": {"type": "integer"}},
            "required": ["partner_id"],
        },
        risk="medium",
    )
    def action_mcp_convert_to_worker(self, partner_id):
        partner = self.browse(partner_id).exists()
        if not partner:
            return {"error": f"Contact {partner_id} not found"}
        Person = self.env["fsm.person"].with_context(active_test=False)
        worker = Person.search([("partner_id", "=", partner.id)], limit=1)
        created = not worker
        if created:
            partner.action_fsm_convert_to_person()
            worker = Person.search([("partner_id", "=", partner.id)], limit=1)
        return {
            "created": created,
            "worker_id": worker.id,
            "worker": worker.display_name,
            "active": worker.active,
        }
