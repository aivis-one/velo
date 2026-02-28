#!/bin/bash

# ==============================================================================
# VELO Platform — VPS Installation & Management Script
# ==============================================================================
#
# WHAT THIS SCRIPT DOES:
#   1. Installs system dependencies (Docker, Nginx, Certbot, UFW)
#   2. Creates a deploy user (not root)
#   3. Sets up SSH deploy key for GitHub
#   4. Clones the repository
#   5. Generates secure .env with random passwords
#   6. Configures Nginx reverse proxy + SSL
#   7. Starts the Docker stack (app + postgres + redis)
#   8. Creates "velo" management command
#
# USAGE:
#   First time:   bash install_velo.sh
#   After that:   velo status | velo logs | velo update | ...
#
# REQUIREMENTS:
#   - Ubuntu 22.04+ (fresh VPS)
#   - Root access
#   - Domain pointing to this server (api.talentir.info)
# ==============================================================================

# === Configuration ===
INSTALL_BASE="/opt/velo"
DOMAIN="api.talentir.info"
REPO_URL=""  # Set after SSH key setup
GITHUB_REPO="inzoddwetrust/velo"
DEPLOY_USER="velo"
DOCKER_COMPOSE_FILE="docker-compose.yml"

# === Colors ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# === Logging ===
log()     { echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; }
info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }

# === Error handler ===
handle_error() {
    error "Error occurred at line: ${1}"
    error "Installation failed. Check output above for details."
    exit 1
}
trap 'handle_error ${LINENO}' ERR

# === Check root ===
if [ "$EUID" -ne 0 ]; then
    error "Please run as root: sudo bash install_velo.sh"
    exit 1
fi

# ==============================================================================
# PRE-FLIGHT CHECKS
# ==============================================================================

preflight_checks() {
    log "Running pre-flight checks..."

    # Check OS
    if [ ! -f /etc/os-release ]; then
        error "Cannot detect OS. Ubuntu 22.04+ required."
        exit 1
    fi

    source /etc/os-release
    if [ "$ID" != "ubuntu" ] && [ "$ID" != "debian" ]; then
        warn "Detected $ID, expected Ubuntu/Debian. Proceeding anyway..."
    fi

    # Check memory (warn if < 2GB)
    local TOTAL_MEM=$(free -m | awk '/Mem:/ {print $2}')
    if [ "$TOTAL_MEM" -lt 2000 ]; then
        warn "Only ${TOTAL_MEM}MB RAM detected. Recommended: 2GB+"
    else
        success "Memory: ${TOTAL_MEM}MB ✓"
    fi

    # Check disk (warn if < 10GB free)
    local FREE_DISK=$(df -BG /opt | tail -1 | awk '{print $4}' | tr -d 'G')
    if [ "$FREE_DISK" -lt 10 ]; then
        warn "Only ${FREE_DISK}GB free disk. Recommended: 10GB+"
    else
        success "Disk: ${FREE_DISK}GB free ✓"
    fi

    # Check DNS
    local RESOLVED_IP=$(dig +short "$DOMAIN" 2>/dev/null | tail -1)
    local SERVER_IP=$(curl -s ifconfig.me 2>/dev/null)

    if [ -z "$RESOLVED_IP" ]; then
        warn "$DOMAIN does not resolve. SSL setup may fail."
    elif [ "$RESOLVED_IP" != "$SERVER_IP" ]; then
        warn "$DOMAIN → $RESOLVED_IP (this server is $SERVER_IP). SSL setup may fail."
    else
        success "DNS: $DOMAIN → $RESOLVED_IP ✓"
    fi

    success "Pre-flight checks passed"
}

clear
echo -e "${CYAN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║       VELO Platform — VPS Installation        ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════╝${NC}"
echo ""

preflight_checks
echo ""

# Check for previous installation
if [ -d "$INSTALL_BASE/repo" ]; then
    warn "Found existing installation at $INSTALL_BASE"
    echo ""
    read -p "Remove existing installation and start fresh? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "Stopping existing services and removing volumes..."
        cd "$INSTALL_BASE/repo" 2>/dev/null && docker compose down -v 2>/dev/null || true
        cd "$INSTALL_BASE"
        log "Removing existing installation..."
        rm -rf "$INSTALL_BASE/repo"
        rm -f /usr/local/bin/velo
        success "Previous installation removed (including Docker volumes)"
    else
        error "Cannot proceed with existing installation"
        exit 1
    fi
fi

# ==============================================================================
# FIX LOCALE
# ==============================================================================

fix_locale() {
    log "Fixing locale settings..."

    apt-get update -qq
    apt-get install -y -qq locales > /dev/null

    locale-gen en_US.UTF-8 > /dev/null 2>&1
    update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

    export LANG=en_US.UTF-8
    export LC_ALL=en_US.UTF-8

    success "Locale configured"
}

fix_locale

# ==============================================================================
# SYSTEM DEPENDENCIES
# ==============================================================================

install_system_deps() {
    log "Installing system dependencies..."

    apt-get update
    apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        git \
        ufw \
        dnsutils \
        software-properties-common

    success "System dependencies installed"
}

install_system_deps

# ==============================================================================
# DOCKER
# ==============================================================================

install_docker() {
    if command -v docker &> /dev/null; then
        success "Docker already installed: $(docker --version)"
        return
    fi

    log "Installing Docker..."

    # Add Docker GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc

    # Add Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Enable and start Docker
    systemctl enable docker
    systemctl start docker

    success "Docker installed: $(docker --version)"
}

install_docker

# ==============================================================================
# NGINX + CERTBOT
# ==============================================================================

install_nginx() {
    if command -v nginx &> /dev/null; then
        success "Nginx already installed: $(nginx -v 2>&1)"
        return
    fi

    log "Installing Nginx..."
    apt-get install -y nginx

    systemctl enable nginx
    systemctl start nginx

    success "Nginx installed"
}

install_certbot() {
    if command -v certbot &> /dev/null; then
        success "Certbot already installed"
        return
    fi

    log "Installing Certbot..."
    apt-get install -y certbot python3-certbot-nginx

    success "Certbot installed"
}

install_nginx
install_certbot

# ==============================================================================
# FIREWALL
# ==============================================================================

setup_firewall() {
    log "Configuring firewall (UFW)..."

    ufw default deny incoming
    ufw default allow outgoing
    ufw allow 22/tcp    # SSH
    ufw allow 80/tcp    # HTTP (for certbot + redirect)
    ufw allow 443/tcp   # HTTPS

    # Enable without prompt
    echo "y" | ufw enable

    success "Firewall configured (SSH + HTTP + HTTPS only)"
}

setup_firewall

# ==============================================================================
# DEPLOY USER
# ==============================================================================

setup_deploy_user() {
    if id "$DEPLOY_USER" &>/dev/null; then
        success "User '$DEPLOY_USER' already exists"
    else
        log "Creating deploy user '$DEPLOY_USER'..."
        useradd -m -s /bin/bash "$DEPLOY_USER"
        success "User '$DEPLOY_USER' created"
    fi

    # Add to docker group
    usermod -aG docker "$DEPLOY_USER"
    success "User '$DEPLOY_USER' added to docker group"
}

setup_deploy_user

# ==============================================================================
# SSH SETUP FOR GITHUB
# ==============================================================================

setup_ssh() {
    log "Setting up SSH for GitHub..."

    DEPLOY_KEY="/root/.ssh/id_ed25519_velo_deploy"

    # Add GitHub to known hosts
    mkdir -p /root/.ssh
    chmod 700 /root/.ssh
    if ! grep -q "github.com" /root/.ssh/known_hosts 2>/dev/null; then
        ssh-keyscan -H github.com >> /root/.ssh/known_hosts 2>/dev/null
    fi

    # Generate deploy key if not exists
    if [ ! -f "$DEPLOY_KEY" ]; then
        ssh-keygen -t ed25519 -C "velo-deploy@$(hostname)" -f "$DEPLOY_KEY" -N ""
        success "Deploy key generated"
    else
        success "Deploy key already exists"
    fi

    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  GitHub Deploy Key (add to repo settings)${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
    echo ""
    cat "${DEPLOY_KEY}.pub"
    echo ""
    echo -e "${YELLOW}Go to: https://github.com/$GITHUB_REPO/settings/keys${NC}"
    echo -e "${YELLOW}Click 'Add deploy key', paste the key above.${NC}"
    echo ""
    read -p "Press ENTER after adding the deploy key to GitHub..."

    # Configure SSH to use this key for GitHub
    if ! grep -q "Host github.com-velo" /root/.ssh/config 2>/dev/null; then
        cat >> /root/.ssh/config << EOF

# VELO Deploy Key
Host github.com-velo
    HostName github.com
    User git
    IdentityFile $DEPLOY_KEY
    IdentitiesOnly yes
EOF
        chmod 600 /root/.ssh/config
    fi

    REPO_URL="git@github.com-velo:$GITHUB_REPO.git"

    # Test connection
    log "Testing GitHub connection..."
    if ssh -T git@github.com-velo 2>&1 | grep -q "successfully authenticated"; then
        success "GitHub connection OK"
    else
        error "Cannot connect to GitHub"
        error "Make sure the deploy key is added to: https://github.com/$GITHUB_REPO/settings/keys"
        return 1
    fi
}

setup_ssh

# ==============================================================================
# CLONE REPOSITORY
# ==============================================================================

clone_repo() {
    log "Cloning repository..."

    mkdir -p "$INSTALL_BASE"
    git clone "$REPO_URL" "$INSTALL_BASE/repo"

    # Set ownership
    chown -R root:root "$INSTALL_BASE"

    success "Repository cloned to $INSTALL_BASE/repo"
}

clone_repo

# ==============================================================================
# GENERATE .ENV
# ==============================================================================

generate_env() {
    local ENV_FILE="$INSTALL_BASE/repo/backend/.env"

    log "Generating .env with secure passwords..."

    # Generate secure random values
    local PG_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    local REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    local SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")

    # Ask for Telegram bot token
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  Telegram Bot Token${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}Get it from @BotFather in Telegram.${NC}"
    echo -e "${YELLOW}Leave empty to skip (you can add it later in .env).${NC}"
    echo ""
    read -p "TELEGRAM_BOT_TOKEN: " TELEGRAM_BOT_TOKEN
    echo ""

    cat > "$ENV_FILE" << EOF
# ===========================================================================
# VELO Backend — Production Environment
# Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
# Server: $(hostname) ($(curl -s ifconfig.me 2>/dev/null))
# ===========================================================================

# --- Application ---
APP_ENV=production
LOG_LEVEL=INFO

# --- Security ---
# Auto-generated. NEVER commit this file.
SECRET_KEY=${SECRET_KEY}

# --- Database (PostgreSQL) ---
# Credentials match POSTGRES_* vars used by Docker to create the DB.
DATABASE_URL=postgresql+asyncpg://velo:${PG_PASSWORD}@postgres:5432/velo
POSTGRES_DB=velo
POSTGRES_USER=velo
POSTGRES_PASSWORD=${PG_PASSWORD}

# --- Redis ---
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
REDIS_PASSWORD=${REDIS_PASSWORD}

# --- CORS ---
CORS_ORIGINS=*

# --- Telegram ---
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}

# --- Session ---
SESSION_TTL_DAYS=30

# --- Stripe (placeholders) ---
STRIPE_SECRET_KEY=TEST
STRIPE_WEBHOOK_SECRET=TEST
STRIPE_PUBLISHABLE_KEY=TEST
STRIPE_SUCCESS_URL=TEST
STRIPE_CANCEL_URL=TEST
EOF

    chmod 600 "$ENV_FILE"
    success ".env generated with secure passwords"
}

generate_env

# ==============================================================================
# NGINX CONFIG
# ==============================================================================

setup_nginx() {
    log "Configuring Nginx reverse proxy..."

    cat > /etc/nginx/sites-available/velo << 'NGINX_EOF'
# VELO — Nginx reverse proxy
# HTTP → backend (API) + frontend (SPA)

server {
    listen 80;
    server_name api.talentir.info;

    # Certbot challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # API routes → backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    location /ready {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    # Everything else → frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX_EOF

    # Enable site
    ln -sf /etc/nginx/sites-available/velo /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default

    # Create certbot webroot
    mkdir -p /var/www/certbot

    # Test and reload
    nginx -t
    systemctl reload nginx

    success "Nginx configured"
}

# ==============================================================================
# SSL CERTIFICATE
# ==============================================================================

setup_ssl() {
    log "Setting up SSL certificate..."

    # Try to get certificate
    if certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        -d "$DOMAIN" \
        --non-interactive \
        --agree-tos \
        --email "admin@$DOMAIN" \
        --no-eff-email; then

        success "SSL certificate obtained"

        # Update nginx config with SSL
        cat > /etc/nginx/sites-available/velo << 'SSL_NGINX_EOF'
# VELO — Nginx reverse proxy with SSL

# HTTP → redirect to HTTPS
server {
    listen 80;
    server_name api.talentir.info;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS
server {
    listen 443 ssl http2;
    server_name api.talentir.info;

    ssl_certificate /etc/letsencrypt/live/api.talentir.info/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.talentir.info/privkey.pem;

    # Modern SSL config
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # HSTS (optional — uncomment after testing)
    # add_header Strict-Transport-Security "max-age=63072000" always;

    # API routes → backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    location /ready {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    # Everything else → frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
SSL_NGINX_EOF

        nginx -t && systemctl reload nginx
        success "Nginx updated with SSL"

        # Auto-renewal cron
        if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
            (crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -
            success "SSL auto-renewal cron added (daily at 3 AM)"
        fi
    else
        error "SSL certificate failed. You can retry later with:"
        error "  certbot certonly --webroot --webroot-path=/var/www/certbot -d $DOMAIN"
        warn "Keeping HTTP-only config for now"
    fi
}

setup_nginx
setup_ssl

# ==============================================================================
# START DOCKER STACK
# ==============================================================================

start_stack() {
    log "Starting VELO Docker stack..."

    cd "$INSTALL_BASE/repo"

    # Build and start
    docker compose build --no-cache app frontend
    docker compose up -d

    # Wait for health
    log "Waiting for services to become healthy..."
    sleep 10

    # Check health
    local HEALTH_URL="http://127.0.0.1:8000/health"
    local RETRIES=12  # 12 x 5s = 60s max

    for i in $(seq 1 $RETRIES); do
        if curl -s "$HEALTH_URL" | grep -q '"status"'; then
            success "VELO API is running!"
            echo ""
            info "Health check response:"
            curl -s "$HEALTH_URL" | python3 -m json.tool 2>/dev/null || curl -s "$HEALTH_URL"
            echo ""
            return 0
        fi
        echo -n "."
        sleep 5
    done

    error "API did not respond within 60s"
    warn "Check logs: docker compose -f $INSTALL_BASE/repo/docker-compose.yml logs"
    return 1
}

start_stack

# ==============================================================================
# MANAGEMENT SCRIPT
# ==============================================================================

create_management_script() {
    log "Creating management script..."

    cat > "$INSTALL_BASE/scripts/manage.sh" << 'MANAGE_EOF'
#!/bin/bash

# ==============================================================================
# VELO Management Script v1.2
# Usage: velo {command} [options]
# ==============================================================================

INSTALL_BASE="/opt/velo"
COMPOSE_DIR="$INSTALL_BASE/repo"
COMPOSE_CMD="docker compose"
DOMAIN="api.talentir.info"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Ensure we're in the right directory for docker compose
cd_compose() {
    cd "$COMPOSE_DIR" || {
        echo -e "${RED}ERROR: $COMPOSE_DIR not found${NC}"
        exit 1
    }
}

# Run frontend tests in a throwaway builder container.
# Uses `docker build --target builder` to get a container with node + source,
# then runs `npm run test` inside it.
run_frontend_tests() {
    echo "Running frontend tests..."
    cd "$COMPOSE_DIR"
    docker build --target builder -t velo-frontend-test -f frontend/Dockerfile frontend/ -q > /dev/null 2>&1
    if docker run --rm velo-frontend-test npm run test; then
        echo -e "${GREEN}✓ Frontend tests passed${NC}"
        return 0
    else
        echo -e "${RED}✗ Frontend tests FAILED${NC}"
        return 1
    fi
}

case "${1:-}" in

    # === Service Management ===

    start)
        echo "Starting VELO..."
        cd_compose
        $COMPOSE_CMD up -d
        echo -e "${GREEN}✓ Started${NC}"
        ;;

    stop)
        echo "Stopping VELO..."
        cd_compose
        $COMPOSE_CMD down
        echo -e "${GREEN}✓ Stopped${NC}"
        ;;

    restart)
        case "${2:-all}" in
            app)
                echo "Restarting app only..."
                cd_compose
                $COMPOSE_CMD restart app
                ;;
            *)
                echo "Restarting all services..."
                cd_compose
                $COMPOSE_CMD down
                $COMPOSE_CMD up -d
                ;;
        esac
        echo -e "${GREEN}✓ Restarted${NC}"
        ;;

    status)
        echo "=== VELO Service Status ==="
        echo ""
        cd_compose
        $COMPOSE_CMD ps
        echo ""

        # Health check
        echo "=== Health Check ==="
        HEALTH=$(curl -s http://127.0.0.1:8000/health 2>/dev/null)
        if [ -n "$HEALTH" ]; then
            echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
        else
            echo -e "${RED}API not responding${NC}"
        fi
        echo ""

        # External check
        echo "=== External Access ==="
        EXT_HEALTH=$(curl -s "https://$DOMAIN/health" 2>/dev/null)
        if [ -n "$EXT_HEALTH" ]; then
            echo -e "${GREEN}✓ https://$DOMAIN/health is accessible${NC}"
        else
            echo -e "${YELLOW}⚠ https://$DOMAIN/health not accessible${NC}"
        fi
        echo ""

        # Disk & memory
        echo "=== Resources ==="
        echo "Disk: $(df -h /opt | tail -1 | awk '{print $3 "/" $2 " (" $5 ")"}')"
        echo "Memory: $(free -h | awk '/Mem:/ {print $3 "/" $2}')"
        echo "Docker images: $(docker images --format '{{.Size}}' | head -5 | paste -sd+ | bc 2>/dev/null || echo 'N/A')"
        ;;

    # === Logs ===

    logs)
        cd_compose
        case "${2:-app}" in
            app)
                $COMPOSE_CMD logs -f --tail=100 app
                ;;
            db|postgres)
                $COMPOSE_CMD logs -f --tail=100 postgres
                ;;
            redis)
                $COMPOSE_CMD logs -f --tail=100 redis
                ;;
            frontend)
                $COMPOSE_CMD logs -f --tail=100 frontend
                ;;
            all|"")
                $COMPOSE_CMD logs -f --tail=100
                ;;
            *)
                echo "Usage: velo logs [app|db|redis|frontend|all]"
                exit 1
                ;;
        esac
        ;;

    # === Testing & Linting ===

    test)
        FAILED=0
        case "${2:-all}" in
            backend)
                echo "=== Backend Tests ==="
                cd_compose
                if ! $COMPOSE_CMD exec -T app python -m pytest tests/ -v --tb=short; then
                    FAILED=1
                fi
                ;;
            frontend)
                echo "=== Frontend Tests ==="
                if ! run_frontend_tests; then
                    FAILED=1
                fi
                ;;
            all|"")
                echo "=== Backend Tests ==="
                cd_compose
                if ! $COMPOSE_CMD exec -T app python -m pytest tests/ -v --tb=short; then
                    FAILED=1
                fi
                echo ""
                echo "=== Frontend Tests ==="
                if ! run_frontend_tests; then
                    FAILED=1
                fi
                ;;
            *)
                echo "Usage: velo test [backend|frontend|all]"
                exit 1
                ;;
        esac

        echo ""
        if [ $FAILED -ne 0 ]; then
            echo -e "${RED}✗ Some tests failed${NC}"
            exit 1
        else
            echo -e "${GREEN}✓ All tests passed${NC}"
        fi
        ;;

    lint)
        cd_compose
        $COMPOSE_CMD exec -T app python -m ruff check app/ tests/
        ;;

    # === Update & Deploy ===

    update|deploy)
        echo "=== Updating VELO ==="
        echo ""

        cd "$INSTALL_BASE/repo"

        # Save current state
        CURRENT_COMMIT=$(git rev-parse --short HEAD)
        BRANCH=$(git branch --show-current)
        echo "Current: $CURRENT_COMMIT ($BRANCH)"

        # Check for uncommitted changes
        if ! git diff-index --quiet HEAD -- 2>/dev/null; then
            echo -e "${YELLOW}⚠ Uncommitted changes detected:${NC}"
            git status --short
            echo ""
            read -p "Discard local changes and update? (y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "Update cancelled"
                exit 1
            fi
            git checkout -- .
        fi

        # Fetch and check
        git fetch origin
        if git diff --quiet HEAD "origin/$BRANCH" 2>/dev/null; then
            echo -e "${GREEN}✓ Already up to date${NC}"
            exit 0
        fi

        # Pull
        echo "Pulling updates..."
        if ! git pull origin "$BRANCH"; then
            echo -e "${RED}Pull failed. Resetting to origin/$BRANCH...${NC}"
            git reset --hard "origin/$BRANCH"
        fi

        NEW_COMMIT=$(git rev-parse --short HEAD)
        echo "Updated: $CURRENT_COMMIT → $NEW_COMMIT"
        echo ""

        # Rebuild and restart
        # NOTE: frontend tests run during `docker compose build frontend`
        # because Dockerfile has `RUN npm run test` before `RUN npm run build`.
        # If tests fail, the build fails, and update stops here.
        echo "Rebuilding Docker images (frontend tests run during build)..."
        cd "$COMPOSE_DIR"
        $COMPOSE_CMD build app frontend

        echo "Restarting services..."
        $COMPOSE_CMD down
        $COMPOSE_CMD up -d

        # Run migrations
        echo ""
        echo "Running database migrations..."
        $COMPOSE_CMD exec -T app python -m alembic upgrade head || {
            echo -e "${RED}✗ Migration failed!${NC}"
            echo "Check logs: velo logs app"
            exit 1
        }
        echo -e "${GREEN}✓ Migrations applied${NC}"

        # Run backend tests
        echo ""
        echo "Running backend tests..."
        if $COMPOSE_CMD exec -T app python -m pytest tests/ -v --tb=short; then
            echo -e "${GREEN}✓ All backend tests passed${NC}"
        else
            echo -e "${RED}✗ BACKEND TESTS FAILED — app is running but code may be broken${NC}"
            echo "Fix the code and run: velo update"
            exit 1
        fi

        # Health check
        echo ""
        echo "Waiting for health check..."
        sleep 5
        HEALTH=$(curl -s http://127.0.0.1:8000/health 2>/dev/null)
        if echo "$HEALTH" | grep -q '"status"'; then
            echo ""
            echo -e "${GREEN}✓ Update complete. API is healthy.${NC}"
            echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
        else
            echo -e "${RED}⚠ API health check failed after update${NC}"
            echo "Check logs: velo logs app"
        fi
        ;;

    # === Backup ===

    backup)
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        BACKUP_DIR="$INSTALL_BASE/backups"
        mkdir -p "$BACKUP_DIR"

        echo "Creating backup..."

        # Dump PostgreSQL from Docker container
        cd_compose
        $COMPOSE_CMD exec -T postgres pg_dump -U velo velo > "$BACKUP_DIR/velo_db_$TIMESTAMP.sql"

        # Backup .env
        cp "$COMPOSE_DIR/backend/.env" "$BACKUP_DIR/env_$TIMESTAMP.bak" 2>/dev/null || true

        # Create archive
        cd "$BACKUP_DIR"
        tar -czf "backup_$TIMESTAMP.tar.gz" "velo_db_$TIMESTAMP.sql" "env_$TIMESTAMP.bak" 2>/dev/null
        rm -f "velo_db_$TIMESTAMP.sql" "env_$TIMESTAMP.bak"

        echo -e "${GREEN}✓ Backup created: $BACKUP_DIR/backup_$TIMESTAMP.tar.gz${NC}"

        # Rotate old backups (keep last 7 days)
        find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +7 -delete
        BACKUP_COUNT=$(find "$BACKUP_DIR" -name "backup_*.tar.gz" | wc -l)
        echo "Total backups: $BACKUP_COUNT (auto-rotating after 7 days)"
        ;;

    # === Database ===

    db)
        cd_compose
        case "${2:-}" in
            connect|psql)
                echo "Connecting to PostgreSQL..."
                $COMPOSE_CMD exec postgres psql -U velo velo
                ;;
            dump)
                TIMESTAMP=$(date +%Y%m%d_%H%M%S)
                OUTPUT="$INSTALL_BASE/backups/db_dump_$TIMESTAMP.sql"
                mkdir -p "$INSTALL_BASE/backups"
                echo "Dumping database..."
                $COMPOSE_CMD exec -T postgres pg_dump -U velo velo > "$OUTPUT"
                echo -e "${GREEN}✓ Dump saved: $OUTPUT${NC}"
                ;;
            restore)
                if [ -z "${3:-}" ]; then
                    echo "Usage: velo db restore <dump_file>"
                    exit 1
                fi
                echo -e "${RED}⚠ This will OVERWRITE the current database!${NC}"
                read -p "Are you sure? (y/n): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    echo "Restoring database..."
                    cat "$3" | $COMPOSE_CMD exec -T postgres psql -U velo velo
                    echo -e "${GREEN}✓ Database restored${NC}"
                fi
                ;;
            migrate)
                echo "Running Alembic migrations..."
                $COMPOSE_CMD exec -T app python -m alembic upgrade head
                echo -e "${GREEN}✓ Migrations complete${NC}"
                ;;
            *)
                echo "Database commands:"
                echo "  velo db connect        — Connect to PostgreSQL (psql)"
                echo "  velo db dump           — Create database dump"
                echo "  velo db restore <file> — Restore from dump"
                echo "  velo db migrate        — Run Alembic migrations"
                ;;
        esac
        ;;

    # === SSL ===

    ssl)
        case "${2:-}" in
            renew)
                echo "Renewing SSL certificate..."
                certbot renew --quiet --post-hook 'systemctl reload nginx'
                echo -e "${GREEN}✓ Done${NC}"
                ;;
            status)
                echo "SSL certificate status:"
                certbot certificates 2>/dev/null || echo "No certificates found"
                ;;
            *)
                echo "SSL commands:"
                echo "  velo ssl renew  — Renew SSL certificate"
                echo "  velo ssl status — Show certificate info"
                ;;
        esac
        ;;

    # === Version ===

    version)
        echo "VELO Management Script v1.2"
        echo ""
        cd "$INSTALL_BASE/repo" 2>/dev/null && {
            echo -n "Commit: "
            git rev-parse --short HEAD 2>/dev/null || echo "unknown"
            echo -n "Branch: "
            git branch --show-current 2>/dev/null || echo "unknown"
            echo -n "Date: "
            git log -1 --format="%ci" 2>/dev/null || echo "unknown"
        }
        echo ""
        cd_compose
        echo "Docker containers:"
        $COMPOSE_CMD ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || $COMPOSE_CMD ps
        ;;

    # === Nginx ===

    nginx)
        case "${2:-}" in
            reload)
                echo "Reloading Nginx..."
                nginx -t && systemctl reload nginx
                echo -e "${GREEN}✓ Nginx reloaded${NC}"
                ;;
            status)
                systemctl status nginx --no-pager -l
                ;;
            *)
                echo "Nginx commands:"
                echo "  velo nginx reload — Reload Nginx config"
                echo "  velo nginx status — Show Nginx status"
                ;;
        esac
        ;;

    # === Help ===

    *)
        echo -e "${CYAN}VELO Management Script${NC}"
        echo "Usage: velo {command} [options]"
        echo ""
        echo "Service Management:"
        echo "  start               — Start all services"
        echo "  stop                — Stop all services"
        echo "  restart [app]       — Restart all (or just app)"
        echo "  status              — Show status + health check"
        echo ""
        echo "Logs:"
        echo "  logs [app|db|redis|frontend] — View logs (default: app)"
        echo ""
        echo "Testing:"
        echo "  test                — Run all tests (backend + frontend)"
        echo "  test backend        — Run backend tests only"
        echo "  test frontend       — Run frontend tests only"
        echo "  lint                — Run linter (ruff)"
        echo ""
        echo "Deployment:"
        echo "  update              — Pull, rebuild, migrate, test, restart"
        echo ""
        echo "Database:"
        echo "  db connect          — Open psql session"
        echo "  db dump             — Create SQL dump"
        echo "  db restore <file>   — Restore from dump"
        echo "  db migrate          — Run Alembic migrations"
        echo ""
        echo "Maintenance:"
        echo "  backup              — Backup DB + .env"
        echo "  ssl renew           — Renew SSL certificate"
        echo "  ssl status          — Show certificate info"
        echo "  nginx reload        — Reload Nginx config"
        echo "  version             — Show version info"
        ;;
esac
MANAGE_EOF

    chmod +x "$INSTALL_BASE/scripts/manage.sh"

    # Create symlink for easy access
    ln -sf "$INSTALL_BASE/scripts/manage.sh" /usr/local/bin/velo

    success "Management script created (use 'velo' command)"
}

mkdir -p "$INSTALL_BASE/scripts"
create_management_script

# ==============================================================================
# BACKUP CRON
# ==============================================================================

setup_backup_cron() {
    if ! crontab -l 2>/dev/null | grep -q "velo backup"; then
        log "Setting up daily backup cron..."
        (crontab -l 2>/dev/null; echo "0 4 * * * /usr/local/bin/velo backup >> /var/log/velo-backup.log 2>&1") | crontab -
        success "Daily backup cron added (4 AM)"
    fi
}

setup_backup_cron

# ==============================================================================
# POST-INSTALLATION
# ==============================================================================

SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "unknown")

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║    VELO Installation Completed Successfully!  ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
echo ""

info "Server: $SERVER_IP"
info "Domain: https://$DOMAIN"
info "Health: https://$DOMAIN/health"
echo ""

info "Directory structure:"
echo "  $INSTALL_BASE/"
echo "  ├── repo/              # Git repository"
echo "  │   ├── backend/       # FastAPI backend"
echo "  │   ├── frontend/      # Vue frontend"
echo "  │   └── docker-compose.yml"
echo "  ├── scripts/           # Management script"
echo "  └── backups/           # Daily backups"

log "Management commands:"
echo -e "  ${CYAN}velo status${NC}          — Check everything"
echo -e "  ${CYAN}velo logs${NC}            — View app logs"
echo -e "  ${CYAN}velo test${NC}            — Run all tests (backend + frontend)"
echo -e "  ${CYAN}velo update${NC}          — Pull + rebuild + migrate + test"
echo -e "  ${CYAN}velo restart${NC}         — Restart all services"
echo -e "  ${CYAN}velo db connect${NC}      — Open psql"
echo -e "  ${CYAN}velo backup${NC}          — Manual backup"
echo ""

warn "Next steps:"
echo "  1. Verify: velo status"
echo "  2. Check: curl https://$DOMAIN/health"
echo ""
