import dotenv from "dotenv";

// Single source of truth: the root .env (one level up from backend/).
dotenv.config({ path: "../.env" });
dotenv.config(); // fallback to a local backend/.env if one exists

export const config = {
  port: Number(process.env.PORT ?? 4000),
  jwtSecret: process.env.JWT_SECRET ?? "change-me-in-production",
  jwtRefreshSecret: process.env.JWT_REFRESH_SECRET ?? "change-me-too",
  aiServiceUrl: process.env.AI_SERVICE_URL ?? "http://localhost:8000",
  deploymentMode: process.env.DEPLOYMENT_MODE ?? "cloud",
  storageProvider: process.env.STORAGE_PROVIDER ?? "memory",
  accessTokenTtl: "15m",
  refreshTokenTtl: "7d",
};
