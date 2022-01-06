import pg
import os
from dotenv import load_dotenv


def getScanAccessPoints(db, scanId):
    return db.query(
        "select * from AccessPoint where scanId = $1",
        (scanId,)
    ).dictresult()


def invalidateOldScans(db):
    db.query(
        "delete from Scan where scanTime >= NOW() - INTERVAL '5 minutes'")


def getScans(db):
    return db.query("select * from Scan").dictresult()


def getPlaces(db):
    return db.query("select * from Place").dictresult()


def getAllAccessPoints(db):
    return db.query('select * from AccessPoint').dictresult()


def addOccupancies(db, occupancies):
    db.query(
        "insert into Occupancy (time, occupancyLevel, placeId)\
            values (NOW(), $1, $2)",
        [(k, v) for (k, v) in occupancies.items()]
    )


def groupBy(objList, key):
    res = {}

    for obj in objList:
        if obj[key] not in res:
            res[obj[key]] = []

        res[obj[key]].append(obj)

    return res


def main():
    load_dotenv()

    # dbDialect = os.environ.get("DB_DIALECT") or "postgresql"
    dbUser = os.environ.get("DB_USER") or "jeronimo"
    dbPassword = os.environ.get("DB_PASSWORD") or "password123"
    dbHost = os.environ.get("DB_HOST") or "psot_db"
    dbPort = os.environ.get("DB_PORT") or 5432
    dbName = os.environ.get("DB_NAME") or "psot_info"

    db = pg.connect(
        dbname=dbName, host=dbHost, port=dbPort, user=dbUser, passwd=dbPassword
    )

    invalidateOldScans(db)
    scans = getScans(db)
    places = getPlaces(db)
    scanAPs = groupBy(getAllAccessPoints(db), 'scanId')

    occupancies = {}

    for scanId in scanAPs.keys():
        max = 0
        for ap in scanAPs[scanId]:
            max = max(max, ap.numConnectClients)

        place = places[scans[scanId].placeId]

        occupancy = (max * place.callibrationConstant) / place.capacity

        occupancies[place.id] = occupancy

    db.close()
