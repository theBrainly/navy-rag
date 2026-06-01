import { useState } from "react";
import { api, getToken, setToken } from "./api";
import { Login } from "./components/Login";
import { Search } from "./components/Search";
import { Upload } from "./components/Upload";

export function App() {
  const [authed, setAuthed] = useState(Boolean(getToken()));
  const [user, setUser] = useState<{ name: string; role: string } | null>(null);

  async function handleLogin(email: string, password: string) {
    const res = await api.login(email, password);
    setToken(res.accessToken);
    setUser(res.user);
    setAuthed(true);
  }

  function logout() {
    setToken("");
    setAuthed(false);
    setUser(null);
  }

  return (
    <div className="app">
      <h1>Defense Logistics Knowledge Intelligence Platform</h1>
      <p className="subtitle">
        Source-grounded RAG search and deterministic product-code lookup
      </p>

      {!authed ? (
        <Login onLogin={handleLogin} />
      ) : (
        <>
          <div className="panel" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span className="hint">
              Signed in{user ? ` as ${user.name} (${user.role})` : ""}
            </span>
            <button className="secondary" onClick={logout}>
              Sign out
            </button>
          </div>
          <Search />
          <Upload />
        </>
      )}
    </div>
  );
}
