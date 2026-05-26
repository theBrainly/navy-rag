/** Typed client for the Python AI service (PRD Section 7). */
import axios from "axios";
import { config } from "./config.js";

const client = axios.create({ baseURL: config.aiServiceUrl, timeout: 60_000 });

export interface ProcessResult {
  document_id: string;
  chunks_created: number;
  codes_indexed: number;
}

export const ai = {
  async process(documentId: string, title: string, text: string): Promise<ProcessResult> {
    const { data } = await client.post("/process", {
      document_id: documentId,
      title,
      text,
    });
    return data;
  },

  async search(query: string, topK?: number) {
    const { data } = await client.post("/search", { query, top_k: topK });
    return data;
  },

  async codeLookup(code: string) {
    const { data } = await client.post("/code-lookup", { code });
    return data;
  },

  async ask(question: string, topK?: number) {
    const { data } = await client.post("/ask", { question, top_k: topK });
    return data;
  },

  async health() {
    const { data } = await client.get("/health");
    return data;
  },
};
