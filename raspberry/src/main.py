import schedule
import time
import scanner
import sender
import asyncio
import os

from dotenv import load_dotenv
load_dotenv()

server = os.environ.get("DEST_HOST") or "http://localhost:8081"

def scan_and_send():
    try:
        print(f"{time.ctime()}: scanning")
        scan = asyncio.run(scanner.scan_for_devices())

        print("Waiting for interface to come back")
        time.sleep(5)  # Wait for interface to come back online

        print(f"Sending to: {server}")
        sender.send_scan(scan, server)
        print("Done\n")
    except:
        print("Error in this iteration")


def main():
    schedule.every().minute.do(scan_and_send)

    schedule.run_all()
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
