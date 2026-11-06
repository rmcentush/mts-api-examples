"""Poll the MTS live feed and print events as they appear or change (Free plan).

    MTS_KEY=mts_... python3 events.py
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE_URL = os.environ.get("MTS_BASE_URL", "https://monitor-the-situation.com")
KEY = os.environ["MTS_KEY"]
POLL_SECONDS = 30  # Well inside the Free limit of 10 requests a minute.
sys.stdout.reconfigure(line_buffering=True)  # Print each change as it arrives, even into a log.


def fetch_events(etag):
    """Returns (events, etag), or (None, etag) when nothing changed since the last poll."""
    headers = {"Authorization": f"Bearer {KEY}", "User-Agent": "mts-api-examples/1.0"}
    if etag:
        headers["If-None-Match"] = etag
    request = urllib.request.Request(f"{BASE_URL}/v1/events", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)["events"], response.headers.get("ETag")
    except urllib.error.HTTPError as error:
        if error.code == 304:
            return None, etag
        if error.code in (429, 503):
            time.sleep(int(error.headers.get("Retry-After", "60")))
            return None, etag
        raise SystemExit(f"{error.code}: {error.read().decode()}")


def main():
    etag = None
    seen = None  # Event ID -> updated_at, from the last poll that changed.
    while True:
        events, etag = fetch_events(etag)
        if events is not None:
            current = {event["id"]: event["updated_at"] for event in events}
            if seen is None:
                print(f"{len(events)} events in the live feed")
            else:
                for event in events:
                    if seen.get(event["id"]) != event["updated_at"]:
                        change = "updated" if event["id"] in seen else "new"
                        print(f"{change}: S{event['severity']} {event['title']} ({event['location_name']}) {event['url']}")
                for event_id in seen.keys() - current.keys():
                    print(f"left the feed: {event_id}")
            seen = current
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
