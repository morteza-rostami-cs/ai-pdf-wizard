const { reactive, ref, readonly } = Vue;

let socketInstance = null;

export const socketStore = (() => {
  // reactive state for socket data
  const state = reactive({
    //messages: [],
    uploads: [],
    connected: false, //is socket connected
  });

  // connect to socket
  function connect(url = "ws://localhost:8000/api/sse/ws") {
    if (socketInstance) return; //return if socket already connected

    socketInstance = new WebSocket(url); //new socket connection

    socketInstance.onopen = () => {
      console.log("socket connected");
      state.connected = true;
    };

    // on message
    socketInstance.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        //console.log(data);

        //if (data.event === "ping") return; // just skip ping events

        // data.event and data.data
        const eventName = data.event;
        const eventData = data.data;

        switch (eventName) {
          case "upload_progress":
            const upload = state.uploads.find((u) => u.id == eventData.id);

            if (upload) {
              upload.progress = eventData.progress; // update progress
            } else {
              state.uploads.push(eventData); // eventData = Upload doc
            }
            break;

          case "upload_done":
          case "upload_failed":
            const up_doc = state.uploads.find((u) => u.id === eventData.id);
            if (up_doc) {
              upload.status = eventName === "upload_done" ? "done" : "failed";
            }
            break;

          default:
            console.log("other events: ", eventName);
        }
      } catch (err) {
        console.error("socket message parse error: ", err);
      }
    };

    // on socket close
    socketInstance.onclose = () => {
      console.log("socket disconnected.");
      state.connected = false;
      socketInstance = null;
    };

    socketInstance.onerror = (err) => {
      console.log("socket error ", err);
    };
  }

  // a function for disconnection
  function disconnect() {
    if (!socketInstance) return;
    socketInstance.close();
    socketInstance = null;
  }

  // a function for sending message
  function sendMessage(msg) {
    if (socketInstance && state.connected) {
      socketInstance.send(JSON.stringify(msg));
    }
  }

  return {
    state: readonly(state),
    connect,
    disconnect,
    sendMessage,
  };
})();
