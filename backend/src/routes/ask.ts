import { Router } from "express";
import { ai } from "../aiClient.js";
import { requireAuth } from "../auth.js";
import { store } from "../store.js";

export const askRouter = Router();
askRouter.use(requireAuth);

askRouter.post("/", async (req, res) => {
  const { question, topK } = req.body ?? {};
  if (!question) return res.status(400).json({ error: "missing question" });
  store.searchLogs.push({
    query: question,
    type: "ask",
    userId: req.user?.email ?? "anon",
    timestamp: new Date().toISOString(),
  });
  res.json(await ai.ask(question, topK));
});
