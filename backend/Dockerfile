FROM node:22-slim

WORKDIR /app

# Backend deps
COPY package.json ./
RUN npm install

# Frontend deps (separate layer for caching)
COPY frontend/package.json ./frontend/package.json
RUN npm --prefix frontend install

# Sources
COPY tsconfig.json ./
COPY src ./src
COPY frontend ./frontend

# Builds the React app into frontend/dist, then compiles the gateway
RUN npm run build

EXPOSE 4000
CMD ["node", "dist/index.js"]
