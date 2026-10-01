# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    request_id = fields.Many2one(
        "maintenance.request",
        string="Maintenance Request",
        help="Request Id. Linked record reference.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        # A maintenance-type order asks the maintenance team for each of its
        # equipments that maintenance knows (fsm.equipment delegates to
        # maintenance.equipment). fsm.order has carried several equipments
        # (equipment_ids) since 14.0; this hook still read a single
        # `equipment_id` and failed on every maintenance order.
        orders = super().create(vals_list)
        for order in orders:
            if order.type.internal_type != "maintenance" or order.request_id:
                continue
            requests = self.env["maintenance.request"]
            for equipment in order.equipment_ids:
                maintenance_equipment = equipment.maintenance_equipment_id
                if not maintenance_equipment:
                    continue
                requests |= (
                    self.env["maintenance.request"]
                    .with_context(fsm_order=True)
                    .create(
                        {
                            "name": order.name or "",
                            "equipment_id": maintenance_equipment.id,
                            "maintenance_type": "corrective",
                            "maintenance_team_id": (
                                maintenance_equipment.maintenance_team_id.id
                            ),
                            "schedule_date": order.request_early,
                            "description": order.description,
                            "fsm_order_id": order.id,
                        }
                    )
                )
            # request_id holds one request; the others stay findable through
            # maintenance.request.fsm_order_id
            order.request_id = requests[:1]
        return orders
