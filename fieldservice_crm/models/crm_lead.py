# Copyright (C) 2019, Patrick Wilson
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Lead(models.Model):
    _inherit = "crm.lead"

    fsm_order_ids = fields.One2many(
        "fsm.order",
        "opportunity_id",
        string="Service Orders",
        help="Fsm Order Ids. Many-to-many / one-to-many relation collection.",
    )
    fsm_location_id = fields.Many2one(
        "fsm.location",
        string="FSM Location",
        help="Fsm Location Id. Linked record reference.",
    )
    fsm_order_count = fields.Integer(
        compute="_compute_fsm_order_count", string="# FSM Orders"
    )

    def _compute_fsm_order_count(self):
        # Counted with sudo: a number gives nothing away, and a salesperson
        # without Field Service rights must still be able to open a lead.
        # This module used to solve that by giving every internal user read
        # access to ALL orders; since 19.4 permissions are OR'd, so that row
        # also showed a fitter with "own documents only" everyone's visits.
        counts = dict(
            self.env["fsm.order"]
            .sudo()
            ._read_group(
                [("opportunity_id", "in", self._origin.ids)],
                ["opportunity_id"],
                ["__count"],
            )
        )
        for rec in self:
            rec.fsm_order_count = counts.get(rec._origin, 0)
