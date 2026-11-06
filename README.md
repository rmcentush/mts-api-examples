# MTS API examples

Copy-paste clients for the [MTS API](https://monitor-the-situation.com/developers): live world events from [Monitor the Situation](https://monitor-the-situation.com) as JSON, as a real-time stream, and as an archive of every past event.

## Get a key

Sign in at [monitor-the-situation.com/developers](https://monitor-the-situation.com/developers) and create a key. It's free; the Event Stream needs the Live plan, and the Archive download needs an Archive purchase.

```bash
export MTS_KEY=mts_...
```

## Examples

| Example | What it does | Plan |
|---|---|---|
| [`python/events.py`](python/events.py) | Polls the live feed with an ETag and prints new and changed events | Free |
| [`python/stream.py`](python/stream.py) | Keeps a live copy of the feed from the Event Stream | Live |
| [`javascript/events.mjs`](javascript/events.mjs) | The same polling client for Node 18+ | Free |
| [`javascript/stream.mjs`](javascript/stream.mjs) | The same stream client for Node 22+ or a browser | Live |
| [`archive.sh`](archive.sh) | Downloads and unpacks the Archive CSV | Archive |

```bash
python3 python/events.py
pip install websockets && python3 python/stream.py
node javascript/events.mjs
node javascript/stream.mjs
sh archive.sh
```

## Reference

- Docs, plans and limits: [monitor-the-situation.com/developers](https://monitor-the-situation.com/developers)
- OpenAPI description: [monitor-the-situation.com/openapi.json](https://monitor-the-situation.com/openapi.json)
- Terms: show events in your apps with the credit "Events by Monitor the Situation" linking to the event's `url`; reselling or republishing the dataset is not allowed. [Full terms](https://monitor-the-situation.com/developers#terms).
- Help: [help@monitor-the-situation.com](mailto:help@monitor-the-situation.com)

The example code is MIT licensed. The data is covered by the API terms.
