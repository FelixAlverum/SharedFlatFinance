# ==========================================
# STUFE 1: Build (Bauen der Anwendung)
# ==========================================
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# ==========================================
# STUFE 2: Produktion (Das finale Image)
# ==========================================
FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY --from=builder /app/build ./build

ENV NODE_ENV=production
ENV PORT=3000

# WICHTIG: Wenn du die App später auf einer echten Domain (z.B. wg-kasse.de) hostest,
# musst du den ORIGIN setzen, sonst blockiert SvelteKit aus Sicherheitsgründen (CSRF) den Login.
# ENV ORIGIN=https://deine-domain.de

EXPOSE 3000
USER node

CMD ["node", "build/index.js"]