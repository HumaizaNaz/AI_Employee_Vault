const VAULT_PATH = process.env.VAULT_PATH || '/home/ubuntu/ai-employee-vault';
const PYTHON = process.env.PYTHON_PATH || '/home/ubuntu/ai-employee-vault/venv/bin/python';

module.exports = {
  apps: [
    {
      name: 'cloud-orchestrator',
      script: './cloud_orchestrator.py',
      interpreter: PYTHON,
      cwd: VAULT_PATH,
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      env: {
        VAULT_PATH: VAULT_PATH,
        ORCHESTRATOR_MODE: 'cloud',
        CLOUD_POLL_INTERVAL: '30'
      }
    },
    {
      name: 'gmail-watcher',
      script: './watchers_gmail/gmail_watcher.py',
      interpreter: PYTHON,
      args: VAULT_PATH,
      cwd: VAULT_PATH,
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      env: {
        VAULT_PATH: VAULT_PATH,
        ORCHESTRATOR_MODE: 'cloud'
      }
    },
    {
      name: 'filesystem-watcher',
      script: './watchers/filesystem_watcher.py',
      interpreter: PYTHON,
      args: VAULT_PATH,
      cwd: VAULT_PATH,
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      env: {
        VAULT_PATH: VAULT_PATH,
        ORCHESTRATOR_MODE: 'cloud'
      }
    },
    {
      name: 'health-monitor',
      script: './health_monitor.py',
      interpreter: PYTHON,
      cwd: VAULT_PATH,
      autorestart: true,
      watch: false,
      max_memory_restart: '256M',
      env: {
        VAULT_PATH: VAULT_PATH,
        HEALTH_CHECK_INTERVAL: '300'
      }
    },
    {
      name: 'sync-manager',
      script: './sync_manager.py',
      interpreter: PYTHON,
      cwd: VAULT_PATH,
      autorestart: true,
      watch: false,
      max_memory_restart: '256M',
      env: {
        VAULT_PATH: VAULT_PATH,
        SYNC_INTERVAL: '300'
      }
    }
  ]
};
