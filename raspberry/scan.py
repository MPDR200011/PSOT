import asyncio

import pyrcrack
import dotmap

from rich.console import Console


async def scan_for_targets():
    """Scan for targets, return json."""
    console = Console()
    console.clear()
    console.show_cursor(False)
    airmon = pyrcrack.AirmonNg()

    counter = 0
    async with airmon('wlp4s0') as mon:
        async with pyrcrack.AirodumpNg() as pdump:
            async for result in pdump(mon.monitor_interface):
                console.clear()
                for access_point in result:
                    print(f"{access_point}:")
                    for client in access_point.clients:
                        mac_address = client.bssid
                        if not isinstance(mac_address, dotmap.DotMap):
                            print(f"\t{mac_address}")
                        else:
                            print("\t n\\a")

                await asyncio.sleep(2)
                counter += 1
                if counter > 5:
                    break


asyncio.run(scan_for_targets())
