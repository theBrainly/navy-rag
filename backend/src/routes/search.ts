import { Router } from "express";
import { ai } from "../aiClient.js";
import { requireAuth } from "../auth.js";
import { store } from "../store.js";

export const searchRouter = Router();
searchRouter.use(requireAuth);

function logSearch(req: any, type: string, query: string) {
  store.searchLogs.push({
    query,
    type,
    userId: req.user?.email ?? "anon",
    timestamp: new Date().toISOString(),
  });
}

searchRouter.post("/semantic", async (req, res) => {
  const { query, topK } = req.body ?? {};
  if (!query) return res.status(400).json({ error: "missing query" });
  logSearch(req, "semantic", query);
  res.json(await ai.search(query, topK));
});

searchRouter.post("/code", async (req, res) => {
  const { code } = req.body ?? {};
  if (!code) return res.status(400).json({ error: "missing code" });
  logSearch(req, "code", code);
  res.json(await ai.codeLookup(code));
});

searchRouter.post("/hybrid", async (req, res) => {
  // The AI service routes code-like queries to the exact index automatically.
  const { query, topK } = req.body ?? {};
  if (!query) return res.status(400).json({ error: "missing query" });
  logSearch(req, "hybrid", query);
  res.json(await ai.search(query, topK));
});
