# Copyright (C) 2018 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    fsm_order_id = fields.Many2one(
        "fsm.order",
        string="Field Service Order",
        help="Field service order this stock move belongs to; the move is listed "
        "on that order's Operations tab. Filled from the transfer when empty.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        moves._fsm_link_to_picking_order()
        return moves

    def write(self, vals):
        res = super().write(vals)
        if "picking_id" in vals:
            self._fsm_link_to_picking_order()
        return res

    def _fsm_link_to_picking_order(self):
        """Give a move without an order the order of its transfer.

        The order's Operations tab lists moves by ``fsm_order_id``. A line added
        to a transfer that belongs to an order (by hand, or by a rule that does
        not carry the order) had none and never showed there. A move already
        linked keeps its own order: one transfer can carry moves of several
        per-line orders.
        """
        for move in self.filtered(
            lambda m: not m.fsm_order_id and m.picking_id.fsm_order_id
        ):
            move.fsm_order_id = move.picking_id.fsm_order_id
