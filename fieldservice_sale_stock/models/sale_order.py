# Copyright (C) 2019 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def prepare_fsm_values_for_stock_move(self, fsm_order):
        return {
            "fsm_order_id": fsm_order.id,
        }

    def prepare_fsm_values_for_stock_picking(self, fsm_order):
        return {
            "fsm_order_id": fsm_order.id,
        }

    def _link_pickings_to_fsm(self):
        # Elevated: this runs inside EVERY sale confirmation, and it is the
        # system tying its own records together, not the salesperson acting
        # on field service. Run as the user it searched fsm.order with the
        # salesperson's rights, and a seller with no field-service access -
        # which is what a salesperson is once the blanket read for every
        # internal user is gone - could not confirm a quotation at all:
        # AccessError on 'Field Service Order', for a sale with no visit in it.
        for rec in self.sudo():
            # TODO: We may want to split the picking to have one picking
            # per FSM order
            # rec.env, not self.env: only the loop variable carries the sudo.
            fsm_order = rec.env["fsm.order"].search(
                [
                    ("sale_id", "=", rec.id),
                    ("sale_line_id", "=", False),
                ]
            )
            # procurement.group removed in saas-19.3; its place is taken by
            # stock.reference, so the order joins the sale's references.
            if fsm_order and rec.stock_reference_ids:
                fsm_order.reference_ids |= rec.stock_reference_ids
            for picking in rec.picking_ids:
                picking.write(rec.prepare_fsm_values_for_stock_picking(fsm_order))
                for move in picking.move_ids:
                    move.write(rec.prepare_fsm_values_for_stock_move(fsm_order))

    def _action_confirm(self):
        """On SO confirmation, link the fsm order on the pickings
        created by the sale order"""
        res = super()._action_confirm()
        self._link_pickings_to_fsm()
        return res
