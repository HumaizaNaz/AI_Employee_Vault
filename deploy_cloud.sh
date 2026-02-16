#!/bin/bash
# ==============================================================================
# AI Employee - Cloud Deployment Script
# One-command setup for Oracle Cloud Free Tier VM
#
# Usage: bash deploy_cloud.sh [REPO_URL]
# ==============================================================================

set -e

# --- Configuration ---
REPO_URL="${1:-}"
INSTALL_DIR="/home/ubuntu/ai-employee-vault"
PYTHON_VERSION="3.11"
NODE_VERSION="20"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() { echo -e "${GREEN}[DEPLOY]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# --- Pre-flight checks ---
log "Starting AI Employee Cloud Deployment..."

if [ -z "$REPO_URL" ]; then
    error "Usage: bash deploy_cloud.sh <REPO_URL>"
fi

if [ "$(whoami)" = "root" ]; then
    warn "Running as root. Recommended to run as 'ubuntu' user."
fi

# --- Step 1: System Update & Dependencies ---
log "Step 1/7: Installing system dependencies..."

sudo apt update && sudo apt upgrade -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install -y \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-venv \
    python${PYTHON_VERSION}-dev \
    python3-pip \
    git \
    curl \
    jq

# Set Python default
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1
sudo update-alternatives --install /usr/bin/python python /usr/bin/python${PYTHON_VERSION} 1

log "Python $(python --version) installed"

# --- Step 2: Install Node.js & PM2 ---
log "Step 2/7: Installing Node.js ${NODE_VERSION} and PM2..."

if ! command -v node &>/dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | sudo -E bash -
    sudo apt install -y nodejs
fi

sudo npm install -g pm2

log "Node $(node --version), PM2 $(pm2 --version) installed"

# --- Step 3: Clone Repository ---
log "Step 3/7: Cloning repository..."

if [ -d "$INSTALL_DIR" ]; then
    warn "Directory $INSTALL_DIR already exists. Pulling latest changes..."
    cd "$INSTALL_DIR"
    git pull
else
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

log "Repository ready at $INSTALL_DIR"

# --- Step 4: Python Virtual Environment ---
log "Step 4/7: Setting up Python virtual environment..."

python -m venv "$INSTALL_DIR/venv"
source "$INSTALL_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r "$INSTALL_DIR/requirements.txt"

log "Python dependencies installed"

# --- Step 5: Create .env Template ---
log "Step 5/7: Creating environment configuration..."

ENV_FILE="$INSTALL_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" << 'ENVTEMPLATE'
# AI Employee Cloud Configuration
# Fill in your actual values below

# Vault path (DO NOT CHANGE on cloud)
VAULT_PATH=/home/ubuntu/ai-employee-vault

# Orchestrator mode (DO NOT CHANGE on cloud)
ORCHESTRATOR_MODE=cloud

# Sync mode
SYNC_MODE=cloud
SYNC_INTERVAL=300

# Cloud poll interval (seconds)
CLOUD_POLL_INTERVAL=30

# Health check interval (seconds)
HEALTH_CHECK_INTERVAL=300

# Python path for PM2
PYTHON_PATH=/home/ubuntu/ai-employee-vault/venv/bin/python

# API Key for MCP servers
API_KEY=CHANGE_ME_YOUR_API_KEY_HERE

# Gmail credentials path (place your token.json in vault root)
GMAIL_CREDENTIALS_PATH=/home/ubuntu/ai-employee-vault/token.json
ENVTEMPLATE

    chmod 600 "$ENV_FILE"
    warn ".env file created. Please edit it with your actual API keys:"
    warn "  nano $ENV_FILE"
else
    log ".env file already exists, skipping"
fi

# --- Step 6: Create Required Folders ---
log "Step 6/7: Creating vault folder structure..."

mkdir -p "$INSTALL_DIR/Needs_Action/Email"
mkdir -p "$INSTALL_DIR/Needs_Action/WhatsApp"
mkdir -p "$INSTALL_DIR/Needs_Action/Files"
mkdir -p "$INSTALL_DIR/Needs_Action/Processed"
mkdir -p "$INSTALL_DIR/Pending_Approval/Email"
mkdir -p "$INSTALL_DIR/Pending_Approval/WhatsApp"
mkdir -p "$INSTALL_DIR/Pending_Approval/Files"
mkdir -p "$INSTALL_DIR/Approved/Email"
mkdir -p "$INSTALL_DIR/Approved/WhatsApp"
mkdir -p "$INSTALL_DIR/Approved/Files"
mkdir -p "$INSTALL_DIR/Rejected"
mkdir -p "$INSTALL_DIR/Done/Email"
mkdir -p "$INSTALL_DIR/Done/WhatsApp"
mkdir -p "$INSTALL_DIR/Done/Files"
mkdir -p "$INSTALL_DIR/Drafts"
mkdir -p "$INSTALL_DIR/Signals"
mkdir -p "$INSTALL_DIR/Updates"
mkdir -p "$INSTALL_DIR/Logs"
mkdir -p "$INSTALL_DIR/Plans"

log "Folder structure created"

# --- Step 7: Start PM2 Processes ---
log "Step 7/7: Starting cloud services with PM2..."

cd "$INSTALL_DIR"

# Load env vars for PM2
export $(grep -v '^#' "$ENV_FILE" | xargs)

# Stop any existing processes
pm2 delete all 2>/dev/null || true

# Start cloud processes
pm2 start cloud_ecosystem.config.js

# Save PM2 state and configure auto-start
pm2 save
pm2 startup systemd -u ubuntu --hp /home/ubuntu 2>/dev/null || \
    warn "Run 'pm2 startup' manually and follow its instructions"

# --- Verification ---
log "============================================"
log "  DEPLOYMENT COMPLETE"
log "============================================"
echo ""

# Show PM2 status
pm2 status

echo ""
log "Next steps:"
log "  1. Edit your .env file: nano $ENV_FILE"
log "  2. Add your Gmail token.json to $INSTALL_DIR/"
log "  3. Restart services: pm2 restart all"
log "  4. Check health: python $INSTALL_DIR/health_monitor.py --once"
log "  5. Monitor logs: pm2 logs"
echo ""

# Run quick health check
log "Running initial health check..."
python "$INSTALL_DIR/health_monitor.py" --once 2>/dev/null || warn "Health check requires services to be running"

log "Done! Your AI Employee is now running in the cloud."
