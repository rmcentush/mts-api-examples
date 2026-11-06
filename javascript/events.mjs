// Poll the MTS live feed and print events as they appear or change (Free plan).
//   MTS_KEY=mts_... node events.mjs
const BASE_URL = process.env.MTS_BASE_URL ?? 'https://monitor-the-situation.com';
const KEY = process.env.MTS_KEY;
const POLL_MS = 30_000; // Well inside the Free limit of 10 requests a minute.

let etag = null;
let seen = null; // Event ID -> updated_at, from the last poll that changed.

for (;;) {
  const response = await fetch(`${BASE_URL}/v1/events`, {
    headers: { Authorization: `Bearer ${KEY}`, ...(etag ? { 'If-None-Match': etag } : {}) },
  });
  if (response.status === 200) {
    etag = response.headers.get('ETag');
    const { events } = await response.json();
    const current = new Map(events.map(event => [event.id, event.updated_at]));
    if (!seen) {
      console.log(`${events.length} events in the live feed`);
    } else {
      for (const event of events) {
        if (seen.get(event.id) !== event.updated_at) {
          const change = seen.has(event.id) ? 'updated' : 'new';
          console.log(`${change}: S${event.severity} ${event.title} (${event.location_name}) ${event.url}`);
        }
      }
      for (const id of seen.keys()) if (!current.has(id)) console.log(`left the feed: ${id}`);
    }
    seen = current;
  } else if (response.status === 429 || response.status === 503) {
    await new Promise(resolve => setTimeout(resolve, Number(response.headers.get('Retry-After') ?? 60) * 1000));
  } else if (response.status !== 304) {
    throw new Error(`${response.status}: ${await response.text()}`);
  }
  await new Promise(resolve => setTimeout(resolve, POLL_MS));
}
