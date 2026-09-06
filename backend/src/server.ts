import { createServer, type IncomingMessage, type ServerResponse } from "node:http";

type CartRequestItem = { productId: number; quantity: number };

const products = [
  { id: 1, name: "계란 (10구)", price: 3200, ingredients: ["계란"] },
  { id: 2, name: "두부 (300g)", price: 1800, ingredients: ["두부"] },
  { id: 3, name: "대파 (1단)", price: 2500, ingredients: ["대파"] },
];

const recipes = [
  { id: 1, name: "계란볶음밥", ingredients: ["계란", "대파", "밥", "간장"], time: "10분" },
  { id: 2, name: "순두부찌개", ingredients: ["두부", "계란", "고춧가루", "멸치육수", "애호박"], time: "20분" },
  { id: 3, name: "파계란탕", ingredients: ["계란", "대파", "소금", "참기름"], time: "8분" },
];

function sendJson(response: ServerResponse, status: number, body: unknown) {
  response.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*",
  });
  response.end(JSON.stringify(body));
}

async function readBody(request: IncomingMessage): Promise<string> {
  const chunks: Buffer[] = [];
  for await (const chunk of request) chunks.push(Buffer.from(chunk));
  return Buffer.concat(chunks).toString("utf8");
}

const server = createServer(async (request, response) => {
  const url = new URL(request.url ?? "/", `http://${request.headers.host ?? "localhost"}`);

  if (request.method === "OPTIONS") {
    response.writeHead(204, { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type" });
    response.end();
    return;
  }

  if (request.method === "GET" && url.pathname === "/api/health") {
    sendJson(response, 200, { ok: true, service: "oneul-mwo-damji-backend" });
    return;
  }

  if (request.method === "GET" && url.pathname === "/api/products") {
    sendJson(response, 200, { products });
    return;
  }

  if (request.method === "POST" && url.pathname === "/api/cart/estimate") {
    try {
      const body = JSON.parse(await readBody(request)) as { items?: CartRequestItem[] };
      const items = body.items ?? [];
      const total = items.reduce((sum, item) => {
        const product = products.find((candidate) => candidate.id === item.productId);
        return sum + (product?.price ?? 0) * Math.max(0, item.quantity);
      }, 0);
      sendJson(response, 200, { total, itemCount: items.reduce((sum, item) => sum + Math.max(0, item.quantity), 0) });
    } catch {
      sendJson(response, 400, { message: "요청 형식이 올바르지 않습니다." });
    }
    return;
  }

  if (request.method === "GET" && url.pathname === "/api/recipes") {
    const owned = new Set((url.searchParams.get("ingredients") ?? "").split(",").filter(Boolean));
    const recommendations = recipes
      .map((recipe) => ({
        ...recipe,
        matched: recipe.ingredients.filter((ingredient) => owned.has(ingredient)),
        missing: recipe.ingredients.filter((ingredient) => !owned.has(ingredient)),
      }))
      .sort((a, b) => b.matched.length - a.matched.length);
    sendJson(response, 200, { recipes: recommendations });
    return;
  }

  sendJson(response, 404, { message: "요청한 API를 찾을 수 없습니다." });
});

const port = Number(process.env.PORT ?? 4000);
server.listen(port, () => console.log(`Backend listening on http://localhost:${port}`));
