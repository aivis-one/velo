# =============================================================================
# VELO Frontend -- Dockerfile
# =============================================================================
#
# MULTI-STAGE BUILD:
#   Stage 1 ("builder"): npm ci + npm run build -> produces dist/
#   Stage 2 ("runtime"): nginx serves dist/ as static files
#
# Internal Nginx handles SPA fallback (all routes -> index.html).
# External Nginx on the host handles SSL + routing between services.
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Build
# ---------------------------------------------------------------------------
FROM node:22-alpine AS builder

WORKDIR /app

# Install dependencies first (cached unless package*.json change).
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source and build.
COPY . .
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2: Serve with Nginx
# ---------------------------------------------------------------------------
FROM nginx:alpine AS runtime

# Remove default nginx site.
RUN rm -f /etc/nginx/conf.d/default.conf

# Copy our nginx config.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built static files from builder.
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
