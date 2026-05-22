import cors from "cors";
import express from "express";
import { existsSync } from "node:fs";
import path from "node:path";
import { ai } from "./aiClient.js";
import { config } from "./config.js";
import { analyticsRouter } from "./routes/analytics.js";
import { askRouter } from "./routes/ask.js";
import { authRouter } from "./routes/auth.js";
import { documentsRouter } from "./routes/documents.js";
import { searchRouter } from "./routes/search.js";

const app = express();
app.use(cors());
app.use(express.json({ limit: "10mb" }));

app.get("/health", async (_req, res) => {
  let aiStatus: unknown = "unreachable";
  try {
    aiStatus = await ai.health();
  } catch {
    /* AI service may be down */
  }
  res.json({ status: "ok", deploymentMode: config.deploymentMode, ai: aiStatus });
});

app.use("/api/auth", authRouter);
app.use("/api/documents", documentsRouter);
app.use("/api/search", searchRouter);
app.use("/api/ask", askRouter);
app.use("/api/analytics", analyticsRouter);

// ── Serve the built React frontend (single-service deployment) ──────
// The frontend lives at backend/frontend and builds to frontend/dist.
const frontendDist = path.resolve(process.cwd(), "frontend", "dist");
if (existsSync(frontendDist)) {
  app.use(express.static(frontendDist));
  // SPA fallback: any non-API GET returns index.html so client routing works.
  app.get(/^\/(?!api\/).*/, (_req, res) => {
    res.sendFile(path.join(frontendDist, "index.html"));
  });
  console.log(`Serving frontend from ${frontendDist}`);
} else {
  console.warn(
    `Frontend build not found at ${frontendDist}. Run "npm run build:frontend" to enable the UI.`,
  );
}

// Centralized error handler.
app.use(
  (err: unknown, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
    console.error(err);
    res.status(500).json({ error: "internal server error" });
  },
);

app.listen(config.port, () => {
  console.log(`DLKIP gateway listening on :${config.port} (mode=${config.deploymentMode})`);
  console.log(`Proxying AI service at ${config.aiServiceUrl}`);
});

export { app };
