import { Router } from "express";
import { requireAuth, requireRole } from "../auth.js";
import { store } from "../store.js";

export const analyticsRouter = Router();
analyticsRouter.use(requireAuth);

analyticsRouter.get("/", requireRole("admin", "manager"), (_req, res) => {
  const topQueries = Object.entries(
    store.searchLogs.reduce<Record<string, number>>((acc, l) => {
      acc[l.query] = (acc[l.query] ?? 0) + 1;
      return acc;
    }, {}),
  )
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([query, count]) => ({ query, count }));

  res.json({
    totalDocuments: store.documents.length,
    totalChunks: store.documents.reduce((s, d) => s + d.chunksCreated, 0),
    totalCodesIndexed: store.documents.reduce((s, d) => s + d.codesIndexed, 0),
    searchVolume: store.searchLogs.length,
    processedDocuments: store.documents.filter((d) => d.status === "processed").length,
    failedDocuments: store.documents.filter((d) => d.status === "failed").length,
    topQueries,
  });
});

// Audit log — Admin only (PRD Module N).
analyticsRouter.get("/audit", requireRole("admin"), (_req, res) => {
  res.json(store.audit);
});
