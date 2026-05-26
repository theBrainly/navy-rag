/**
 * In-memory data store (PRD Section 8). Swap for MongoDB in production by
 * implementing the same methods against collections.
 */
import bcrypt from "bcryptjs";
import { randomUUID } from "node:crypto";
import type { AuditEntry, DocumentRecord, Role, User } from "./types.js";

class Store {
  users: User[] = [];
  documents: DocumentRecord[] = [];
  audit: AuditEntry[] = [];
  searchLogs: { query: string; type: string; userId: string; timestamp: string }[] = [];

  seedUsers() {
    if (this.users.length) return;
    const seed: Array<[string, string, Role]> = [
      ["admin@dlkip.mil", "admin123", "admin"],
      ["manager@dlkip.mil", "manager123", "manager"],
      ["officer@dlkip.mil", "officer123", "officer"],
      ["viewer@dlkip.mil", "viewer123", "viewer"],
    ];
    for (const [email, pw, role] of seed) {
      this.users.push({
        id: randomUUID(),
        name: role[0].toUpperCase() + role.slice(1),
        email,
        role,
        passwordHash: bcrypt.hashSync(pw, 10),
      });
    }
  }

  findUserByEmail(email: string) {
    return this.users.find((u) => u.email === email);
  }

  addDocument(doc: DocumentRecord) {
    this.documents.push(doc);
  }

  findDocBySha(sha: string) {
    return this.documents.find((d) => d.sha256 === sha);
  }

  log(entry: AuditEntry) {
    this.audit.push(entry);
  }
}

export const store = new Store();
store.seedUsers();
