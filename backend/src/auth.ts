/** JWT auth + RBAC middleware (PRD Module A). */
import type { NextFunction, Request, Response } from "express";
import jwt from "jsonwebtoken";
import { config } from "./config.js";
import type { Role } from "./types.js";

export function signAccessToken(payload: { id: string; role: Role; email: string }) {
  const opts: jwt.SignOptions = { expiresIn: config.accessTokenTtl as jwt.SignOptions["expiresIn"] };
  return jwt.sign(payload, config.jwtSecret, opts);
}

export function signRefreshToken(payload: { id: string }) {
  const opts: jwt.SignOptions = { expiresIn: config.refreshTokenTtl as jwt.SignOptions["expiresIn"] };
  return jwt.sign(payload, config.jwtRefreshSecret, opts);
}

export function requireAuth(req: Request, res: Response, next: NextFunction) {
  const header = req.headers.authorization;
  if (!header?.startsWith("Bearer ")) {
    return res.status(401).json({ error: "missing bearer token" });
  }
  try {
    const decoded = jwt.verify(header.slice(7), config.jwtSecret) as {
      id: string;
      role: Role;
      email: string;
    };
    req.user = { id: decoded.id, role: decoded.role, email: decoded.email };
    next();
  } catch {
    res.status(401).json({ error: "invalid or expired token" });
  }
}

/** Restrict a route to the given roles. */
export function requireRole(...roles: Role[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) return res.status(401).json({ error: "unauthenticated" });
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: "insufficient permissions" });
    }
    next();
  };
}
