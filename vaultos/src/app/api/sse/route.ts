import { NextRequest } from "next/server";

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      // Send initial connection message
      controller.enqueue(
        encoder.encode(`data: ${JSON.stringify({ type: "connected", message: "SSE connected" })}\n\n`)
      );

      // Send updates every 30 seconds
      const interval = setInterval(() => {
        // In production, this would read from actual vault files
        const data = {
          type: "update",
          timestamp: new Date().toISOString(),
          emails: Math.floor(Math.random() * 5),
          approvals: Math.floor(Math.random() * 3),
          whatsapp: Math.floor(Math.random() * 2),
        };
        
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify(data)}\n\n`)
        );
      }, 30000);

      // Clean up on client disconnect
      request.signal.addEventListener("abort", () => {
        clearInterval(interval);
        controller.close();
      });
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
    },
  });
}
