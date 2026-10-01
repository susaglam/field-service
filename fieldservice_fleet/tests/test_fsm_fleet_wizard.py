# Copyright (C) 2019 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import new_test_user

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.fieldservice_fleet import hooks


class TestFSMFleetWizard(BaseCommon):
    # 20.0 runs BaseCommon tests as a plain internal user, not as superuser:
    # the dispatcher who converts vehicles manages both FSM and Fleet
    _test_user_groups = (
        "base.group_user",
        "base.group_partner_manager",
        "fieldservice.group_fsm_manager",
        "fleet.fleet_group_manager",
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Wizard = cls.env["fsm.fleet.wizard"]
        cls.fleet_vehicle_1 = cls.env.ref("fleet.vehicle_1")
        cls.person_1 = cls.env.ref("fieldservice.person_1")
        cls.driver_1 = cls.partner

    def test_convert_vehicle(self):
        # Convert a Fleet vehicle to FSM vehicle and link it
        self.Wizard.action_convert_vehicle(self.fleet_vehicle_1)

        # Search FSM vehicle records linked to the test Fleet vehicle
        fsm_vehicle = self.env["fsm.vehicle"].search(
            [("fleet_vehicle_id", "=", self.fleet_vehicle_1.id)]
        )

        # Create a driver partner without an associated fsm.person record
        driver_partner = self.env["res.partner"].create(
            {
                "name": "Driver Partner",
            }
        )

        # Retrieve the fsm_worker record for the driver partner
        fsm_worker = self.env["fsm.person"].search(
            [("partner_id", "=", driver_partner.id)]
        )

        self.assertEqual(
            len(fsm_vehicle),
            1,
            """FSM Fleet Wizard: Did not find FSM vehicle
               linked to Fleet vehicle""",
        )
        self.assertEqual(
            fsm_vehicle.name,
            self.fleet_vehicle_1.name,
            """FSM Fleet Wizard: FSM Vehicle and Fleet Vehicle
               names do not match""",
        )
        self.assertTrue(
            self.fleet_vehicle_1.is_fsm_vehicle,
            """FSM Fleet Wizard: Fleet vehicle boolean field
               is_fsm_vehicle is False""",
        )
        self.assertEqual(
            fsm_vehicle.person_id.partner_id,
            self.fleet_vehicle_1.driver_id,
            """FSM Fleet Wizard: FSM vehicle driver is not same
               as the Fleet vehicle driver""",
        )
        self.assertTrue(
            self.fleet_vehicle_1.driver_id and self.fleet_vehicle_1.is_fsm_vehicle,
            "Driver ID and is_fsm_vehicle condition is not True",
        )

        # Set the driver_id of the fleet vehicle to the driver partner
        self.fleet_vehicle_1.driver_id = driver_partner.id

        # Assert that fsm_worker is not found
        self.assertFalse(
            fsm_worker, "FSM worker found for driver partner, but it should not exist"
        )

        # Attempt to convert the Fleet vehicle again, but expect UserError
        # because we already converted it
        with self.assertRaises(UserError):
            self.Wizard.action_convert_vehicle(self.fleet_vehicle_1)

    def test_fsm_vehicle(self):
        self.fleet_vehicle_2 = self.env["fsm.vehicle"].create(
            {
                "name": "Vehicle 2",
                "person_id": self.person_1.id,
                "fleet_vehicle_id": self.fleet_vehicle_1.id,
            }
        )
        self.fleet_vehicle_1.is_fsm_vehicle = True
        self.fleet_vehicle_2.write({"driver_id": self.driver_1.id})
        manager = new_test_user(
            self.env,
            "test fleet manager",
            groups="fleet.fleet_group_manager,base.group_partner_manager",
        )
        user = new_test_user(self.env, "test base user", groups="base.group_user")
        brand = self.env["fleet.vehicle.model.brand"].create(
            {
                "name": "Audi",
            }
        )
        model = self.env["fleet.vehicle.model"].create(
            {
                "brand_id": brand.id,
                "name": "A3",
            }
        )
        hooks.pre_init_hook(self.env)
        self.fleet_vehicle_3 = (
            self.env["fleet.vehicle"]
            .with_user(manager)
            .create(
                {
                    "model_id": model.id,
                    "driver_id": user.partner_id.id,
                }
            )
        )
        self.context = {
            "active_model": "fleet.vehicle",
            "active_ids": [self.fleet_vehicle_3.id],
            "active_id": self.fleet_vehicle_3.id,
        }
        self.Wizard.with_context(**self.context).action_convert()

    def test_pre_init_hook_gives_existing_vehicles_a_fleet_vehicle(self):
        """What the hook is for: FSM vehicles that exist before this module is
        installed have no Fleet vehicle yet. The state is rebuilt here (DDL is
        transactional, so it is undone with the test)."""
        worker = self.env["fsm.person"].sudo().create({"name": "Van Driver"})
        vehicle = self.env["fsm.vehicle"].create(
            {
                "name": "Van 7",
                "person_id": worker.id,
                "fleet_vehicle_id": self.fleet_vehicle_1.id,
            }
        )
        self.env.flush_all()
        self.env.cr.execute(
            "ALTER TABLE fsm_vehicle ALTER COLUMN fleet_vehicle_id DROP NOT NULL"
        )
        self.env.cr.execute(
            "UPDATE fsm_vehicle SET fleet_vehicle_id = NULL WHERE id = %s",
            (vehicle.id,),
        )
        self.env.invalidate_all()

        hooks.pre_init_hook(self.env)

        fleet = vehicle.fleet_vehicle_id
        self.assertTrue(fleet, "the vehicle got a Fleet vehicle")
        self.assertNotEqual(fleet, self.fleet_vehicle_1, "a new one, not a reused one")
        self.assertTrue(fleet.is_fsm_vehicle)
        self.assertEqual(fleet.driver_id, worker.partner_id)
        # required Fleet columns took their defaults (20.0 added power_unit)
        self.assertTrue(fleet.power_unit)
        self.assertTrue(fleet.odometer_unit)

        # running it again changes nothing
        hooks.pre_init_hook(self.env)
        self.env.invalidate_all()
        self.assertEqual(vehicle.fleet_vehicle_id, fleet)
