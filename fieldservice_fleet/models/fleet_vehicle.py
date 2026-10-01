# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    is_fsm_vehicle = fields.Boolean(
        string="Is used for Field Service?",
        help="Is Fsm Vehicle. Boolean flag — true when the condition holds.",
    )

    def set_fsm_driver(self):
        for record in self.filtered("is_fsm_vehicle").filtered("driver_id"):
            driver_partner = record.driver_id
            fsm_worker = self.env["fsm.person"].search(
                [("partner_id", "=", driver_partner.id)], limit=1
            )
            if not fsm_worker:
                # The driver is often an employee with a login. On 20.0 writing
                # on such a contact requires user-administration rights
                # (res.partner.write checks access on the linked internal
                # user), which a dispatcher does not have. Converting the
                # vehicle IS theirs to do, so the worker record of its driver
                # is created with elevated rights.
                fsm_worker = (
                    self.env["fsm.person"]
                    .sudo()
                    .create({"partner_id": driver_partner.id})
                )
                driver_partner.sudo().fsm_person = True
            fsm_vehicle = self.env["fsm.vehicle"].search(
                [("fleet_vehicle_id", "=", record.id)], limit=1
            )
            # Assign the worker to the FSM vehicle
            fsm_vehicle.person_id = fsm_worker.id
