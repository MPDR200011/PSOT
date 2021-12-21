import schedule
import time
import scanner
import sender
import asyncio


def scan_and_send():
    print(f"{time.ctime()}: scanning")
    scan = asyncio.run(scanner.scan_for_devices())

    print("Waiting for interface to come back")
    time.sleep(5)  # Wait for interface to come back online

    server = "localhost:8081"

    print(f"Sending to: {server}")
    sender.send_scan(scan, server)
    print("Done\n")


def main():
    schedule.every().minute.do(scan_and_send)

    schedule.run_all()
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
