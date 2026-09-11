# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Purchase",
    "summary": "Manage FSM Purchases",
    "author": "Open Source Integrators, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "category": "Field Service",
    "license": "AGPL-3",
    "version": "saas~19.4.1.0.3",
    "depends": [
        "fieldservice",
        "purchase",
    ],
    "data": [
        "security/ir.access.csv",
        "views/fsm_person.xml",
    ],
    "development_status": "Beta",
    "maintainers": [
        "osi-scampbell",
    ],
}
