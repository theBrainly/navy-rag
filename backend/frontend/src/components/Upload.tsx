import { useState } from "react";
import { api } from "../api";

export function Upload() {
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState<any>(null);
  const [busy, setBusy] = useState(false);

  async function submit() {
    if (!title.trim() || !text.trim()) return;
    setError("");
    setResult(null);
    setBusy(true);
    try {
      setResult(await api.upload(title, text));
      setText("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "upload failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="panel">
      <strong>Upload document</strong>
      <p className="hint">Admin and Manager roles only. Paste catalog/manual text to index it.</p>
      <label>Title</label>
      <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Equipment Catalog 2025" />
      <label>Content</label>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Product code DDR333 is categorized as Football Equipment…"
      />
      <button disabled={busy} onClick={submit}>
        {busy ? "Processing…" : "Upload & index"}
      </button>
      {error && <p className="error">{error}</p>}
      {result && (
        <p className="hint">
          Indexed “{result.title}” — {result.chunksCreated} chunks, {result.codesIndexed} codes.
        </p>
      )}
    </div>
  );
}
