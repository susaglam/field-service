# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    @api.model
    def _default_warehouse_id(self):
        company = self.env.user.company_id
        warehouse_ids = self.env["stock.warehouse"].search(
            [("company_id", "=", company.id)], limit=1
        )
        return warehouse_ids and warehouse_ids.id

    @api.model
    def _get_move_domain(self):
        return [("picking_id.picking_type_id.code", "in", ("outgoing", "incoming"))]

    picking_ids = fields.One2many(
        "stock.picking",
        "fsm_order_id",
        string="Transfers",
        help="Delivery and return transfers linked to this order, e.g. the parts "
        "shipped to the site for the job.",
    )
    delivery_count = fields.Integer(
        string="Delivery Orders", compute="_compute_picking_ids"
    )
    # procurement_group_id removed: procurement.group model gone in saas-19.3.
    # stock.reference is what groups a sale's transfers on saas-19.4.
    reference_ids = fields.Many2many(
        "stock.reference",
        "stock_reference_fsm_order_rel",
        "fsm_order_id",
        "reference_id",
        string="Stock References",
        help="Stock references (the grouping of transfers that replaced "
        "procurement groups) this order is part of. Filled when the sale that "
        "created the order is confirmed, so the order and its sale share the "
        "same transfers. Example: sale S00042 -> reference S00042 -> the "
        "delivery of its tiles and the order installing them.",
    )
    inventory_location_id = fields.Many2one(
        related="location_id.inventory_location_id",
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        required=True,
        default=lambda self: self._default_warehouse_id(),
        help="Warehouse used to ship the materials",
    )
    return_count = fields.Integer(
        string="Return Orders", compute="_compute_picking_ids"
    )
    move_ids = fields.One2many(
        "stock.move",
        "fsm_order_id",
        string="Operations",
        domain=lambda self: self._get_move_domain(),
        help="Stock moves of this order's delivery and return transfers, shown on "
        "the Operations tab. A line added to a transfer of this order is listed "
        "here automatically.",
    )

    @api.depends("picking_ids")
    def _compute_picking_ids(self):
        for order in self:
            outgoing_pickings = order.picking_ids.filtered(
                lambda p: p.picking_type_id.code == "outgoing"
            )
            order.delivery_count = len(outgoing_pickings.ids)
            incoming_pickings = order.picking_ids.filtered(
                lambda p: p.picking_type_id.code == "incoming"
            )
            order.return_count = len(incoming_pickings.ids)

    def action_complete(self):
        # Validate BEFORE the stage moves, so a transfer that cannot be booked
        # leaves the order open instead of "Completed" with stock unbooked.
        self.filtered("company_id.fsm_auto_validate_pickings")._fsm_validate_pickings()
        return super().action_complete()

    def _fsm_validate_pickings(self):
        """Validate the open delivery/return transfers of these orders.

        Raises UserError naming the order, the transfer and the next step when
        a transfer lacks stock or saas-19.4 answers ``button_validate`` with a
        confirmation wizard (SMS, expiry dates, ...) instead of validating it.
        """
        for order in self:
            pickings = order.picking_ids.filtered(
                lambda p: p.state in ("confirmed", "waiting", "assigned")
            )
            for picking in pickings:
                try:
                    picking.action_assign()
                except AccessError as error:
                    raise UserError(
                        self.env._(
                            "Order %(order)s cannot be completed by you yet: "
                            "completing it also books transfer %(picking)s, and "
                            "that needs Inventory rights. Ask a warehouse user to "
                            "complete the order, or ask an administrator to give "
                            "you Inventory access.",
                            order=order.name,
                            picking=picking.name,
                        )
                    ) from error
                short = picking.move_ids.filtered(
                    lambda m: m.state != "cancel"
                    and m.uom_id.compare(m.quantity, m.product_uom_qty) < 0
                )
                if short:
                    move = short[0]
                    raise UserError(
                        self.env._(
                            "Order %(order)s cannot be completed yet: transfer "
                            "%(picking)s has %(available)s of the %(demand)s "
                            "%(uom)s of %(product)s it needs. Receive or move the "
                            "missing stock and complete the order again, or turn "
                            "off 'Validate Transfers on Order Completion' in "
                            "Field Service settings to complete the order and "
                            "book the transfer by hand.",
                            order=order.name,
                            picking=picking.name,
                            available=move.quantity,
                            demand=move.product_uom_qty,
                            uom=move.uom_id.name,
                            product=move.product_id.display_name,
                        )
                    )
                picking.button_validate()
                if picking.state != "done":
                    raise UserError(
                        self.env._(
                            "Order %(order)s cannot be completed yet: transfer "
                            "%(picking)s asks for a confirmation step before it "
                            "can be validated. Open the transfer, validate it "
                            "there, then complete the order.",
                            order=order.name,
                            picking=picking.name,
                        )
                    )

    def action_view_delivery(self):
        """
        This function returns an action that display existing delivery orders
        of given fsm order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        """
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        pickings = self.mapped("picking_ids")
        delivery_ids = self.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "outgoing"
        ).ids
        if len(delivery_ids) > 1:
            action["domain"] = [("id", "in", delivery_ids)]
        elif pickings:
            action["views"] = [(self.env.ref("stock.view_picking_form").id, "form")]
            action["res_id"] = delivery_ids[0]
        return action

    def action_view_returns(self):
        """
        This function returns an action that display existing return orders
        of given fsm order ids. It can either be a in a list or in a form
        view, if there is only one return order to show.
        """
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        pickings = self.mapped("picking_ids")
        return_ids = self.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "incoming"
        ).ids
        if len(return_ids) > 1:
            action["domain"] = [("id", "in", return_ids)]
        elif pickings:
            action["views"] = [(self.env.ref("stock.view_picking_form").id, "form")]
            action["res_id"] = return_ids[0]
        return action
