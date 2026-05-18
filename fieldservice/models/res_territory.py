# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResTerritory(models.Model):
    _inherit = "res.territory"

    person_ids = fields.Many2many("fsm.person", string="Field Service Workers", help="Person Ids. Many-to-many / one-to-many relation collection.")
    person_id = fields.Many2one("fsm.person", string="Primary Assignment", help="Person Id. Linked record reference.")
