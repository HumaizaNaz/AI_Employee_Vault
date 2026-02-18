"use client";

import { Sidebar } from "@/components/Sidebar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { MessageCircle, Eye, Send } from "lucide-react";

const messages = [
  {
    id: 1,
    contact: "+1 234 567 8900",
    content: "Hi, I need help with my order",
    date: "2026-02-18 11:00",
    status: "pending",
    replyReady: true,
  },
  {
    id: 2,
    contact: "+1 987 654 3210",
    content: "What are your business hours?",
    date: "2026-02-18 10:30",
    status: "processed",
    replyReady: false,
  },
];

export default function WhatsAppPage() {
  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      
      <main className="ml-60 p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">WhatsApp Queue</h1>
            <p className="text-text-muted mt-1">WhatsApp Business Integration</p>
          </div>
          <Badge variant="warning">1 Pending</Badge>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-text-muted">
                Pending Replies
              </CardTitle>
              <MessageCircle className="w-5 h-5 text-warning" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-warning">1</div>
              <p className="text-xs text-text-muted mt-1">Needs response</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-text-muted">
                Processed
              </CardTitle>
              <MessageCircle className="w-5 h-5 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-success">8</div>
              <p className="text-xs text-text-muted mt-1">Last 7 days</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-text-muted">
                Replies Ready
              </CardTitle>
              <MessageCircle className="w-5 h-5 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-primary">1</div>
              <p className="text-xs text-text-muted mt-1">Pending approval</p>
            </CardContent>
          </Card>
        </div>

        {/* Messages Table */}
        <Card>
          <CardHeader>
            <CardTitle>All Messages</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Contact</TableHead>
                  <TableHead>Message</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Reply</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {messages.map((message) => (
                  <TableRow key={message.id}>
                    <TableCell className="font-medium">{message.contact}</TableCell>
                    <TableCell className="max-w-md truncate">{message.content}</TableCell>
                    <TableCell className="text-text-muted">{message.date}</TableCell>
                    <TableCell>
                      <Badge variant={message.status === "pending" ? "warning" : "success"}>
                        {message.status === "pending" ? "⚠ Pending" : "✓ Processed"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {message.replyReady ? (
                        <Badge variant="default">Ready</Badge>
                      ) : (
                        <span className="text-text-muted text-sm">—</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button variant="ghost" size="icon">
                          <Eye className="w-4 h-4" />
                        </Button>
                        {message.replyReady && (
                          <Button variant="default" size="icon">
                            <Send className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
