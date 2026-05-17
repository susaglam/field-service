# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def get_default_leaflet_position(self, model_name):
        result = super().get_default_leaflet_position(model_name)
        if model_name != "fsm.location":
            return result
        company = self.env.user.company_id
        if company.fsm_map_default_latitude and company.fsm_map_default_longitude:
            result["lat"] = company.fsm_map_default_latitude
            result["lng"] = company.fsm_map_default_longitude
        result["default_zoom"] = company.fsm_map_default_zoom or 7
        result["fit_bounds"] = bool(company.fsm_map_fit_bounds)
        result["default_layer"] = company.fsm_map_default_layer or "OpenStreetMap"
        return result
