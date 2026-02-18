"use client";

import { Sidebar } from "@/components/Sidebar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Cloud, Server, Activity, CheckCircle2, RefreshCw } from "lucide-react";
import { useData } from "@/hooks/useData";

interface CloudStatus {
  cloud: { status: string; ip: string };
  cpu: number;
  memory: { used: number; total: number };
  disk: { used: number; total: number };
  pm2Processes: { name: string; status: string; cpu: string; memory: string; restarts: number }[];
  recentActivity: { time: string; event: string }[];
}

export default function CloudPage() {
  const { data, loading, refetch } = useData<CloudStatus>("/api/cloud", 15000);

  const cpu = data?.cpu ?? 0;
  const mem = data?.memory ?? { used: 0, total: 1024 };
  const disk = data?.disk ?? { used: 0, total: 50 };
  const processes = data?.pm2Processes ?? [];
  const allOnline = processes.length > 0 && processes.every((p) => p.status === "online");

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <main className="ml-60 p-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">Cloud Status</h1>
            <p className="text-text-muted mt-1">Oracle VM: {data?.cloud?.ip ?? "80.225.222.19"}</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" onClick={refetch}>
              <RefreshCw className="w-4 h-4" />
            </Button>
            <Badge variant={allOnline ? "success" : "warning"} className="text-sm px-4 py-2">
              <CheckCircle2 className="w-4 h-4 mr-2" />
              {loading ? "Loading..." : allOnline ? "All Online" : "Check Processes"}
            </Badge>
          </div>
        </div>

        {/* Resource Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-text-muted">CPU Usage</CardTitle>
              <Activity className="w-5 h-5 text-text-muted" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold mb-2">{loading ? "—" : `${cpu}%`}</div>
              <Progress value={cpu} className="h-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-text-muted">Memory</CardTitle>
              <Server className="w-5 h-5 text-text-muted" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold mb-2">
                {loading ? "—" : `${mem.used}/${mem.total} MB`}
              </div>
              <Progress value={Math.round((mem.used / mem.total) * 100)} className="h-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-text-muted">Disk</CardTitle>
              <Cloud className="w-5 h-5 text-text-muted" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold mb-2">
                {loading ? "—" : `${disk.used}/${disk.total} GB`}
              </div>
              <Progress value={Math.round((disk.used / disk.total) * 100)} className="h-2" />
            </CardContent>
          </Card>
        </div>

        {/* PM2 Processes — real data from pm2 list --json */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>PM2 Processes</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center text-text-muted py-8">Loading process list...</div>
            ) : processes.length === 0 ? (
              <div className="text-center text-text-muted py-8">No PM2 processes found</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">Name</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">Status</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">CPU</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">Memory</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">Restarts</th>
                    </tr>
                  </thead>
                  <tbody>
                    {processes.map((p) => (
                      <tr key={p.name} className="border-b border-border last:border-0">
                        <td className="py-3 px-4 text-sm font-medium">{p.name}</td>
                        <td className="py-3 px-4">
                          <Badge variant={p.status === "online" ? "success" : "danger"} className="text-xs">
                            {p.status === "online" ? "🟢" : "🔴"} {p.status}
                          </Badge>
                        </td>
                        <td className="py-3 px-4 text-sm text-text-muted">{p.cpu}</td>
                        <td className="py-3 px-4 text-sm text-text-muted">{p.memory}</td>
                        <td className="py-3 px-4 text-sm text-text-muted">{p.restarts}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Activity from Signals/ */}
        {data?.recentActivity && data.recentActivity.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Recent Cloud Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {data.recentActivity.map((item, index) => (
                  <div key={index} className="flex items-center gap-4">
                    <span className="text-sm text-text-muted font-mono">{item.time}</span>
                    <span className="text-sm">{item.event}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
