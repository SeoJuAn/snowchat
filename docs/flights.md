**Table 1: TEST.PUBLIC.FLIGHTS** (Stores detailed information about flight records)

This table contains operational records of flights including schedule, departure, arrival, delay, and cancellation details.

- YEAR: Number (4,0) [Not Null] – Year of the flight
- MONTH: Number (2,0) [Not Null] – Month of the flight
- DAY: Number (2,0) [Not Null] – Day of the month
- DAY_OF_WEEK: Number (1,0) – Day of the week (1=Monday, 7=Sunday)
- AIRLINE: Varchar (10) – Airline carrier code
- FLIGHT_NUMBER: Number (6,0) – Flight number
- TAIL_NUMBER: Varchar (20) – Aircraft tail number
- ORIGIN_AIRPORT: Varchar (10) – Origin airport code
- DESTINATION_AIRPORT: Varchar (10) – Destination airport code
- SCHEDULED_DEPARTURE: Number (4,0) – Scheduled departure time (hhmm format)
- DEPARTURE_TIME: Number (4,0) – Actual departure time (hhmm format)
- DEPARTURE_DELAY: Number (5,0) – Departure delay in minutes
- TAXI_OUT: Number (5,0) – Taxi out time in minutes
- WHEELS_OFF: Number (4,0) – Time when aircraft took off (hhmm format)
- SCHEDULED_TIME: Number (5,0) – Scheduled duration of flight in minutes
- ELAPSED_TIME: Number (5,0) – Actual elapsed time of flight in minutes
- AIR_TIME: Number (5,0) – Actual flying time in minutes
- DISTANCE: Number (6,0) – Distance between airports in miles
- WHEELS_ON: Number (4,0) – Time when aircraft landed (hhmm format)
- TAXI_IN: Number (5,0) – Taxi in time in minutes
- SCHEDULED_ARRIVAL: Number (4,0) – Scheduled arrival time (hhmm format)
- ARRIVAL_TIME: Number (4,0) – Actual arrival time (hhmm format)
- ARRIVAL_DELAY: Number (5,0) – Arrival delay in minutes
- DIVERTED: Boolean – Whether the flight was diverted (TRUE/FALSE)
- CANCELLED: Boolean – Whether the flight was cancelled (TRUE/FALSE)
- CANCELLATION_REASON: Varchar (10) – Reason for cancellation (A=Airline, B=Weather, C=National Air System, D=Security)
- AIR_SYSTEM_DELAY: Number (5,0) – Minutes of delay due to air system
- SECURITY_DELAY: Number (5,0) – Minutes of delay due to security
- AIRLINE_DELAY: Number (5,0) – Minutes of delay caused by airline
- LATE_AIRCRAFT_DELAY: Number (5,0) – Minutes of delay caused by late-arriving aircraft
- WEATHER_DELAY: Number (5,0) – Minutes of delay caused by weather