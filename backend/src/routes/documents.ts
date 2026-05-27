import { createHash, randomUUID } from "node:crypto";
import { Router } from "express";
import multer from "multer";
import { ai } from "../aiClient.js";
import { requireAuth, requireRole } from "../auth.js";
import { store } from "../store.js";
import type { DocumentRecord } from "../types.js";

export const documentsRouter = Router();
const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 25 * 1024 * 1024 } });

documentsRouter.use(requireAuth);

/**
 * Upload a document. Admin and Manager only (PRD Module B).
 * For this skeleton we accept a text file (or a `text` field) and forward it to
 * the AI service for extraction/chunking/embedding/code-indexing. A production
 * build would push binaries to Cloudinary/MinIO and run OCR (Module D).
 */
documentsRouter.post(
  "/",
  requireRole("admin", "manager"),
  upload.single("file"),
  async (req, res) => {
    const title = req.body?.title ?? req.file?.originalname ?? "Untitled";
    const text = req.file ? req.file.buffer.toString("utf-8") : req.body?.text;
    if (!text || !text.trim()) {
      return res.status(400).json({ error: "provide a text file or a `text` field" });
    }

    const sha256 = createHash("sha256").update(text).digest("hex");
    const existing = store.findDocBySha(sha256);
    if (existing) {
      // Exact duplicate detection (PRD Module K).
      return res.status(409).json({ error: "duplicate document", existing });
    }

    const id = randomUUID();
    const doc: DocumentRecord = {
      id,
      title,
      fileType: req.file?.mimetype ?? "text/plain",
      sha256,
      uploadedBy: req.user!.email,
      status: "pending",
      chunksCreated: 0,
      codesIndexed: 0,
      createdAt: new Date().toISOString(),
    };
    store.addDocument(doc);

    try {
      const result = await ai.process(id, title, text);
      doc.status = "processed";
      doc.chunksCreated = result.chunks_created;
      doc.codesIndexed = result.codes_indexed;
    } catch (err) {
      doc.status = "failed";
      return res.status(502).json({ error: "AI processing failed", detail: String(err) });
    }

    store.log({
      actor: req.user!.email,
      action: "upload",
      target: id,
      ip: req.ip ?? "",
      timestamp: new Date().toISOString(),
    });
    res.status(201).json(doc);
  },
);

documentsRouter.get("/", (_req, res) => {
  res.json(store.documents);
});

documentsRouter.get("/:id", (req, res) => {
  const doc = store.documents.find((d) => d.id === req.params.id);
  if (!doc) return res.status(404).json({ error: "not found" });
  res.json(doc);
});
