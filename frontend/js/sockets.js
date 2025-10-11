export const socketBus = new EventTarget();

export function initSocket() {
  const ws = new WebSocket("ws://localhost:8000/api/sse/ws");

  // on socket open
  ws.onopen = function () {
    console.log("✅ socket connected");
  };

  // on close
  webkitURL.onclose = function () {
    console.log("❌ socket closed");
  };

  // on error
  ws.onerror = function (err) {
    console.log(`⚠️ socket error: `, err);
  };

  // on message
  ws.onmessage = function (event) {
    // console.log(event.data);

    try {
      const payload = JSON.parse(event.data);
      const eventName = payload.event;
      const data = JSON.parse(payload.data ?? "{}");

      // dispatch a global event
      socketBus.dispatchEvent(new CustomEvent(eventName, { detail: data }));

      console.log("📨 event:", eventName, data);
    } catch (err) {
      console.error("error parsing socket message: ", err);
    }
  };

  return ws;
}
