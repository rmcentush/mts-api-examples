// Keep a live copy of the MTS feed from the Event Stream (Live plan).
//   MTS_KEY=mts_... node stream.mjs     (Node 22+; the same code runs in a browser)
// In a browser the key is visible to anyone using the page: connect from your own server
// unless only you use it.
const BASE_URL = globalThis.process?.env.MTS_BASE_URL ?? 'https://monitor-the-situation.com';
const KEY = globalThis.process?.env.MTS_KEY ?? globalThis.MTS_KEY;
const STREAM_URL = `${BASE_URL.replace(/^http/, 'ws')}/v1/stream`;
// Closes that reconnecting cannot fix: the key was revoked, or the Live plan ended.
const FINAL_CLOSES = { 4401: 'The key was revoked or its access changed.', 4402: 'The Live plan ended.' };

const events = new Map(); // Event ID -> event: the whole live feed, kept current.
let delay = 1000;

function apply(message) {
  if (message.type === 'snapshot') {
    events.clear();
    for (const event of message.events) events.set(event.id, event);
    console.log(`${events.size} events in the live feed`);
    return;
  }
  for (const event of message.upserts) {
    const change = events.has(event.id) ? 'updated' : 'new';
    events.set(event.id, event);
    console.log(`${change}: S${event.severity} ${event.title} (${event.location_name}) ${event.url}`);
  }
  for (const id of message.removed) {
    events.delete(id);
    console.log(`left the feed: ${id}`);
  }
}

function connect() {
  // Browsers cannot set headers on a WebSocket, so the key travels as a subprotocol.
  const socket = new WebSocket(STREAM_URL, ['mts', KEY]);
  // A ping every 30 seconds keeps idle proxies from dropping the connection.
  let keepalive;
  socket.onopen = () => {
    delay = 1000;
    keepalive = setInterval(() => socket.send('ping'), 30_000);
  };
  socket.onmessage = ({ data }) => {
    if (data !== 'pong') apply(JSON.parse(data));
  };
  socket.onclose = ({ code }) => {
    clearInterval(keepalive);
    if (FINAL_CLOSES[code]) {
      console.error(FINAL_CLOSES[code]);
      return;
    }
    // Any other close: reconnect. The new snapshot replaces the copy.
    setTimeout(connect, delay);
    delay = Math.min(delay * 2, 60_000);
  };
}

connect();
