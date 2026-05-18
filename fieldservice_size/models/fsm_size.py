# Copyright (C) 2020 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FSMSize(models.Model):
    _name = "fsm.size"
    _description = "Field Service Size"

    name = fields.Char(required=True)
    type_id = fields.Many2one("fsm.order.type", string="Order Type", help="Type Id. Linked record reference.")
    parent_id = fields.Many2one("fsm.size", string="Parent Size", index=True, help="Parent Id. Linked record reference.")
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure", help="Uom Id. Linked record reference.")
    is_order_size = fields.Boolean(
        string="Is the Order Size?", help="The default size for orders of this type"
    )

    _name_uniq = models.Constraint(
        'unique (name)',
        'Size name already exists!',
    )

    @api.constrains("is_order_size", "type_id")
    def _one_size_per_type(self):
        size_count = self.search_count(
            [("type_id", "=", self.type_id.id), ("is_order_size", "=", True)]
        )
        if size_count >= 2:
            raise ValidationError(_("Only one default order size per type is allowed."))
