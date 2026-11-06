"""Keep a live copy of the MTS feed from the Event Stream (Live plan).

    pip install websockets
    MTS_KEY=mts_... python3 stream.py
"""
import asyncio
import json
import os
import sys

from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed, InvalidStatus

BASE_URL = os.environ.get("MTS_BASE_URL", "https://monitor-the-situation.com")
KEY = os.environ["MTS_KEY"]
STREAM_URL = BASE_URL.replace("http", "ws", 1) + "/v1/stream"
# Closes that reconnecting cannot fix: the key was revoked, or the Live plan ended.
FINAL_CLOSES = {4401: "The key was revoked or its access changed.", 4402: "The Live plan ended."}

events = {}  # Event ID -> event: the whole live feed, kept current.
sys.stdout.reconfigure(line_buffering=True)  # Print each event as it arrives, even into a log.


def apply(message):
    if message["type"] == "snapshot":
        events.clear()
        events.update((event["id"], event) for event in message["events"])
        print(f"{len(events)} events in the live feed")
        return
    for event in message["upserts"]:
        change = "updated" if event["id"] in events else "new"
        events[event["id"]] = event
        print(f"{change}: S{event['severity']} {event['title']} ({event['location_name']}) {event['url']}")
    for event_id in message["removed"]:
        events.pop(event_id, None)
        print(f"left the feed: {event_id}")


async def main():
    delay = 1
    while True:
        try:
            async with connect(STREAM_URL, additional_headers={"Authorization": f"Bearer {KEY}"}) as socket:
                delay = 1
                async for raw in socket:
                    apply(json.loads(raw))
        except InvalidStatus as refused:
            status = refused.response.status_code
            if status in (401, 403):  # A bad key or no Live plan: retrying cannot help.
                raise SystemExit(f"{status}: {refused.response.body.decode()}")
            print(f"The stream refused the connection ({status}); retrying")
        except ConnectionClosed as closed:
            code = closed.rcvd.code if closed.rcvd else None
            if code in FINAL_CLOSES:
                raise SystemExit(FINAL_CLOSES[code])
        except OSError as error:
            print(f"Connection failed: {error}")
        # Any other close: reconnect. The new snapshot replaces the copy.
        await asyncio.sleep(delay)
        delay = min(delay * 2, 60)


if __name__ == "__main__":
    asyncio.run(main())
