import pg
import os
from dotenv import load_dotenv
from collections import Counter
import sched
import time
import datetime
import paho.mqtt.client as mqtt
import json


def getScanAccessPoints(db, scanId):
    return db.query(
        "select * from access_point where scan_id = $1",
        (scanId,)
    ).dictresult()


def invalidateOldScans(db):
    db.query(
        "delete from scan where scan_time < NOW() - INTERVAL '7 minutes'")


def getScans(db):
    return db.query("select * from scan").dictresult()


def getPlaces(db):
    return db.query("select * from place").dictresult()


def getAllAccessPoints(db):
    return db.query('select * from access_point').dictresult()


def getAllClients(db):
    return db.query('select * from client').dictresult()


def getPlaceWhiteList(db, place_id):
    return db.query('select * from ap_whitelist where place_id = $1',
                    (place_id,)).dictresult()


def getAllWhiteLists(db):
    return db.query('select * from ap_whitelist')\
                    .dictresult()


def addOccupancies(db, occupancies):
    db.query(
        "insert into occupancy (time, occupancy_percentage, confirmed_number,\
        place_id) values (NOW(), $1, $2, $3)",
        [
            (v['percentage'], v['confirmed_number'], k)
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


def calculateOccupancies(mqtt_client):
    try:
        # dbDialect = os.environ.get("DB_DIALECT") or "postgresql"
        dbUser = os.environ.get("DB_USER") or "jeronimo"
        dbPassword = os.environ.get("DB_PASSWORD") or "password123"
        dbHost = os.environ.get("DB_HOST") or "psot_db"
        dbPort = os.environ.get("DB_PORT") or 5432
        dbName = os.environ.get("DB_NAME") or "psot_info"

        print("Connecting...")
        db = pg.connect(
            dbname=dbName, host=dbHost, port=dbPort, user=dbUser, passwd=dbPassword
        )

        print("Removing old scans...")
        invalidateOldScans(db)

        print("Calculating occupancies...")
        allClients = getAllClients(db)
        clientsByAP = groupBy(allClients, 'access_point_id')
        print(f"{len(allClients)} clients, devided into {len(clientsByAP)} APs")

        allAccessPoints = getAllAccessPoints(db)
        for accessPoint in allAccessPoints:
            if accessPoint['id'] in clientsByAP:
                accessPoint['clients'] = clientsByAP[accessPoint['id']]
            else:
                accessPoint['clients'] = []

        accessPointsByScan = groupBy(allAccessPoints, 'scan_id')

        print(f"{len(allAccessPoints)} clients, divided into \
        {len(accessPointsByScan)} scans")

        accessPointWhiteLists = groupBy(getAllWhiteLists(db), 'place_id')
        scans = getScans(db)
        for scan in scans:
            accessPoints = []
            if scan['id'] in accessPointsByScan:
                accessPoints = accessPointsByScan[scan['id']]
                if scan['place_id'] in accessPointWhiteLists:
                    whiteList = set(map(
                        lambda x: x['name'],
                        accessPointWhiteLists[scan['place_id']]
                    ))

                    filtered = filter(
                        lambda ap: ap['name'] in whiteList,
                        accessPoints
                    )
                    accessPoints = list(filtered)

            scan['access_points'] = accessPoints

        occupancies = {}
        scansByPlaces = groupBy(scans, 'place_id')
        places = groupBy(getPlaces(db), 'id')
        for (placeId, placeScans) in scansByPlaces.items():
            occupancies[placeId] = {
                'percentage': 0,
                'confirmed_number': 0
            }

            # convert time stamp strings to unix timestamps
            for scan in placeScans:
                scanTime = time.mktime(datetime.datetime.strptime(
                        scan['scan_time'], "%Y-%m-%d %H:%M:%S").timetuple())
                print(f"times: {scanTime}")
                scan['time'] = scanTime

            # sort scans, most recent first
            placeScans.sort(key=lambda s: s['time'], reverse=True)

            partitionTimeSpan = 10
            initTime = placeScans[0]['time']
            currentTime = initTime
            scanPartitions = [set()]
            currentPartition = scanPartitions[0]

            # partition scans
            for scan in placeScans:
                while((currentTime - scan['time']) > partitionTimeSpan):
                    if len(currentPartition) > 0:
                        # no need to create new partition if
                        # the current one is empty
                        newPartition = set()
                        scanPartitions.append(newPartition)
                        currentPartition = newPartition
                    currentTime -= partitionTimeSpan

                for ap in scan['access_points']:
                    for client in ap['clients']:
                        currentPartition.add(client['mac_address'])

            print(scanPartitions)

            # count in how many partitions each mac address appears
            counts = Counter()
            for partition in scanPartitions:
                counts.update(partition)
            print(counts)

            # chooses mac adresses that appear in
            # a certain amount of different partitions
            threshold = 2
            confirmed = set(
                x for x, count in counts.items() if count >= threshold)

            place = places[placeId][0]
            occupancies[placeId] = {
                'percentage': (len(confirmed) * place['callibration_constant'])
                / place['capacity'],
                'confirmed_number': len(confirmed)
            }

            print(f"Place {place['name']}, \
            calculated {len(confirmed)} people")

        if len(occupancies) > 0:
            addOccupancies(db, occupancies)
        db.close()

        # prepare data for publishing
        publishingData = {}
        for (placeId, occupancy) in occupancies.items():
            publishingData[placeId] = {
                'name': places[placeId][0]['name'],
                'id': placeId,
                'occupancy_percentage': occupancy['occupancy_percentage'],
                'confirmed_number': occupancy['confirmed_number']
            }

        print("Publishing to MQTT...")
        mqtt_client.publish(
            'occupancy_notifications', json.dumps(publishingData))
        print("Done")

    except Exception as e:
        print(f"Error aggregating: {e}")


def periodic(scheduler, interval, action, actionargs=()):
    scheduler.enter(interval, 1, periodic,
                    (scheduler, interval, action, actionargs))
    action(*actionargs)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("MQTT Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.


def main():
    load_dotenv()

    client = mqtt.Client()
    client.on_connect = on_connect

    client.connect("psot_notifications", 1883, 60)
    client.loop_start()

    scheduler = sched.scheduler(time.time, time.sleep)
    periodic(scheduler, 60, calculateOccupancies, [client])
    scheduler.run()


if __name__ == "__main__":
    main()
