import asyncio

import pyrcrack
import dotmap

import time
import json
import os


async def scan_wifi(number_of_iterations=5, iteration_duration=2):
    """Scan for targets, return json."""
    airmon = pyrcrack.AirmonNg()

    results = {}

    counter = 0
    async with airmon(os.environ.get("SCANNER_INTERFACE")) as mon:

        async with pyrcrack.AirodumpNg() as pdump:

            # give time for scan
            await asyncio.sleep(iteration_duration)

            async for result in pdump(mon.monitor_interface):
                for access_point in result:
                    temp = results[f"{access_point}"] = {
                        "name": access_point.essid,
                        "macAddress": access_point.bssid,
                        "numConnectedClients": len(access_point.clients),
                        "concreteDetectedClients": []
                    }

                    for client in access_point.clients:
                        mac_address = client.bssid
                        if not isinstance(mac_address, dotmap.DotMap):
                            temp["concreteDetectedClients"].append({
                                "macAddress": mac_address
                            })

                counter += 1
                if counter >= number_of_iterations:
                    break
                await asyncio.sleep(iteration_duration)

    return results


async def scan_for_devices():
    """
        Produces an object with the following strutcure
        {
            "scanTime": 0,
            "place": <placeid>,
            "wifiAccessPoints": [
                {
                    "name": "",
                    "macAddress": "",
                    "numConnectedClients": 0,
                    "concreteDetectedClients": [
                        {
                            "macAddress": ""
                        },
                        .
                        .
                        .
                    ]
                },
                .
                .
                .
            ]
        }
    """
    access_points = await scan_wifi(15, 2)

    scanTime = time.strftime("%Y-%m-%d %H:%M:%S")
    scan = {
        "scanTime": scanTime,
        "place": os.environ.get("PLACE_ID"),
        "wifiAccessPoints": [ap for ap in access_points.values()]
    }

    return scan


def main():
    scan = asyncio.run(scan_for_devices())
    print(json.dumps(scan, sort_keys=True, indent=4))


if __name__ == "__main__":
    main()
