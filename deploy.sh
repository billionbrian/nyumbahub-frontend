#!/usr/bin/env bash
###############################################################################
# NyumbaHub Local Deploy Script
# Spins up: PostgreSQL (db) + Redis + Django (gunicorn) + cloudflared tunnel
#
# Usage:
#   chmod +x deploy.sh
#   ./deploy.sh
#
# Prerequisites for cloudflared with YOUR domain:
#   1. A domain on Cloudflare (e.g. nyumbahub.app)
#   2. A named tunnel created: cloudflared tunnel create nyumbahub
#   3. DNS routed: cloudflared tunnel route dns nyumbahub <your-domain>
#   4. credentials JSON saved to credentials/nyumbahub.json
#   5. Edit cloudflared-config.yml with your tunnel id + domain
###############################################################################
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"

VENV="/home/zayne/nyumbahub/venv/bin"
ENV_FILE=".env"
CLOUDFLARED_CONFIG="cloudflared-config.yml"
CREDENTIALS_DIR="credentials"

# Colours
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log()  { echo -e "${GREEN}[deploy]${NC} $*"; }
warn() { echo -e "${YELLOW}[deploy]${NC} $*"; }
err()  { echo -e "${RED}[deploy]${NC} $*" >&2; }

# ---------------------------------------------------------------------------
# Load local .env (gitignored) so Django uses PostgreSQL + Redis
# ---------------------------------------------------------------------------
if [[ -f "$ENV_FILE" ]]; then
  # Robust .env loader: exports KEY=VALUE line-by-line (safer than `source`)
  while IFS= read -r line || [[ -n "$line" ]]; do
    # skip comments and blank lines
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line// }" ]] && continue
    # strip leading/trailing whitespace
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    # only lines with =
    [[ "$line" == *"="* ]] || continue
    key="${line%%=*}"
    value="${line#*=}"
    # strip surrounding quotes
    value="${value#\"}"; value="${value%\"}"
    value="${value#\'}"; value="${value%\'}"
    export "$key=$value"
  done < "$ENV_FILE"
  log "Loaded $ENV_FILE"
else
  err "$ENV_FILE not found. Copy .env.example to .env and fill in values."
  exit 1
fi

# ---------------------------------------------------------------------------
# Sanity: virtualenv
# ---------------------------------------------------------------------------
if [[ ! -x "$VENV/python" ]]; then
  err "Virtualenv not found at $VENV"
  exit 1
fi

PY="$VENV/python"

# ---------------------------------------------------------------------------
# Helper: wait for a TCP port
# ---------------------------------------------------------------------------
wait_for_port() {
  local host=$1 port=$2 name=$3
  log "Waiting for $name ($host:$port)..."
  for i in $(seq 1 30); do
    if $PY -c "
import socket, sys
s = socket.socket(); s.settimeout(1)
try:
    s.connect(('$host', $port)); s.close(); sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
      log "$name is ready."
      return 0
    fi
    sleep 2
  done
  err "$name not reachable at $host:$port after 60s"
  return 1
}

# ---------------------------------------------------------------------------
# 1. PostgreSQL (db) — use existing host container if reachable, else start one
# ---------------------------------------------------------------------------
if $PY -c "
import socket, sys
s = socket.socket(); s.settimeout(1)
try:
    s.connect(('localhost', 5432)); s.close(); sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
  log "PostgreSQL already reachable on localhost:5432."
else
  log "Starting PostgreSQL container (nyumbahub_db)..."
  docker run -d --name nyumbahub_db \
    -e POSTGRES_DB=nyumbahub \
    -e POSTGRES_USER=nyumbahub \
    -e POSTGRES_PASSWORD=nyumbahub \
    -p 5432:5432 \
    -v nyumbahub_postgres_data:/var/lib/postgresql/data \
    postgres:16-alpine >/dev/null 2>&1 || true
fi
wait_for_port localhost 5432 PostgreSQL

# ---------------------------------------------------------------------------
# 2. Redis — use existing host container if reachable, else start one
# ---------------------------------------------------------------------------
if $PY -c "
import socket, sys
s = socket.socket(); s.settimeout(1)
try:
    s.connect(('localhost', 6379)); s.close(); sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
  log "Redis already reachable on localhost:6379."
else
  log "Starting Redis container (nyumbahub_redis)..."
  docker run -d --name nyumbahub_redis \
    -p 6379:6379 \
    -v nyumbahub_redis_data:/data \
    redis:7-alpine redis-server --appendonly yes >/dev/null 2>&1 || true
fi
wait_for_port localhost 6379 Redis

# ---------------------------------------------------------------------------
# 3. Ensure the nyumbahub database exists (best-effort)
# ---------------------------------------------------------------------------
log "Ensuring 'nyumbahub' database exists..."
$PY -c "
import os, sys
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost', port=5432,
        user=os.getenv('POSTGRES_USER','postgres'),
        password=os.getenv('POSTGRES_PASSWORD','postgres'),
        dbname='postgres'
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(\"SELECT 1 FROM pg_database WHERE datname='nyumbahub'\")
    if not cur.fetchone():
        cur.execute('CREATE DATABASE nyumbahub')
        print('Created database nyumbahub')
    else:
        print('Database nyumbahub already exists')
    cur.close(); conn.close()
except Exception as e:
    print('Could not auto-create database:', e)
    sys.exit(0)
" 2>/dev/null || true

# ---------------------------------------------------------------------------
# 4. Django migrations + collectstatic
# ---------------------------------------------------------------------------
log "Running Django migrations..."
$PY manage.py migrate --noinput

log "Collecting static files..."
$PY manage.py collectstatic --noinput

# ---------------------------------------------------------------------------
# 5. Start gunicorn (Django) if not already on 8000
# ---------------------------------------------------------------------------
if ss -tlnp 2>/dev/null | grep -q ':8000'; then
  log "gunicorn already running on 8000."
else
  log "Starting gunicorn on 0.0.0.0:8000..."
  nohup $VENV/gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    config.wsgi:application \
    > /tmp/nyumbahub_gunicorn.log 2>&1 &
  sleep 4
fi
wait_for_port localhost 8000 Django

# ---------------------------------------------------------------------------
# 6. cloudflared tunnel with YOUR domain (named tunnel)
# ---------------------------------------------------------------------------
log "Checking cloudflared..."

if ! command -v cloudflared >/dev/null 2>&1; then
  warn "cloudflared not installed."
  warn "Install it (macOS): brew install cloudflared"
  warn "Or download: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/tunnel-guide/"
else
  if [[ ! -f "$CLOUDFLARED_CONFIG" ]]; then
    warn "$CLOUDFLARED_CONFIG not found. Creating template..."
    if [[ -f "cloudflared-config.yml.template" ]]; then
      cp cloudflared-config.yml.template "$CLOUDFLARED_CONFIG"
    else
      cat > "$CLOUDFLARED_CONFIG" <<EOF
# NyumbaHub cloudflared named tunnel config
# 1. cloudflared tunnel create nyumbahub
# 2. cloudflared tunnel route dns nyumbahub <your-domain>
# 3. Save credentials to credentials/nyumbahub.json
# 4. Edit tunnel id, credentials-file, and hostname below

tunnel: <YOUR_TUNNEL_ID_OR_NAME>
credentials-file: $APP_DIR/credentials/nyumbahub.json

ingress:
  - hostname: <YOUR-DOMAIN.COM>
    service: http://localhost:8000
  - service: http_status:404
EOF
    fi
    warn "Please edit $CLOUDFLARED_CONFIG with your tunnel id, credentials path, and domain."
    warn "Then re-run ./deploy.sh to start the tunnel."
  else
    mkdir -p "$CREDENTIALS_DIR"
    if ! pgrep -x cloudflared >/dev/null 2>&1; then
      log "Starting cloudflared tunnel ($CLOUDFLARED_CONFIG)..."
      nohup cloudflared --config "$CLOUDFLARED_CONFIG" tunnel run \
        > /tmp/nyumbahub_cloudflared.log 2>&1 &
      sleep 5
      log "cloudflared started. Logs: /tmp/nyumbahub_cloudflared.log"
    else
      log "cloudflared already running."
    fi
  fi
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo "=============================================="
echo "  NyumbaHub is running"
echo "=============================================="
echo "  Local:   http://localhost:8000"
echo "  API:     http://localhost:8000/api/properties/"
echo "  Admin:   http://localhost:8000/admin/"
echo "  Tunnel:  check $CLOUDFLARED_CONFIG for your domain URL"
echo ""
echo "  Demo login:"
  echo "    Landlord: demo_landlord / DemoLandlord123!"
  echo "    Tenant:   demo_tenant   / DemoTenant123!"
echo "=============================================="
