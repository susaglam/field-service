# Copyright (C) 2019 Brian McMaster
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    field_service_tracking = fields.Selection(
        # no help= here: it would replace fieldservice_sale's explanation of the
        # field with this module's text for every value, not only "recurring"
        selection_add=[("recurring", "Create a recurring order")],
    )
    fsm_recurring_template_id = fields.Many2one(
        "fsm.recurring.template",
        "Field Service Recurring Template",
        help="Select a field service recurring order template to be created",
    )

    @api.onchange("field_service_tracking")
    def _onchange_field_service_tracking(self):
        if self.field_service_tracking != "recurring":
            self.fsm_recurring_template_id = False
        # always: the parent clears the order template when tracking is "no",
        # which this override used to skip for every value but "recurring"
        return super()._onchange_field_service_tracking()
