# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models

# The two priority scales use the same keys for different levels:
# maintenance.request  0 Very Low · 1 Low · 2 Normal · 3 High
# fsm.order            0 Normal   · 1 Low · 2 High   · 3 Urgent
PRIORITY_TO_FSM = {"0": "1", "1": "1", "2": "0", "3": "2"}


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    fsm_order_id = fields.Many2one(
        "fsm.order",
        "Field Service Order",
        help="Fsm Order Id. Linked record reference.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        # A request for an equipment that Field Service also knows gets a
        # maintenance-type FSM order at the equipment's location. Skipped when
        # the request itself was created by such an order (context fsm_order).
        requests = super().create(vals_list)
        if "fsm_order" in self.env.context:
            return requests
        order_type = self.env["fsm.order.type"].search(
            [("internal_type", "=", "maintenance")], order="id desc", limit=1
        )
        for request in requests.filtered("equipment_id.is_fsm_equipment"):
            fsm_equipment = self.env["fsm.equipment"].search(
                [("maintenance_equipment_id", "=", request.equipment_id.id)], limit=1
            )
            if not fsm_equipment.current_location_id:
                odoobot = self.env.ref("base.partner_root")
                request._message_log(
                    subject="Missing location",
                    body=self.env._(
                        "Order was not created because the "
                        "equipment's location is not set"
                    ),
                    message_type="notification",
                    author_id=odoobot.id,
                )
                continue
            vals = {
                "type": order_type.id,
                "equipment_ids": [Command.set(fsm_equipment.ids)],
                "location_id": fsm_equipment.current_location_id.id,
                "request_id": request.id,
                "description": request.description,
                "request_early": request.schedule_date,
                "scheduled_date_start": request.schedule_date,
            }
            if request.priority in PRIORITY_TO_FSM:
                vals["priority"] = PRIORITY_TO_FSM[request.priority]
            request.fsm_order_id = self.env["fsm.order"].create(vals)
        return requests
