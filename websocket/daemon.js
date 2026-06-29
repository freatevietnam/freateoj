import { createServer } from "http";
import { Server } from "socket.io";

const PORT = parseInt(process.env.PORT || "9996");

const httpServer = createServer((req, res) => {
  // HTTP POST endpoint for Django to post events
  if (req.method === "POST" && req.url === "/post") {
    let body = "";
    req.on("data", (chunk) => {
      body += chunk;
      if (body.length > 65536) {
        res.writeHead(413);
        res.end("too large");
        req.destroy();
      }
    });
    req.on("end", () => {
      try {
        const { command, channel, message } = JSON.parse(body);
        if (command === "post" && typeof channel === "string") {
          messageId++;
          const msg = { id: messageId, channel, message };
          messages.push(msg);
          if (messages.length > maxQueue) messages.shift();
          broadcastEvent(msg);
          console.log(`[POST] channel=${channel} id=${messageId} type=${message.type || 'unknown'}`);
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ status: "success", id: messageId }));
        } else if (command === "last-msg") {
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ status: "success", id: messageId }));
        } else {
          res.writeHead(400, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ status: "error", code: "bad-command" }));
        }
      } catch (e) {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ status: "error", code: "syntax-error" }));
      }
    });
    return;
  }

  // Long-poll fallback for channels
  if (req.url && req.url.startsWith("/channels/")) {
    const url = new URL(req.url, "http://n");
    const lastMsg = parseInt(url.searchParams.get("last") || "0");
    const channelStr = decodeURI(url.pathname).slice(10);
    const channels = channelStr.split("|");

    if (!channelStr || channels.length === 0 || !channels[0]) {
      res.writeHead(400, { "Content-Type": "application/json" });
      res.end('{"error":"bad request"}');
      return;
    }

    const channelSet = {};
    channels.forEach((c) => (channelSet[c] = true));

    for (const msg of messages) {
      if (msg.id > lastMsg && channelSet[msg.channel]) {
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify(msg));
        return;
      }
    }

    const timeout = setTimeout(() => {
      pollers.delete(cb);
      res.writeHead(504, { "Content-Type": "application/json" });
      res.end('{"error":"timeout"}');
    }, 60000);

    const cb = (msg) => {
      if (msg.id > lastMsg && channelSet[msg.channel]) {
        clearTimeout(timeout);
        pollers.delete(cb);
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify(msg));
        return true;
      }
      return false;
    };
    pollers.add(cb);
    req.on("close", () => {
      clearTimeout(timeout);
      pollers.delete(cb);
    });
    return;
  }

  res.writeHead(404);
  res.end("Not Found");
});

const io = new Server(httpServer, {
  cors: { origin: "*" },
  transports: ["polling", "websocket"],
});

const maxQueue = 50;
let messageId = Date.now();
const messages = [];
const pollers = new Set();

function notifyPollers(msg) {
  for (const cb of pollers) {
    cb(msg);
  }
}

function broadcastEvent(msg) {
  // Emit to specific room (channel) for efficiency
  io.to(msg.channel).emit("event", msg);
  // Also notify long-poll clients
  notifyPollers(msg);
}

io.on("connection", (socket) => {
  console.log(`[Socket.IO] Client connected: ${socket.id}`);
  let subscribedChannels = [];

  socket.on("subscribe", (data) => {
    if (!data || !Array.isArray(data.channels)) return;
    const lastMsg = data.last_msg || 0;

    // Leave old rooms
    subscribedChannels.forEach((ch) => socket.leave(ch));

    // Join new rooms
    subscribedChannels = [];
    data.channels.forEach((ch) => {
      if (typeof ch === "string") {
        socket.join(ch);
        subscribedChannels.push(ch);
      }
    });

    console.log(`[Socket.IO] ${socket.id} rooms:`, subscribedChannels);

    // Send catch-up messages from last_msg
    for (const msg of messages) {
      if (msg.id > lastMsg && subscribedChannels.includes(msg.channel)) {
        socket.emit("event", msg);
      }
    }
  });

  socket.on("disconnect", (reason) => {
    console.log(`[Socket.IO] Client disconnected: ${socket.id} reason=${reason}`);
  });
});

httpServer.listen(PORT, "0.0.0.0", () => {
  console.log(`Socket.IO event daemon listening on port ${PORT}`);
});
