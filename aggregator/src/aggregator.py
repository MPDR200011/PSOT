import pg
import os
from dotenv import load_dotenv
from collections import Counter


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


def getAllClients(db):
    return db.query('select * from Client').dictresult()


def addOccupancies(db, occupancies):
    db.query(
        "insert into Occupancy (time, occupancyPercentage, confirmedNumber,\
        placeId) values (NOW(), $1, $2, $3)",
        [
            (v['percentage'], v['confirmedNumber'], k)
            for (k, v) in occupancies.items()
        ]
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

    allClients = getAllClients(db)
    clientsByAP = groupBy(allClients, 'accessPointId')

    allAccessPoints = getAllAccessPoints(db)
    for accessPoint in allAccessPoints:
        accessPoint['clients'] = clientsByAP[accessPoint['id']]

    accessPointsByScan = groupBy(allAccessPoints, 'scanId')

    scans = getScans(db)
    for scan in scans:
        scan['accessPoints'] = accessPointsByScan[scan['id']]

    occupancies = {}
    scansByPlaces = groupBy(scans, 'placeId')
    places = groupBy(getPlaces(db), 'id')
    for (placeId, placeScans) in scansByPlaces.items():
        # sort scans, most recent first
        placeScans.sort(lambda s: s['time'], reverse=True)

        partitionTimeSpan = 10
        initTime = placeScans[0]['time']
        currentTime = initTime
        scanPartitions = [set()]
        currentPartition = scanPartitions[0]

        # partition scans
        for scan in placeScans:
            while((scan['time'] - currentTime) > partitionTimeSpan):
                if len(currentPartition) > 0:
                    # no need to create new partition if
                    # the current one is empty
                    newPartition = set()
                    scanPartitions.append(newPartition)
                    currentPartition = newPartition
                currentTime += partitionTimeSpan

            for ap in scan['accessPoints']:
                for client in ap['clients']:
                    currentPartition.add(client['macAddress'])

        # count in how many partitions each mac address appears
        counts = Counter()
        for partition in scanPartitions:
            counts.update(partition)

        # chooses mac adresses that appear in
        # a certain amount of different partitions
        threshold = 4
        confirmed = set(x for x, count in counts.items() if count >= threshold)

        place = places[placeId]
        occupancies[placeId] = {
            'percentage': (len(confirmed) * place['callibrationConstant'])
            / place['capacity'],
            'confirmedNumber': len(confirmed)
        }

    addOccupancies(db, occupancies)

    db.close()
