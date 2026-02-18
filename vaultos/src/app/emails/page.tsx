"use client";

import { Sidebar } from "@/components/Sidebar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Mail, Eye, RefreshCw, Inbox } from "lucide-react";
import { useData } from "@/hooks/useData";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface Email {
  id: string;
  from: string;
  subject: string;
  date: string;
  status: string;
  draftReady: boolean;
  content: string;
}

export default function EmailsPage() {
  const { data, loading, refetch } = useData<{ emails: Email[] }>("/api/emails");
  const emails = data?.emails || [];
  const needsAction = emails.filter((e) => e.status === "needs_action").length;
  const draftsReady = emails.filter((e) => e.draftReady).length;

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <main className="ml-60 p-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">Email Queue</h1>
            <p className="text-text-muted mt-1">Vault: Needs_Action/Email/</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" onClick={refetch}>
              <RefreshCw className="w-4 h-4" />
            </Button>
            <Badge variant={needsAction > 0 ? "warning" : "success"}>
              {loading ? "..." : `${emails.length} Items`}
            </Badge>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-text-muted">Needs Action</CardTitle>
              <Mail className="w-5 h-5 text-warning" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-warning">{loading ? "—" : needsAction}</div>
              <p className="text-xs text-text-muted mt-1">In Needs_Action/Email/</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-text-muted">Total in Queue</CardTitle>
              <Mail className="w-5 h-5 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-success">{loading ? "—" : emails.length}</div>
              <p className="text-xs text-text-muted mt-1">All email files</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-text-muted">Drafts Ready</CardTitle>
              <Mail className="w-5 h-5 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-primary">{loading ? "—" : draftsReady}</div>
              <p className="text-xs text-text-muted mt-1">Pending approval</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>All Emails</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center h-32 text-text-muted">Loading from vault...</div>
            ) : emails.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-32 text-text-muted gap-2">
                <Inbox className="w-8 h-8" />
                <p>No emails in queue — vault is clear</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>From</TableHead>
                    <TableHead>Subject</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Draft</TableHead>
                    <TableHead className="text-right">View</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {emails.map((email) => (
                    <TableRow key={email.id}>
                      <TableCell className="font-medium max-w-[180px] truncate">{email.from}</TableCell>
                      <TableCell className="max-w-[200px] truncate">{email.subject}</TableCell>
                      <TableCell className="text-text-muted text-sm">{email.date || "—"}</TableCell>
                      <TableCell>
                        <Badge variant={email.status === "needs_action" ? "warning" : "success"}>
                          {email.status === "needs_action" ? "⚠ Needs Action" : "✓ Done"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {email.draftReady ? (
                          <Badge variant="success">Ready</Badge>
                        ) : (
                          <span className="text-text-muted text-sm">—</span>
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <Eye className="w-4 h-4" />
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="max-w-2xl">
                            <DialogHeader>
                              <DialogTitle>{email.subject}</DialogTitle>
                            </DialogHeader>
                            <div className="text-sm space-y-1 mb-4">
                              <p><span className="text-text-muted">From:</span> {email.from}</p>
                              <p><span className="text-text-muted">Date:</span> {email.date || "—"}</p>
                            </div>
                            <div className="bg-zinc-900 rounded-lg p-4 max-h-96 overflow-y-auto">
                              <p className="whitespace-pre-wrap text-sm">{email.content}</p>
                            </div>
                          </DialogContent>
                        </Dialog>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
