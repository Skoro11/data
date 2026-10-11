# Park proximity - typecategory filter

07.10.2026

Source: NYC Open Data, Parks Properties (enfh-gkve), 2,061 total properties.

Excluded typecategory values (not genuine recreational amenities):
- Undeveloped - vacant/unused land
- Operations - administrative Parks Dept facilities
- Managed Sites - administrative, not public recreational space
- Buildings/Institutions - structures, not park land
- Lot - undeveloped parcels
- Cemetery - not usable recreational space

Kept: Neighborhood Park, Flagship Park, Community Park, Playground, Jointly Operated Playground, Nature Area, Recreational Field/Courts, Garden, Mall, Parkway, Waterfront Facility, Historic House Park, Triangle/Plaza, Strip.

Query used:
https://data.cityofnewyork.us/resource/enfh-gkve.geojson?$where=typecategory NOT IN('Undeveloped','Operations','Managed Sites','Buildings/Institutions','Lot','Cemetery')&$limit=3000

Distance calculated to nearest polygon edge (not centroid), since park size varies too much (tiny plaza vs. Central Park) for a centroid-based distance to be accurate.
