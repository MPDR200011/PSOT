DROP TABLE IF EXISTS Scan CASCADE;
DROP TABLE IF EXISTS Place CASCADE;
DROP TABLE IF EXISTS Occupancy CASCADE;
DROP TABLE IF EXISTS AccessPoint CASCADE;
DROP TABLE IF EXISTS Client CASCADE;

CREATE TABLE Place (
	id SERIAL PRIMARY KEY,
    name varchar(50) NOT NULL,
    capacity integer NOT NULL,
    callibrationConstant real NOT NULL,
);

CREATE TABLE Scan (
	id SERIAL PRIMARY KEY,
    scanTime timestamp,
    placeId SERIAL REFERENCES Place ("id") ON DELETE CASCADE
);

CREATE TABLE Occupancy (
	id SERIAL PRIMARY KEY,
    time timestamp NOT NULL,
    occupancyLevel real NOT NULL,
    placeId SERIAL REFERENCES Place ("id") ON DELETE CASCADE
);

CREATE TABLE AccessPoint (
	id SERIAL PRIMARY KEY,
    name varchar(50) NOT NULL,
    macAddress varchar(255) NOT NULL,
    numConnectClients integer NOT NULL,
    scanId SERIAL REFERENCES Scan ("id") ON DELETE CASCADE
);

CREATE TABLE Client (
	id SERIAL PRIMARY KEY,
    macAddress varchar(255) NOT NULL,
    scanId SERIAL REFERENCES Scan ("id") ON DELETE CASCADE,
    accessPointId SERIAL REFERENCES AccessPoint ("id") ON DELETE CASCADE
);
