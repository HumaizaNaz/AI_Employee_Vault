"use client";

import { useState, useEffect } from "react";
import { Sidebar } from "@/components/Sidebar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Share2, Facebook, Instagram, Twitter, Send, CheckCircle2, XCircle, Loader2 } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface PlatformStatus {
  facebook: { connected: boolean; name?: string; error?: string };
  instagram: { connected: boolean; accountId?: string };
}

interface PostResult {
  success: boolean;
  postId?: string;
  error?: string;
}

interface PostHistory {
  id: number;
  message: string;
  platforms: string[];
  timestamp: string;
  results: Record<string, PostResult>;
}

export default function SocialPage() {
  const [status, setStatus] = useState<PlatformStatus | null>(null);
  const [statusLoading, setStatusLoading] = useState(true);
  const [open, setOpen] = useState(false);

  // Post form state
  const [message, setMessage] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [platforms, setPlatforms] = useState<string[]>(["facebook", "instagram"]);
  const [posting, setPosting] = useState(false);
  const [postResult, setPostResult] = useState<{ success: boolean; results: Record<string, PostResult> } | null>(null);
  const [history, setHistory] = useState<PostHistory[]>([]);

  useEffect(() => {
    fetch("/api/social")
      .then((r) => r.json())
      .then((d) => setStatus(d))
      .finally(() => setStatusLoading(false));
  }, []);

  const togglePlatform = (p: string) => {
    setPlatforms((prev) =>
      prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p]
    );
  };

  const handlePost = async () => {
    if (!message.trim() || platforms.length === 0) return;
    setPosting(true);
    setPostResult(null);
    try {
      const res = await fetch("/api/social", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, platforms, imageUrl: imageUrl || undefined }),
      });
      const data = await res.json();
      setPostResult(data);
      if (data.success) {
        setHistory((prev) => [
          {
            id: Date.now(),
            message,
            platforms,
            timestamp: new Date().toLocaleString(),
            results: data.results,
          },
          ...prev,
        ]);
        if (data.allSuccess) {
          setTimeout(() => {
            setOpen(false);
            setMessage("");
            setImageUrl("");
            setPostResult(null);
          }, 2000);
        }
      }
    } catch (e) {
      setPostResult({ success: false, results: { error: { success: false, error: "Network error" } } });
    } finally {
      setPosting(false);
    }
  };

  const charCount = message.length;

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <main className="ml-60 p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">Social Media</h1>
            <p className="text-text-muted mt-1">Post directly to Facebook & Instagram</p>
          </div>
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button>
                <Share2 className="w-4 h-4 mr-2" />
                Create Post
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle>New Social Media Post</DialogTitle>
              </DialogHeader>

              <div className="space-y-5 mt-2">
                {/* Platform selector */}
                <div>
                  <p className="text-sm text-text-muted mb-3">Select platforms:</p>
                  <div className="flex gap-3">
                    <button
                      onClick={() => togglePlatform("facebook")}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all ${
                        platforms.includes("facebook")
                          ? "border-blue-500 bg-blue-500/10 text-blue-400"
                          : "border-border text-text-muted hover:border-zinc-600"
                      }`}
                    >
                      <Facebook className="w-4 h-4" />
                      <span className="text-sm font-medium">Facebook</span>
                    </button>
                    <button
                      onClick={() => togglePlatform("instagram")}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all ${
                        platforms.includes("instagram")
                          ? "border-pink-500 bg-pink-500/10 text-pink-400"
                          : "border-border text-text-muted hover:border-zinc-600"
                      }`}
                    >
                      <Instagram className="w-4 h-4" />
                      <span className="text-sm font-medium">Instagram</span>
                    </button>
                    <button
                      disabled
                      className="flex items-center gap-2 px-4 py-2 rounded-lg border border-border text-text-muted opacity-40 cursor-not-allowed"
                      title="Credits reset March 1"
                    >
                      <Twitter className="w-4 h-4" />
                      <span className="text-sm">Twitter</span>
                    </button>
                  </div>
                </div>

                {/* Message input */}
                <div>
                  <label className="text-sm text-text-muted block mb-2">Your message</label>
                  <textarea
                    className="w-full bg-zinc-900 border border-border rounded-lg px-4 py-3 text-sm resize-none focus:outline-none focus:border-primary transition-colors"
                    rows={5}
                    placeholder="Write your post here..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    maxLength={2000}
                  />
                  <p className={`text-xs mt-1 text-right ${charCount > 1800 ? "text-warning" : "text-text-muted"}`}>
                    {charCount}/2000
                  </p>
                </div>

                {/* Image URL (Instagram) */}
                {platforms.includes("instagram") && (
                  <div>
                    <label className="text-sm text-text-muted block mb-2">
                      Image URL <span className="text-xs">(Instagram requires an image)</span>
                    </label>
                    <input
                      className="w-full bg-zinc-900 border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary transition-colors"
                      placeholder="https://example.com/image.jpg (optional — uses default if empty)"
                      value={imageUrl}
                      onChange={(e) => setImageUrl(e.target.value)}
                    />
                  </div>
                )}

                {/* Result feedback */}
                {postResult && (
                  <div className="space-y-2">
                    {Object.entries(postResult.results).map(([platform, result]) => (
                      <div
                        key={platform}
                        className={`flex items-center gap-3 px-4 py-3 rounded-lg ${
                          result.success ? "bg-success/10 border border-success/30" : "bg-danger/10 border border-danger/30"
                        }`}
                      >
                        {result.success ? (
                          <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0" />
                        ) : (
                          <XCircle className="w-5 h-5 text-danger flex-shrink-0" />
                        )}
                        <div>
                          <p className="text-sm font-medium capitalize">{platform}</p>
                          {result.success ? (
                            <p className="text-xs text-success">Posted! ID: {result.postId}</p>
                          ) : (
                            <p className="text-xs text-danger">{result.error}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Post button */}
                <Button
                  onClick={handlePost}
                  disabled={posting || !message.trim() || platforms.length === 0}
                  className="w-full"
                >
                  {posting ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Posting...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4 mr-2" />
                      Post to {platforms.map((p) => p.charAt(0).toUpperCase() + p.slice(1)).join(" + ")}
                    </>
                  )}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Platform Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-text-muted flex items-center gap-2">
                <Facebook className="w-4 h-4 text-blue-400" /> Facebook
              </CardTitle>
            </CardHeader>
            <CardContent>
              {statusLoading ? (
                <Badge variant="default">Checking...</Badge>
              ) : status?.facebook?.connected ? (
                <>
                  <Badge variant="success">✓ Connected</Badge>
                  {status.facebook.name && (
                    <p className="text-xs text-text-muted mt-2">{status.facebook.name}</p>
                  )}
                </>
              ) : (
                <Badge variant="danger">Disconnected</Badge>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-text-muted flex items-center gap-2">
                <Instagram className="w-4 h-4 text-pink-400" /> Instagram
              </CardTitle>
            </CardHeader>
            <CardContent>
              {statusLoading ? (
                <Badge variant="default">Checking...</Badge>
              ) : status?.instagram?.connected ? (
                <>
                  <Badge variant="success">✓ Connected</Badge>
                  <p className="text-xs text-text-muted mt-2">Business Account Linked</p>
                </>
              ) : (
                <Badge variant="danger">Disconnected</Badge>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-text-muted flex items-center gap-2">
                <Twitter className="w-4 h-4 text-blue-400" /> Twitter / X
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Badge variant="warning">Credits Reset Mar 1</Badge>
              <p className="text-xs text-text-muted mt-2">Auth verified @NazHumo</p>
            </CardContent>
          </Card>
        </div>

        {/* Post History */}
        <Card>
          <CardHeader>
            <CardTitle>Post History (This Session)</CardTitle>
          </CardHeader>
          <CardContent>
            {history.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-32 text-text-muted gap-2">
                <Share2 className="w-8 h-8" />
                <p className="text-sm">No posts yet — use "Create Post" to get started</p>
              </div>
            ) : (
              <div className="space-y-4">
                {history.map((post) => (
                  <div key={post.id} className="bg-zinc-900 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {post.platforms.includes("facebook") && (
                          <Facebook className="w-4 h-4 text-blue-400" />
                        )}
                        {post.platforms.includes("instagram") && (
                          <Instagram className="w-4 h-4 text-pink-400" />
                        )}
                        <span className="text-xs text-text-muted">{post.timestamp}</span>
                      </div>
                      <div className="flex gap-2">
                        {Object.entries(post.results).map(([platform, r]) => (
                          <Badge key={platform} variant={r.success ? "success" : "danger"}>
                            {r.success ? `✓ ${platform}` : `✕ ${platform}`}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <p className="text-sm whitespace-pre-wrap">{post.message}</p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
