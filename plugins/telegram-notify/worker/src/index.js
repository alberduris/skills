export default {
  // HTTP endpoint: schedule a message
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204 });
    }

    // Auth check
    const auth = request.headers.get("Authorization");
    if (auth !== `Bearer ${env.API_TOKEN}`) {
      return Response.json({ error: "unauthorized" }, { status: 401 });
    }

    const url = new URL(request.url);

    // POST /schedule — add a message to the queue
    if (request.method === "POST" && url.pathname === "/schedule") {
      const body = await request.json();
      const { text, send_at } = body;

      if (!text || !send_at) {
        return Response.json(
          { error: "missing 'text' and/or 'send_at' (ISO 8601)" },
          { status: 400 }
        );
      }

      const id = crypto.randomUUID();
      await env.QUEUE.put(id, JSON.stringify({ text, send_at }));

      return Response.json({ ok: true, id, text, send_at });
    }

    // GET /list — show pending messages
    if (request.method === "GET" && url.pathname === "/list") {
      const keys = await env.QUEUE.list();
      const items = await Promise.all(
        keys.keys.map(async (k) => {
          const val = await env.QUEUE.get(k.name);
          return { id: k.name, ...JSON.parse(val) };
        })
      );
      return Response.json({ pending: items });
    }

    // DELETE /cancel/:id — remove a scheduled message
    if (request.method === "DELETE" && url.pathname.startsWith("/cancel/")) {
      const id = url.pathname.replace("/cancel/", "");
      await env.QUEUE.delete(id);
      return Response.json({ ok: true, deleted: id });
    }

    // POST /send — send immediately (bypass queue)
    if (request.method === "POST" && url.pathname === "/send") {
      const body = await request.json();
      const { text } = body;
      if (!text) {
        return Response.json({ error: "missing 'text'" }, { status: 400 });
      }
      const result = await sendTelegram(env, text);
      return Response.json(result);
    }

    return Response.json({ error: "not found" }, { status: 404 });
  },

  // Cron trigger: check queue and send due messages
  async scheduled(event, env, ctx) {
    const now = new Date();
    const keys = await env.QUEUE.list();

    for (const key of keys.keys) {
      const raw = await env.QUEUE.get(key.name);
      if (!raw) continue;

      const { text, send_at } = JSON.parse(raw);
      const sendTime = new Date(send_at);

      if (sendTime <= now) {
        await sendTelegram(env, text);
        await env.QUEUE.delete(key.name);
      }
    }
  },
};

async function sendTelegram(env, text) {
  const url = `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: env.TELEGRAM_CHAT_ID,
      text: text,
    }),
  });
  return res.json();
}
