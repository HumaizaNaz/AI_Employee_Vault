"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard, Mail, MessageCircle, AlertTriangle,
  Share2, Building2, Cloud, FileText,
} from "lucide-react";

interface SidebarProps {
  emailCount?: number;
  waCount?: number;
  approvalCount?: number;
}

export function Sidebar({ emailCount, waCount, approvalCount }: SidebarProps) {
  const pathname = usePathname();

  const navItems = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    { name: "Emails", href: "/emails", icon: Mail, badge: emailCount },
    { name: "WhatsApp", href: "/whatsapp", icon: MessageCircle, badge: waCount },
    { name: "Approvals", href: "/approvals", icon: AlertTriangle, badge: approvalCount, highlight: true },
    { name: "Social Media", href: "/social", icon: Share2 },
    { name: "Accounting", href: "/accounting", icon: Building2 },
    { name: "Cloud Status", href: "/cloud", icon: Cloud },
    { name: "Logs", href: "/logs", icon: FileText },
  ];

  return (
    <aside className="fixed left-0 top-0 h-full w-60 bg-card border-r border-border flex flex-col">
      {/* Logo */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🔷</span>
          <span className="text-xl font-bold">VaultOS</span>
        </div>
        <p className="text-xs text-text-muted mt-1">AI Employee Command Center</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          const showBadge = item.badge !== undefined && item.badge > 0;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center justify-between px-3 py-2 rounded-lg transition-colors",
                isActive
                  ? "bg-primary text-white"
                  : "text-text-muted hover:bg-zinc-800 hover:text-text-primary",
                item.highlight && !isActive && showBadge && "text-warning"
              )}
            >
              <div className="flex items-center gap-3">
                <Icon className="w-5 h-5" />
                <span className="text-sm">{item.name}</span>
              </div>
              {showBadge && (
                <span
                  className={cn(
                    "px-2 py-0.5 text-xs rounded-full font-medium",
                    isActive
                      ? "bg-white/20 text-white"
                      : item.highlight
                      ? "bg-warning/20 text-warning"
                      : "bg-zinc-800 text-text-muted"
                  )}
                >
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* System Status Footer */}
      <div className="p-4 border-t border-border space-y-2">
        <p className="text-xs text-text-muted font-medium mb-2">System</p>
        <div className="flex items-center gap-2 text-xs text-text-muted">
          <span className="w-2 h-2 rounded-full bg-success flex-shrink-0"></span>
          <span>Cloud: ONLINE</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-text-muted">
          <span className="w-2 h-2 rounded-full bg-success flex-shrink-0"></span>
          <span>Local: RUNNING</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-text-muted">
          <span className="w-2 h-2 rounded-full bg-success flex-shrink-0"></span>
          <span>Odoo: PORT 3006</span>
        </div>
      </div>
    </aside>
  );
}
