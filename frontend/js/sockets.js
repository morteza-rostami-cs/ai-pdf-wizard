export function initSocket() {
  const ws = new WebSocket("ws://localhost:8000/api/sse/ws");

  // on socket open
  ws.onopen = function () {
    console.log("socket connected");
  };

  // on message
  ws.onmessage = function (event) {
    console.log(event.data);
  };

  // on close
  webkitURL.onclose = function () {
    console.log("socket closed");
  };

  // on error
  ws.onerror = function (err) {
    console.log(`socket error: `, err);
  };
}
