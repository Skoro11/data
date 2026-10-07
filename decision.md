# School zone type selection

07.10.2026

NYC school zoning only applies to certain school types. Verified via NYC DOE enrollment policy (schools.nyc.gov / enrollmentsupport.schools.nyc):

Actual `school_type` values found in the School Quality Reports data (dnpx-dfnc): D75, Elementary, High School, High School Transfer, K-1, K-2, K-3, K-8, Middle, YABC.

| School type                        | Zoned?                                                                                                           |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Elementary                         | Yes                                                                                                              |
| K-1, K-2, K-3                      | Yes - grade-span variants of elementary (building only serves early grades, same zoning mechanism as Elementary) |
| K-8                                | Yes (same neighborhood-zoning concept, extended through grade 8)                                                 |
| Middle                             | Yes, except Districts 1, 7, 23 (choice districts, no zoning)                                                     |
| High School / High School Transfer | No - citywide choice/application-based, not tied to address                                                      |
| YABC (Young Adult Borough Centers) | No - alternative program for over-age/under-credit students, not address-based                                   |
| D75                                | No - citywide special education district, served by IEP need not geography                                       |

Decision: use Elementary, K-1, K-2, K-3, K-8, and Middle school zones only. High School, High School Transfer, YABC, and D75 excluded since "zoned school" doesn't apply to them - using their data would not represent a real address-based school assignment.

Filtered on school type k1,k2,k3,k8 elementary mmoiddle school, update year 2024 , rating mean ella and rating mean math all

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
