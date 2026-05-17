# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field Service - Leaflet Map (OpenStreetMap)",
    "summary": "Display FSM locations on a Leaflet/OSM map without PostGIS.",
    "version": "saas~19.3.1.0.0",
    "license": "AGPL-3",
    "category": "Field Service",
    "author": "saas-19.3 port, Odoo Community Association (OCA)",
    "website": "https://github.com/susaglam/field-service",
    "depends": [
        "fieldservice",
        "web_view_leaflet_map",
    ],
    "data": [
        "views/fsm_location_views.xml",
    ],
    "installable": True,
}
