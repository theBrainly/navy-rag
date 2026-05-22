export type Role = "admin" | "manager" | "officer" | "viewer";

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
  passwordHash: string;
}

export interface DocumentRecord {
  id: string;
  title: string;
  fileType: string;
  sha256: string;
  uploadedBy: string;
  status: "pending" | "processed" | "failed";
  chunksCreated: number;
  codesIndexed: number;
  createdAt: string;
}

export interface AuditEntry {
  actor: string;
  action: string;
  target: string;
  ip: string;
  timestamp: string;
}

declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace Express {
    interface Request {
      user?: { id: string; role: Role; email: string };
    }
  }
}
