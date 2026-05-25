import bcrypt from "bcryptjs";
import { Router } from "express";
import jwt from "jsonwebtoken";
import { signAccessToken, signRefreshToken } from "../auth.js";
import { config } from "../config.js";
import { store } from "../store.js";

export const authRouter = Router();

authRouter.post("/login", (req, res) => {
  const { email, password } = req.body ?? {};
  const user = email ? store.findUserByEmail(email) : undefined;
  if (!user || !bcrypt.compareSync(password ?? "", user.passwordHash)) {
    return res.status(401).json({ error: "invalid credentials" });
  }
  store.log({
    actor: user.email,
    action: "login",
    target: "-",
    ip: req.ip ?? "",
    timestamp: new Date().toISOString(),
  });
  res.json({
    accessToken: signAccessToken({ id: user.id, role: user.role, email: user.email }),
    refreshToken: signRefreshToken({ id: user.id }),
    user: { id: user.id, name: user.name, email: user.email, role: user.role },
  });
});

authRouter.post("/refresh", (req, res) => {
  const { refreshToken } = req.body ?? {};
  if (!refreshToken) return res.status(400).json({ error: "missing refreshToken" });
  try {
    const decoded = jwt.verify(refreshToken, config.jwtRefreshSecret) as { id: string };
    const user = store.users.find((u) => u.id === decoded.id);
    if (!user) return res.status(401).json({ error: "unknown user" });
    res.json({
      accessToken: signAccessToken({ id: user.id, role: user.role, email: user.email }),
    });
  } catch {
    res.status(401).json({ error: "invalid refresh token" });
  }
});
