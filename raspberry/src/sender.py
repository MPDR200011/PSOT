import requests


def send_scan(scan, server=None):
    requests.post(f"http://{server}/ingest", json=scan)
