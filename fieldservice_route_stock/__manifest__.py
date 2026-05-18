# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field Service Route Stock",
    "summary": "Capacity planning for FSM routes: track vehicle product "
    "capacity and aggregate per-day usage from order moves.",
    "version": "saas~19.3.1.2.3",
    "category": "Field Service",
    "author": "Open Source Integrators, "
    "Odoo Community Association (OCA), saas-19.3 port",
    "website": "https://github.com/susaglam/field-service",
    "depends": [
        "stock",
        "fieldservice_route",
        "fieldservice_stock",
        "fieldservice_vehicle",
    ],
    "data": [
        "views/fsm_vehicle.xml",
        "views/fsm_route.xml",
        "views/fsm_route_dayroute.xml",
    ],
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": ["max3903"],
    "installable": True,
}
