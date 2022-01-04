import schedule
import time
import scanner
import sender
import asyncio
import os

from dotenv import load_dotenv


def scan_and_send():
    try:
        print(f"{time.ctime()}: scanning")
        scan = asyncio.run(scanner.scan_for_devices())

        print("Waiting for interface to come back")
        time.sleep(5)  # Wait for interface to come back online

        ingestServerHost = os.environ.get("DEST_HOST")
        print(f"Sending to: {ingestServerHost}")
        sender.send_scan(scan, ingestServerHost)
        print("Done\n")
    except:
        print("Error in this iteration")


def main():
    load_dotenv()
    schedule.every().minute.do(scan_and_send)

    schedule.run_all()
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
