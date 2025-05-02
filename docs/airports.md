**Table 3: TEST.PUBLIC.AIRPORTS** (Stores airport location and identification information)

This table contains details about airports including their codes, names, locations, and geographic coordinates.

- IATA_CODE: Varchar (10) [Primary Key, Not Null] – Three-letter IATA airport code
- AIRPORT: Varchar (255) – Full name of the airport
- CITY: Varchar (100) – City where the airport is located
- STATE: Varchar (10) – State abbreviation (US states only)
- COUNTRY: Varchar (100) – Country where the airport is located
- LATITUDE: Number (10,5) – Geographic latitude of the airport
- LONGITUDE: Number (10,5) – Geographic longitude of the airport