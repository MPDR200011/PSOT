import pg
import os
from flask import Flask
from flask_cors import CORS

"""
    SELECT tbl.*
FROM place_occupancy tbl
  right JOIN
  (
    SELECT id, max(time) as maxTime
    FROM place_occupancy
    GROUP BY id
  ) tbl1
  ON tbl1.id = tbl.id
WHERE tbl1.maxTime = tbl.time;
"""

dbUser = os.environ.get("DB_USER") or "jeronimo"
dbPassword = os.environ.get("DB_PASSWORD") or "password123"
dbHost = os.environ.get("DB_HOST") or "psot_db"
dbPort = os.environ.get("DB_PORT") or 5432
dbName = os.environ.get("DB_NAME") or "psot_info"


def groupBy(objList, key):
    res = {}

    for obj in objList:
        if obj[key] not in res:
            res[obj[key]] = []

        res[obj[key]].append(obj)

    return res


app = Flask(__name__)
CORS(app)


def queryPlaces(db):
    return db.query("select * from place").dictresult()


def queryAllOccupancies(db):
    return db.query("select * from recent_occupancies").dictresult()


def queryPlaceOccupancy(db, placeId):
    return db.query(
        "select * from recent_occupancies where id = $1",
        (placeId,)
    ).dictresult()


def queryPlaceOccupancyHistory(db, placeId):
    return db.query(
        "select * from occupancy where place_id=$1\
        and time >= NOW() - interval '6 hours'",
        (placeId,)
    ).dictresult()


@app.route("/places")
def getPlaces():
    db = pg.connect(
        dbname=dbName, host=dbHost, port=dbPort, user=dbUser, passwd=dbPassword
    )

    return {'places': queryPlaces(db)}


@app.route("/occupancies")
def getOccupancies():
    db = pg.connect(
        dbname=dbName, host=dbHost, port=dbPort, user=dbUser, passwd=dbPassword
    )

    occupancies = groupBy(queryAllOccupancies(db), 'id')
    for placeId in occupancies.keys():
        occupancies[placeId] = occupancies[placeId][0]
    return occupancies


@app.route("/occupancies/<placeId>")
def getPlaceOccupancy(placeId):
    db = pg.connect(
        dbname=dbName, host=dbHost, port=dbPort, user=dbUser, passwd=dbPassword
    )

    occupancy = queryPlaceOccupancy(db, placeId)[0]
    return occupancy


@app.route("/occupancies/<placeId>/history")
def getPlaceOccupancyHistory(placeId):
    db = pg.connect(
        dbname=dbName, host=dbHost, port=dbPort, user=dbUser, passwd=dbPassword
    )

    queryResult = queryPlaceOccupancyHistory(db, placeId)

    history = {
        'placeId': placeId,
        'records': [{
            'time': row['time'],
            'percentage': row['occupancy_percentage'],
            'confirmedNumber': row['confirmed_number']
        } for row in queryResult]
    }

    return history
