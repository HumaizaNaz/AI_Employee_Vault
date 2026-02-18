"use client";

import { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Mail, Share2, Check, X, Eye, RefreshCw, Inbox } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useData } from "@/hooks/useData";

interface ApprovalItem {
  id: string;
  type: "email" | "social";
  status: "pending" | "approved" | "rejected";
  created: string;
  recipient?: string;
  subject?: string;
  platform?: string;
  content: string;
}

export default function ApprovalsPage() {
  const { data, loading, error, refetch } = useData<{ approvals: ApprovalItem[] }>("/api/approvals");
  const [processing, setProcessing] = useState<string | null>(null);
  const [localStatuses, setLocalStatuses] = useState<Record<string, string>>({});

  const approvals = data?.approvals || [];
  const pendingCount = approvals.filter(
    (a) => !localStatuses[a.id] && a.status === "pending"
  ).length;

  const handleAction = async (id: string, action: "approve" | "reject") => {
    setProcessing(id);
    try {
      const res = await fetch("/api/approvals", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, action }),
      });
      if (res.ok) {
        setLocalStatuses((prev) => ({ ...prev, [id]: action === "approve" ? "approved" : "rejected" }));
        refetch();
      }
    } finally {
      setProcessing(null);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <main className="ml-60 p-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">Approvals</h1>
            <p className="text-text-muted mt-1">
              {loading ? "Loading..." : `${pendingCount} item${pendingCount !== 1 ? "s" : ""} pending approval`}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" onClick={refetch}>
              <RefreshCw className="w-4 h-4" />
            </Button>
            <Badge variant={pendingCount > 0 ? "warning" : "success"}>
              {pendingCount > 0 ? `⚠ ${pendingCount} Pending` : "✓ All Clear"}
            </Badge>
          </div>
        </div>

        {loading && (
          <div className="flex items-center justify-center h-64 text-text-muted">
            Loading from vault...
          </div>
        )}

        {error && (
          <Card className="border-danger/50">
            <CardContent className="py-6 text-danger">{error}</CardContent>
          </Card>
        )}

        {!loading && approvals.length === 0 && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center h-64 text-text-muted gap-4">
              <Inbox className="w-12 h-12" />
              <p>No pending approvals</p>
              <p className="text-sm">Vault folder: Pending_Approval/</p>
            </CardContent>
          </Card>
        )}

        <div className="space-y-6">
          {approvals.map((item) => {
            const currentStatus = localStatuses[item.id] || item.status;
            return (
              <Card key={item.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {item.type === "email" ? (
                        <Mail className="w-6 h-6 text-primary" />
                      ) : (
                        <Share2 className="w-6 h-6 text-primary" />
                      )}
                      <div>
                        <CardTitle className="text-lg">
                          {item.type === "email" ? "📧 EMAIL DRAFT" : "📱 SOCIAL POST DRAFT"}
                        </CardTitle>
                        <p className="text-sm text-text-muted mt-1">Created: {item.created || "—"}</p>
                      </div>
                    </div>
                    <Badge
                      variant={
                        currentStatus === "pending" ? "warning"
                        : currentStatus === "approved" ? "success"
                        : "danger"
                      }
                    >
                      {currentStatus === "pending" && "⚠ PENDING"}
                      {currentStatus === "approved" && "✓ APPROVED"}
                      {currentStatus === "rejected" && "✕ REJECTED"}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {item.type === "email" && item.recipient && (
                      <div className="text-sm space-y-1">
                        <p className="text-text-muted"><span className="font-medium">To:</span> {item.recipient}</p>
                        {item.subject && <p className="text-text-muted"><span className="font-medium">Subject:</span> {item.subject}</p>}
                      </div>
                    )}
                    {item.type === "social" && item.platform && (
                      <p className="text-sm text-text-muted"><span className="font-medium">Platform:</span> {item.platform}</p>
                    )}

                    <div className="bg-zinc-900 rounded-lg p-4 max-h-40 overflow-y-auto">
                      <p className="text-sm whitespace-pre-wrap">{item.content}</p>
                    </div>

                    {currentStatus === "pending" && (
                      <div className="flex items-center gap-4 pt-4">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button variant="outline">
                              <Eye className="w-4 h-4 mr-2" />
                              View Full {item.type === "email" ? "Draft" : "Post"}
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="max-w-2xl">
                            <DialogHeader>
                              <DialogTitle>
                                {item.type === "email" ? "Email Draft" : "Social Post"} Preview
                              </DialogTitle>
                            </DialogHeader>
                            <div className="mt-4">
                              {item.type === "email" && (
                                <div className="mb-4 space-y-1 text-sm">
                                  {item.recipient && <p><span className="text-text-muted">To:</span> {item.recipient}</p>}
                                  {item.subject && <p><span className="text-text-muted">Subject:</span> {item.subject}</p>}
                                </div>
                              )}
                              <div className="bg-zinc-900 rounded-lg p-4 max-h-96 overflow-y-auto">
                                <p className="whitespace-pre-wrap text-sm">{item.content}</p>
                              </div>
                            </div>
                          </DialogContent>
                        </Dialog>

                        <div className="flex-1" />

                        <Button
                          variant="success"
                          onClick={() => handleAction(item.id, "approve")}
                          disabled={processing === item.id}
                          className="min-w-[120px]"
                        >
                          <Check className="w-4 h-4 mr-2" />
                          {processing === item.id ? "Moving..." : "Approve"}
                        </Button>
                        <Button
                          variant="destructive"
                          onClick={() => handleAction(item.id, "reject")}
                          disabled={processing === item.id}
                          className="min-w-[120px]"
                        >
                          <X className="w-4 h-4 mr-2" />
                          Reject
                        </Button>
                      </div>
                    )}

                    {currentStatus !== "pending" && (
                      <div className="pt-4">
                        <Badge variant={currentStatus === "approved" ? "success" : "danger"}>
                          {currentStatus === "approved" ? "✓ Moved to Approved/" : "✕ Moved to Rejected/"}
                        </Badge>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </main>
    </div>
  );
}
