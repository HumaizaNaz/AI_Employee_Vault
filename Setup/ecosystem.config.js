const path = require('path');

const VAULT_PATH = process.env.VAULT_PATH || 'F:/AI_Employee_Vault/AI_Employee_Vault - Copy';

module.exports = {
  apps: [
    {
      name: 'gmail-watcher',
      script: './watchers_gmail/gmail_watcher.py',
      interpreter: 'python',
      args: [VAULT_PATH, 'F:/AI_Employee_Vault/AI_Employee_Vault - Copy/watchers_gmail/token.json'],
      cwd: './',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PYTHONPATH: './System:./',
        VAULT_PATH: VAULT_PATH,
        ORCHESTRATOR_MODE: 'local',
        PYTHONIOENCODING: 'utf-8',
        PYTHONUNBUFFERED: '1'
      }
    },
    {
      name: 'whatsapp-watcher',
      script: './watchers_whatsapp/whatsapp_watcher.py',
      interpreter: 'python',
      args: VAULT_PATH,
      cwd: './',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PYTHONPATH: './System:./',
        VAULT_PATH: VAULT_PATH,
        ORCHESTRATOR_MODE: 'local',
        PYTHONIOENCODING: 'utf-8',
        PYTHONUNBUFFERED: '1'
      }
    },
    {
      name: 'filesystem-watcher',
      script: './watchers/filesystem_watcher.py',
      interpreter: 'python',
      args: VAULT_PATH,
      cwd: './',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PYTHONPATH: './System:./',
        VAULT_PATH: VAULT_PATH,
        ORCHESTRATOR_MODE: 'local',
        PYTHONIOENCODING: 'utf-8',
        PYTHONUNBUFFERED: '1'
      }
    },
    {
      name: 'orchestrator',
      script: './System/orchestrator.py',
      interpreter: 'python',
      args: '',
      cwd: './',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PYTHONPATH: './System:./',
        VAULT_PATH: VAULT_PATH,
        ORCHESTRATOR_MODE: 'local',
        PYTHONIOENCODING: 'utf-8',
        PYTHONUNBUFFERED: '1'
      }
    },
    {
      name: 'mcp-email-server',
      script: './watchers_gmail/mcp/mcp_email.js',
      interpreter: 'node',
      cwd: './',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production',
        VAULT_PATH: VAULT_PATH,
        MCP_EMAIL_PORT: '3005'
      }
    },
    {
      name: 'linkedin-poster',
      script: './Social_Media/linkedin_poster.py',
      interpreter: 'python',
      cwd: './',
      cron_restart: '0 9 * * 1-5',
      autorestart: false,
      watch: false,
      env: {
        NODE_ENV: 'production',
        PYTHONPATH: './System:./',
        VAULT_PATH: VAULT_PATH,
        PYTHONIOENCODING: 'utf-8',
        PYTHONUNBUFFERED: '1'
      }
    },
    {
      name: 'social-auto-poster',
      script: './Social_Media/social_auto_poster.py',
      interpreter: 'python',
      cwd: './',
      cron_restart: '0 10 * * 1-5',
      autorestart: false,
      watch: false,
      env: {
        NODE_ENV: 'production',
        PYTHONPATH: './System:./',
        VAULT_PATH: VAULT_PATH,
        PYTHONIOENCODING: 'utf-8',
        PYTHONUNBUFFERED: '1'
      }
    },
    {
      name: 'odoo-mcp-server',
      script: './Accounting/odoo_mcp_server.js',
      interpreter: 'node',
      cwd: './',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production',
        VAULT_PATH: VAULT_PATH,
        ODOO_URL: 'http://localhost:8069',
        ODOO_DB: 'ai_emp',
        ODOO_USERNAME: 'humaizaasghar@gmail.com',
        ODOO_PASSWORD: '123Ai_emply',
        ODOO_MCP_PORT: '3006'
      }
    },
    {
      name: 'ceo-briefing',
      script: './System/ceo_briefing.py',
      interpreter: 'python',
      cwd: './',
      cron_restart: '0 23 * * 0',
      autorestart: false,
      watch: false,
      env: {
        NODE_ENV: 'production',
        PYTHONPATH: './System:./',
        VAULT_PATH: VAULT_PATH,
        PYTHONIOENCODING: 'utf-8',
        PYTHONUNBUFFERED: '1'
      }
    }
  ]
};
