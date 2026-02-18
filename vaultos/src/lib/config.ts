// VaultOS Configuration
// This file defines paths to the vault directories

export const vaultConfig = {
  // Base path to the vault (parent of vaultos/)
  basePath: '..',
  
  // Directory paths relative to basePath
  directories: {
    needsAction: 'Needs_Action',
    pendingApproval: 'Pending_Approval',
    approved: 'Approved',
    rejected: 'Rejected',
    done: 'Done',
    logs: 'Logs',
    signals: 'Signals',
    updates: 'Updates',
  },
  
  // Email configuration
  email: {
    needsActionDir: 'Needs_Action/Email',
    pendingApprovalDir: 'Pending_Approval/Email',
  },
  
  // Social media configuration
  social: {
    pendingApprovalDir: 'Pending_Approval/Social',
  },
  
  // MCP service ports
  mcpPorts: {
    odoo: 3006,
    email: 3005,
    social: 3007,
  },
  
  // Cloud VM configuration
  cloud: {
    ip: '80.225.222.19',
    healthReportPath: 'Signals/health_report.md',
  },
};

export type VaultConfig = typeof vaultConfig;
