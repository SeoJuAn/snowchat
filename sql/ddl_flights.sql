create or replace TABLE TEST.PUBLIC.FLIGHTS (
	YEAR NUMBER(38,0),
	MONTH NUMBER(38,0),
	DAY NUMBER(38,0),
	DAY_OF_WEEK NUMBER(38,0),
	AIRLINE VARCHAR(16777216),
	FLIGHT_NUMBER NUMBER(38,0),
	TAIL_NUMBER VARCHAR(16777216),
	ORIGIN_AIRPORT VARCHAR(16777216),
	DESTINATION_AIRPORT VARCHAR(16777216),
	SCHEDULED_DEPARTURE NUMBER(38,0),
	DEPARTURE_TIME NUMBER(38,0),
	DEPARTURE_DELAY NUMBER(38,0),
	TAXI_OUT NUMBER(38,0),
	WHEELS_OFF NUMBER(38,0),
	SCHEDULED_TIME NUMBER(38,0),
	ELAPSED_TIME NUMBER(38,0),
	AIR_TIME NUMBER(38,0),
	DISTANCE NUMBER(38,0),
	WHEELS_ON NUMBER(38,0),
	TAXI_IN NUMBER(38,0),
	SCHEDULED_ARRIVAL NUMBER(38,0),
	ARRIVAL_TIME NUMBER(38,0),
	ARRIVAL_DELAY NUMBER(38,0),
	DIVERTED BOOLEAN,
	CANCELLED BOOLEAN,
	CANCELLATION_REASON VARCHAR(16777216),
	AIR_SYSTEM_DELAY NUMBER(38,0),
	SECURITY_DELAY NUMBER(38,0),
	AIRLINE_DELAY NUMBER(38,0),
	LATE_AIRCRAFT_DELAY NUMBER(38,0),
	WEATHER_DELAY NUMBER(38,0)
);