# Copyright (C) 2019 Brian McMaster
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    sale_id = fields.Many2one("sale.order", help="Sale Id. Linked record reference.")
    sale_line_id = fields.Many2one("sale.order.line", help="Sale Line Id. Linked record reference.")

    def action_view_sales(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "views": [[False, "form"]],
            "res_id": self.sale_line_id.order_id.id or self.sale_id.id,
            "context": {"create": False},
            "name": _("Sales Orders"),
        }
