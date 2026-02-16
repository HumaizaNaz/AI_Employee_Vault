# Oracle Cloud VM Setup Guide - AI Employee Platinum Tier

## Prerequisites
- Email address for Oracle Cloud account
- Credit/debit card (for verification only - Free Tier is never charged)
- SSH client (PuTTY on Windows, or built-in ssh on Mac/Linux)

---

## Step 1: Sign Up for Oracle Cloud Free Tier

1. Go to [https://www.oracle.com/cloud/free/](https://www.oracle.com/cloud/free/)
2. Click **Start for Free**
3. Fill in your details and verify your email
4. Add a payment method (verification only, Free Tier is always free)
5. Select your **Home Region** (choose closest to you for low latency)
6. Wait for account provisioning (usually 5-15 minutes)

### What You Get (Always Free)
- **ARM VM**: Up to 4 OCPUs + 24 GB RAM (Ampere A1)
- **Boot Volume**: 200 GB total block storage
- **Networking**: 10 TB/month outbound data
- **Object Storage**: 20 GB

---

## Step 2: Create Ubuntu 22.04 VM Instance

1. Log in to Oracle Cloud Console
2. Navigate to **Compute > Instances > Create Instance**
3. Configure:
   - **Name**: `ai-employee-vm`
   - **Image**: Ubuntu 22.04 (Canonical)
   - **Shape**: Click **Change Shape** > **Ampere** > **VM.Standard.A1.Flex**
     - OCPUs: **4**
     - Memory: **24 GB**
   - **Networking**: Create new VCN or use existing
     - Ensure **Assign a public IPv4 address** is checked
   - **SSH Keys**: Upload your public key or let Oracle generate one
     - **IMPORTANT**: Download the private key if generated - you cannot retrieve it later
   - **Boot Volume**: 50 GB (default is fine)
4. Click **Create**
5. Wait for instance state to show **RUNNING**
6. Note the **Public IP Address** from the instance details

---

## Step 3: Configure Security List (Firewall)

1. Go to **Networking > Virtual Cloud Networks**
2. Click your VCN > **Security Lists** > **Default Security List**
3. Add **Ingress Rules**:

| Stateless | Source CIDR | Protocol | Dest Port | Description |
|-----------|------------|----------|-----------|-------------|
| No | 0.0.0.0/0 | TCP | 22 | SSH |
| No | YOUR_IP/32 | TCP | 3005 | Email MCP Server |
| No | YOUR_IP/32 | TCP | 3006 | Odoo MCP Server |
| No | YOUR_IP/32 | TCP | 3007 | Social Media MCP |

> **Security Note**: Replace `YOUR_IP/32` with your actual public IP to restrict MCP access.
> Never open MCP ports to `0.0.0.0/0` in production.

4. Also open the Ubuntu firewall on the VM:
```bash
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 3005 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 3006 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 3007 -j ACCEPT
sudo netfilter-persistent save
```

---

## Step 4: SSH Key Setup

### Generate SSH Key (if you don't have one)
```bash
ssh-keygen -t ed25519 -C "ai-employee-cloud" -f ~/.ssh/ai_employee_cloud
```

### Connect to VM
```bash
ssh -i ~/.ssh/ai_employee_cloud ubuntu@<YOUR_VM_PUBLIC_IP>
```

### Add to SSH Config (~/.ssh/config)
```
Host ai-employee
    HostName <YOUR_VM_PUBLIC_IP>
    User ubuntu
    IdentityFile ~/.ssh/ai_employee_cloud
    ServerAliveInterval 60
```

Then connect with just: `ssh ai-employee`

---

## Step 5: Install Dependencies on VM

SSH into the VM and run:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Set Python 3.11 as default
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2 globally
sudo npm install -g pm2

# Install Git
sudo apt install -y git

# Verify installations
python --version    # Should show 3.11.x
node --version      # Should show v20.x.x
pm2 --version       # Should show 5.x.x
git --version       # Should show 2.x.x
```

---

## Step 6: Clone and Configure

```bash
# Clone the vault repo
cd /home/ubuntu
git clone <YOUR_REPO_URL> ai-employee-vault
cd ai-employee-vault

# Create Python virtual environment
python -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create .env file (fill in your actual values)
cp .env.template .env
nano .env
```

---

## Step 7: Start Cloud Services

```bash
cd /home/ubuntu/ai-employee-vault

# Start cloud processes with PM2
pm2 start cloud_ecosystem.config.js

# Save PM2 config (auto-start on reboot)
pm2 save
pm2 startup

# Verify everything is running
pm2 status
pm2 logs --lines 20
```

---

## Step 8: Verify Health

```bash
# Run health check
python health_monitor.py

# Check the health report
cat Signals/health_report.md

# Monitor logs
pm2 logs
```

---

## Troubleshooting

### VM won't start
- Check your tenancy limits in OCI Console > Governance > Limits
- ARM instances are popular; try a different availability domain

### Can't SSH
- Verify security list has port 22 open
- Check that your SSH key matches what was uploaded
- Try: `ssh -vvv -i ~/.ssh/ai_employee_cloud ubuntu@<IP>`

### PM2 processes crashing
- Check logs: `pm2 logs <process-name> --lines 50`
- Verify .env file has all required values
- Check Python venv is activated in ecosystem config

### MCP servers unreachable
- Verify security list rules include your IP
- Check Ubuntu firewall: `sudo iptables -L -n`
- Test locally first: `curl http://localhost:3005/health`

---

## Security Checklist

- [ ] SSH key authentication only (no password login)
- [ ] MCP ports restricted to your IP only
- [ ] `.env` file has proper permissions: `chmod 600 .env`
- [ ] Git sync never pushes `.env`, tokens, or credentials
- [ ] PM2 logs don't contain sensitive data
- [ ] Regular `sudo apt update && sudo apt upgrade`
