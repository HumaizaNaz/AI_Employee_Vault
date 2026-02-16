const path = require('path');

const VAULT_PATH = process.env.VAULT_PATH || 'F:/AI_Employee_Vault/AI_Employee_Vault';

module.exports = {
  apps: [
    {
      name: 'gmail-watcher',
      script: './watchers_gmail/gmail_watcher.py',
      interpreter: 'python',
      args: VAULT_PATH,
      cwd: './',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PYTHONPATH: './',
        VAULT_PATH: VAULT_PATH,
        ORCHESTRATOR_MODE: 'local'
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
        PYTHONPATH: './',
        VAULT_PATH: VAULT_PATH,
        ORCHESTRATOR_MODE: 'local'
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
        PYTHONPATH: './',
        VAULT_PATH: VAULT_PATH,
        ORCHESTRATOR_MODE: 'local'
      }
    },
    {
      name: 'orchestrator',
      script: './orchestrator.py',
      interpreter: 'python',
      args: '',
      cwd: './',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PYTHONPATH: './',
        VAULT_PATH: VAULT_PATH,
        ORCHESTRATOR_MODE: 'local'
      }
    }
  ]
};
