DROP TABLE IF EXISTS scan CASCADE;
DROP TABLE IF EXISTS place CASCADE;
DROP TABLE IF EXISTS occupancy CASCADE;
DROP TABLE IF EXISTS access_point CASCADE;
DROP TABLE IF EXISTS client CASCADE;

CREATE TABLE place (
	id SERIAL PRIMARY KEY,
    name varchar(255) NOT NULL,
    capacity integer NOT NULL,
    callibration_constant real NOT NULL
);

CREATE TABLE scan (
	id SERIAL PRIMARY KEY,
    scan_time timestamp,
    place_id SERIAL REFERENCES place ("id") ON DELETE CASCADE
);

CREATE TABLE occupancy (
	id SERIAL PRIMARY KEY,
    time timestamp NOT NULL,
    occupancy_percentage real NOT NULL,
    confirmed_number integer NOT NULL,
    place_id SERIAL REFERENCES place ("id") ON DELETE CASCADE
);

CREATE TABLE access_point (
	id SERIAL PRIMARY KEY,
    name varchar(255) NOT NULL,
    mac_address varchar(255) NOT NULL,
    num_connected_clients integer NOT NULL,
    scan_id SERIAL REFERENCES scan ("id") ON DELETE CASCADE
);

CREATE TABLE client (
	id SERIAL PRIMARY KEY,
    mac_address varchar(255) NOT NULL,
    scan_id SERIAL REFERENCES scan ("id") ON DELETE CASCADE,
    access_point_id SERIAL REFERENCES access_point ("id") ON DELETE CASCADE
);

CREATE TABLE ap_whitelist (
    id SERIAL PRIMARY KEY,
    place_id SERIAL REFERENCES place ("id") ON DELETE CASCADE,
    name varchar(255) NOT NULL
);
