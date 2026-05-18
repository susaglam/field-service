# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FSMRouteDayRoute(models.Model):
    _inherit = "fsm.route.dayroute"

    fsm_vehicle_id = fields.Many2one(
        "fsm.vehicle",
        string="Vehicle",
        help="Vehicle assigned to this day-route. Drives capacity validation "
        "against the vehicle's max_product_qty.",
    )
    max_product_id = fields.Many2one(
        "product.product",
        related="route_id.max_product_id",
        store=True,
        readonly=True,
    )
    max_product_qty = fields.Float(
        compute="_compute_vehicle_capacity",
        string="Max Vehicle Capacity",
        digits="Product Unit of Measure",
        store=True,
        help="Capacity of the assigned vehicle for the route's max product.",
    )
    is_limited = fields.Boolean(
        compute="_compute_vehicle_capacity",
        string="Is Limited?",
        store=True,
        help="True if the assigned vehicle has a non-zero max_product_qty "
        "set for the route's max product.",
    )
    product_qty = fields.Float(
        compute="_compute_product_qty",
        string="Used Product Quantity",
        digits="Product Unit of Measure",
        store=True,
        help="Sum of the route's max product quantity across all moves "
        "belonging to this day-route's orders.",
    )
    product_qty_remaining = fields.Float(
        compute="_compute_product_qty",
        string="Available Stock Capacity",
        digits="Product Unit of Measure",
        store=True,
        help="max_product_qty minus product_qty. Negative values indicate "
        "the day-route exceeds the vehicle's capacity.",
    )

    @api.depends("fsm_vehicle_id", "route_id", "route_id.max_product_id")
    def _compute_vehicle_capacity(self):
        for rec in self:
            vehicle = rec.fsm_vehicle_id
            route_product = rec.route_id.max_product_id
            if (
                vehicle
                and route_product
                and vehicle.max_product_id == route_product
                and vehicle.max_product_qty
            ):
                rec.is_limited = True
                rec.max_product_qty = vehicle.max_product_qty
            else:
                rec.is_limited = False
                rec.max_product_qty = 0.0

    @api.depends("order_ids.move_ids", "route_id.max_product_id", "max_product_qty")
    def _compute_product_qty(self):
        for rec in self:
            qty = 0.0
            if rec.order_ids and rec.max_product_id:
                for order in rec.order_ids:
                    for move in order.move_ids:
                        if move.product_id == rec.max_product_id:
                            qty += move.product_uom_qty
            rec.product_qty = qty
            rec.product_qty_remaining = rec.max_product_qty - qty

    @api.constrains("is_limited", "product_qty_remaining")
    def check_vehicle_capacity(self):
        for rec in self:
            if rec.is_limited and rec.product_qty_remaining < 0:
                raise ValidationError(
                    _(
                        "The vehicle %(vehicle)s is over capacity "
                        "(%(used).2f > %(max).2f) on %(date)s.",
                        vehicle=rec.fsm_vehicle_id.name,
                        used=rec.product_qty,
                        max=rec.max_product_qty,
                        date=rec.date,
                    )
                )
