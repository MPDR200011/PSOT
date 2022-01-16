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

db = pg.connect(
    dbname=dbName, host=dbHost, port=dbPort, user=dbUser, passwd=dbPassword
)


def queryPlaces(db):
    return db.query("select * from place").dictresult()


def queryAllOccupancies(db):
    return db.query("select * from recent_occupancies").dictresult()


def queryPlaceOccupancy(db, placeId):
    return db.query(
        "select * from recent_occupancies where id = $1",
        (placeId,)
    ).dictresult()


@app.route("/places")
def getPlaces():
    return {'places': queryPlaces(db)}


@app.route("/occupancies")
def getOccupancies():
    occupancies = groupBy(queryAllOccupancies(db), 'id')
    for placeId in occupancies.keys():
        occupancies[placeId] = occupancies[placeId][0]
    return occupancies


@app.route("/occupancies/<placeId>")
def getPlaceOccupancy(placeId):
    occupancy = queryPlaceOccupancy(db, placeId)[0]
    return occupancy
