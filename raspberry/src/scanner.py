import asyncio

import pyrcrack
import dotmap

import time
import json


async def scan_wifi(number_of_iterations=5, iteration_duration=2):
    """Scan for targets, return json."""
    airmon = pyrcrack.AirmonNg()

    results = {}

    counter = 0
    async with airmon('wlp4s0') as mon:

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
                                "mac_address": mac_address
                            })

                counter += 1
                if counter >= number_of_iterations:
                    break
                await asyncio.sleep(iteration_duration)

    return results


async def scan_for_devices():
    access_points = await scan_wifi(15, 2)

    scan = {
        "scanTime": time.time(),
        "wifiAccessPoints": [ap for ap in access_points.values()]
    }

    return scan


def main():
    scan = asyncio.run(scan_for_devices())
    print(json.dumps(scan, sort_keys=True, indent=4))


if __name__ == "__main__":
    main()
