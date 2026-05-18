# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    auto_populate_persons_on_location = fields.Boolean(
        string="Auto-populate Workers on Location based on Territory",
        help="Auto Populate Persons On Location. Automation toggle — when on, the related action happens automatically.",
    )
    auto_populate_equipments_on_order = fields.Boolean(
        string="Auto-populate Equipments on Order based on Location",
        help="Auto Populate Equipments On Order. Automation toggle — when on, the related action happens automatically.",
    )
    search_on_complete_name = fields.Boolean(string="Search Location By Hierarchy", help="Search On Complete Name.")

    fsm_order_request_late_lowest = fields.Float(
        string="Hours of Buffer for Lowest Priority FS Orders",
        default=72,
        help="Fsm Order Request Late Lowest.",
    )
    fsm_order_request_late_low = fields.Float(
        string="Hours of Buffer for Low Priority FS Orders",
        default=48,
        help="Fsm Order Request Late Low.",
    )
    fsm_order_request_late_medium = fields.Float(
        string="Hours of Buffer for Medium Priority FS Orders",
        default=24,
        help="Fsm Order Request Late Medium.",
    )
    fsm_order_request_late_high = fields.Float(
        string="Hours of Buffer for High Priority FS Orders", default=8,
        help="Fsm Order Request Late High.",
    )
