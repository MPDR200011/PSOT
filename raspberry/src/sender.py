import requests


def send_scan(scan, server=None):
    requests.post(f"{server}/ingest", json=scan)
