import time
import scanner
import sender
import asyncio
import os
import sched

from dotenv import load_dotenv


def scan_and_send():
    try:
        print(f"{time.ctime()}: scanning")
        scan = asyncio.run(scanner.scan_for_devices())

        print("Waiting for interface to come back")
        time.sleep(15)  # Wait for interface to come back online

        ingestServerHost = os.environ.get("DEST_HOST")
        print(f"Sending to: {ingestServerHost}")
        sender.send_scan(scan, ingestServerHost)
        print("Done\n")
    except Exception as e:
        print("Error in this iteration", e)


def periodic(scheduler, interval, action, actionargs=()):
    scheduler.enter(interval, 1, periodic,
                    (scheduler, interval, action, actionargs))
    action(*actionargs)


def main():
    load_dotenv()

    scheduler = sched.scheduler(time.time, time.sleep)
    periodic(scheduler, 60, scan_and_send)
    scheduler.run()


if __name__ == "__main__":
    main()
