# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FSMLocation(models.Model):
    _inherit = "fsm.location"

    description = fields.Text(
        string="Description",
        help="Free-text description of this Field Service location. Shown "
        "as an italic block in the Leaflet map popup so dispatchers see "
        "site-specific notes (access codes, parking, contact tips) at a "
        "glance without opening the form.",
    )

    def _auto_geocode_if_enabled(self):
        for rec in self:
            company = rec.company_id or self.env.company
            if not company.fsm_map_auto_geocode:
                continue
            partner = rec.partner_id
            if not partner or partner.partner_latitude or partner.partner_longitude:
                continue
            if not (partner.street or partner.city or partner.zip):
                continue
            try:
                partner.geo_localize()
            except Exception:
                # Nominatim rate-limit / network glitch — don't break the
                # create/write transaction over a best-effort geocode.
                pass

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._auto_geocode_if_enabled()
        return records

    def write(self, vals):
        res = super().write(vals)
        if any(k in vals for k in ("street", "city", "zip", "country_id", "state_id")):
            self._auto_geocode_if_enabled()
        return res
