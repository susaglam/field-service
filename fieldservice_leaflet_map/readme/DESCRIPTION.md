Shows Field Service locations on an OpenStreetMap map (Leaflet), without PostGIS.
Locations are placed by the latitude/longitude of their contact; the popup shows the
location's description so dispatchers see access codes, parking and contact tips
without opening the form.

Optionally geocodes a location's address when it is created or its address changes
(Field Service settings). Geocoding is best effort: a failed lookup is logged and
never blocks saving the location.
