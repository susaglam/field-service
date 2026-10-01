# Copyright (C) 2019 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def pre_init_hook(env):
    """Give every existing FSM vehicle a Fleet vehicle.

    Once this module is installed fsm.vehicle delegates to fleet.vehicle through
    a required fleet_vehicle_id, so vehicles that already exist need one before
    the column is made NOT NULL.

    The hook runs before this module's columns exist, so it adds the two it
    writes. The Fleet vehicles are created through the ORM: fleet.vehicle has
    required columns with defaults (odometer, power, range and CO2 units) and
    the list grows between versions. The raw INSERT this replaces named them by
    hand, failed on 20.0's power_unit, and wrote is_fsm_vehicle before that
    column existed.

    Safe to run again: a vehicle that already has a Fleet vehicle is skipped.
    """
    cr = env.cr
    cr.execute("ALTER TABLE fsm_vehicle ADD COLUMN IF NOT EXISTS fleet_vehicle_id int4")
    cr.execute("ALTER TABLE fleet_vehicle ADD COLUMN IF NOT EXISTS is_fsm_vehicle bool")
    cr.execute(
        "SELECT id, name, person_id FROM fsm_vehicle WHERE fleet_vehicle_id IS NULL"
    )
    vehicles = cr.dictfetchall()
    if not vehicles:
        return
    env = env(su=True)
    # model_id is required on fleet.vehicle; take any, or make a neutral one
    model = env["fleet.vehicle.model"].search([], limit=1)
    if not model:
        brand = env["fleet.vehicle.model.brand"].create({"name": "Field Service"})
        model = env["fleet.vehicle.model"].create(
            {"name": "Vehicle", "brand_id": brand.id}
        )
    for veh in vehicles:
        driver = env["fsm.person"].browse(veh["person_id"] or []).partner_id
        fleet = env["fleet.vehicle"].create(
            {"model_id": model.id, "driver_id": driver.id}
        )
        env.flush_all()
        # keep the name the dispatchers know (fleet computes brand/model/plate)
        cr.execute(
            "UPDATE fleet_vehicle SET is_fsm_vehicle = TRUE, name = %s WHERE id = %s",
            (veh["name"], fleet.id),
        )
        cr.execute(
            "UPDATE fsm_vehicle SET fleet_vehicle_id = %s WHERE id = %s",
            (fleet.id, veh["id"]),
        )
    env.invalidate_all()
