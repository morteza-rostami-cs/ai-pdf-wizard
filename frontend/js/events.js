// global SSE connection
export function connectSse() {
  let eventSource = null;

  if (eventSource) {
    console.log("event source already exists.");
    return;
  }

  eventSource = new EventSource("/api/sse/sse");

  // on connection open
  eventSource.onopen = function () {
    console.log("SSE connected");
  };

  // listen to a message
  eventSource.onmessage = function (e) {
    console.log("message: " + e.data);
  };

  // event: connected
  eventSource.addEventListener("connected", function (e) {
    console.log(`event: connected - ${e.data}`);
  });

  // event: test_event
  eventSource.addEventListener("test_event", function (e) {
    console.log("event: test_event -  " + e.data);
  });

  // error
  eventSource.onerror = function (err) {
    console.log("SSE error : ", err);
  };
}
