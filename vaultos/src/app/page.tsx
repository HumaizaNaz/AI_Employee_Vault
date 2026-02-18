"use client";

import { Sidebar } from "@/components/Sidebar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Mail, MessageCircle, AlertTriangle, Building2, Activity, CheckCircle2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useData } from "@/hooks/useData";

const activityData = [
  { day: "Mon", value: 12 },
  { day: "Tue", value: 18 },
  { day: "Wed", value: 25 },
  { day: "Thu", value: 15 },
  { day: "Fri", value: 22 },
  { day: "Sat", value: 10 },
  { day: "Sun", value: 8 },
];

export default function Dashboard() {
  const { data: emailData, loading: emailLoading, refetch: refetchEmails } = useData<{ emails: any[] }>("/api/emails");
  const { data: waData, loading: waLoading } = useData<{ messages: any[] }>("/api/whatsapp");
  const { data: approvalData, loading: approvalLoading } = useData<{ approvals: any[] }>("/api/approvals");
  const { data: accountingData, loading: accountingLoading } = useData<{ stats: any; error?: string }>("/api/accounting");
  const { data: cloudData, loading: cloudLoading } = useData<{ pm2Processes: any[] }>("/api/cloud", 15000);

  const emails = emailData?.emails ?? [];
  const messages = waData?.messages ?? [];
  const approvals = (approvalData?.approvals ?? []).filter((a: any) => a.status === "pending");
  const draftInvoices = accountingData?.stats?.draft ?? 0;
  const processes = cloudData?.pm2Processes ?? [];
  const allOnline = processes.length > 0 && processes.every((p: any) => p.status === "online");

  const loading = emailLoading && waLoading && approvalLoading;

  return (
    <div className="min-h-screen bg-background">
      <Sidebar emailCount={emails.length} waCount={messages.length} approvalCount={approvals.length} />
      <main className="ml-60 p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-text-muted mt-1">Your AI Employee Command Center</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" onClick={refetchEmails}>
              <RefreshCw className="w-4 h-4" />
            </Button>
            <Badge variant={allOnline || cloudLoading ? "success" : "warning"} className="text-sm px-4 py-2">
              <CheckCircle2 className="w-4 h-4 mr-2" />
              {cloudLoading ? "Checking..." : allOnline ? "All Systems Online" : "Check Cloud"}
            </Badge>
          </div>
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-text-muted">Emails in Queue</CardTitle>
              <Mail className="w-5 h-5 text-text-muted" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{emailLoading ? "—" : emails.length}</div>
              <p className="text-xs text-text-muted mt-1">Needs_Action/Email/</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-text-muted">WhatsApp Messages</CardTitle>
              <MessageCircle className="w-5 h-5 text-text-muted" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{waLoading ? "—" : messages.length}</div>
              <p className="text-xs text-text-muted mt-1">Needs_Action/WhatsApp/</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-text-muted">Pending Approvals</CardTitle>
              <AlertTriangle className="w-5 h-5 text-warning" />
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${approvals.length > 0 ? "text-warning" : ""}`}>
                {approvalLoading ? "—" : approvals.length}
              </div>
              <p className="text-xs text-text-muted mt-1">
                {approvals.length > 0 ? "Action required" : "All clear"}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-text-muted">Odoo Draft Invoices</CardTitle>
              <Building2 className="w-5 h-5 text-text-muted" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{accountingLoading ? "—" : draftInvoices}</div>
              <p className="text-xs text-text-muted mt-1">
                {accountingData?.error ? "Odoo offline" : "Draft invoices"}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts + Status */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Activity Overview (7 days)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={activityData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                  <XAxis dataKey="day" stroke="#71717A" />
                  <YAxis stroke="#71717A" />
                  <Tooltip contentStyle={{ backgroundColor: "#18181B", border: "1px solid #27272A", borderRadius: "8px" }} />
                  <Bar dataKey="value" fill="#6366F1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>System Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                { label: "Cloud VM", ok: allOnline || cloudLoading, text: allOnline ? "ONLINE" : "CHECK" },
                { label: "Gmail Watcher", ok: true, text: "ACTIVE" },
                { label: "WhatsApp Watcher", ok: true, text: "ACTIVE" },
                { label: "Odoo MCP", ok: !accountingData?.error, text: accountingData?.error ? "OFFLINE" : "PORT 3006" },
                { label: "Email MCP", ok: true, text: "PORT 3005" },
                { label: "Social MCP", ok: true, text: "PORT 3007" },
              ].map((item) => (
                <div key={item.label} className="flex items-center justify-between">
                  <span className="text-sm text-text-muted">{item.label}</span>
                  <Badge variant={item.ok ? "success" : "danger"}>{item.text}</Badge>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Approvals Alert + Social */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Pending Approvals</CardTitle>
            </CardHeader>
            <CardContent>
              {approvalLoading ? (
                <p className="text-text-muted text-sm">Loading...</p>
              ) : approvals.length === 0 ? (
                <p className="text-text-muted text-sm">No pending approvals — vault is clear.</p>
              ) : (
                <div className="space-y-3">
                  {approvals.slice(0, 5).map((a: any) => (
                    <div key={a.id} className="flex items-center justify-between bg-zinc-900 rounded-lg px-4 py-3">
                      <div>
                        <p className="text-sm font-medium">
                          {a.type === "email" ? "📧" : "📱"}{" "}
                          {a.subject || a.platform || a.type}
                        </p>
                        <p className="text-xs text-text-muted">{a.created || "—"}</p>
                      </div>
                      <Badge variant="warning">⚠ Pending</Badge>
                    </div>
                  ))}
                  {approvals.length > 5 && (
                    <p className="text-sm text-text-muted">+{approvals.length - 5} more in Approvals page</p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Social Media</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-text-muted">Facebook</span>
                <Badge variant="success">Connected</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-text-muted">Instagram</span>
                <Badge variant="success">Connected</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-text-muted">Twitter/X</span>
                <Badge variant="warning">Mar 1 reset</Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
