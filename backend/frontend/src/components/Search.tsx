import { useState } from "react";
import { api } from "../api";

type Mode = "ask" | "code";

export function Search() {
  const [mode, setMode] = useState<Mode>("ask");
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [ask, setAsk] = useState<any>(null);
  const [code, setCode] = useState<any>(null);

  async function run() {
    if (!query.trim()) return;
    setError("");
    setBusy(true);
    setAsk(null);
    setCode(null);
    try {
      if (mode === "ask") setAsk(await api.ask(query));
      else setCode(await api.codeLookup(query));
    } catch (err) {
      setError(err instanceof Error ? err.message : "request failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="panel">
      <div className="tabs">
        <button className={mode === "ask" ? "active" : ""} onClick={() => setMode("ask")}>
          Ask (RAG)
        </button>
        <button className={mode === "code" ? "active" : ""} onClick={() => setMode("code")}>
          Exact code lookup
        </button>
      </div>

      <div className="row">
        <div>
          <label>{mode === "ask" ? "Question" : "Product code"}</label>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && run()}
            placeholder={mode === "ask" ? "What is DDR333 used for?" : "DDR333"}
          />
        </div>
        <button disabled={busy} onClick={run}>
          {busy ? "Searching…" : "Search"}
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      {ask && (
        <div>
          {ask.found ? (
            <>
              <p className="answer">{ask.answer}</p>
              <p className="confidence">Confidence: {(ask.confidence * 100).toFixed(0)}%</p>
              <strong>Sources</strong>
              {ask.sources.map((s: any, i: number) => (
                <div className="source" key={i}>
                  <span className="badge">page {s.page_number}</span>
                  {s.title}
                </div>
              ))}
            </>
          ) : (
            <p className="answer">{ask.answer}</p>
          )}
        </div>
      )}

      {code && (
        <div>
          <p>
            <span className="badge">{code.code}</span>
            {code.total_matches} match(es) across {code.documents} document(s)
          </p>
          {code.records.map((r: any, i: number) => (
            <div className="record" key={i}>
              <span className="badge">page {r.page_number}</span>
              <strong>{r.title}</strong>
              <div className="hint">{r.context}</div>
            </div>
          ))}
          {code.total_matches === 0 && <p className="hint">No records found for this code.</p>}
        </div>
      )}
    </div>
  );
}
