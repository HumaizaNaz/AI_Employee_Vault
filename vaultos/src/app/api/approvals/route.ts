import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export const dynamic = 'force-dynamic';

const APPROVALS_DIR = path.join(process.cwd(), "..", "Pending_Approval");
const MCP_EMAIL_URL = "http://localhost:3005/send-email";
const MCP_API_KEY = "AIEMCP_RANDOM_KEY_v27RzD0xW4jL9yP7cFqA8sH3nB5gK6tE";

function parseMarkdown(filePath: string) {
  const content = fs.readFileSync(filePath, "utf-8");
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)/);
  let metadata: Record<string, string> = {};
  let body = content;
  if (match) {
    match[1].split("\n").forEach(line => {
      const [key, ...valueParts] = line.split(":");
      if (key && valueParts.length) {
        metadata[key.trim()] = valueParts.join(":").trim();
      }
    });
    body = match[2];
  }
  return { metadata, body };
}

export async function GET() {
  try {
    if (!fs.existsSync(APPROVALS_DIR)) {
      return NextResponse.json({ approvals: [], error: "Approvals directory not found" });
    }

    const approvals: any[] = [];

    // Email drafts
    const emailDir = path.join(APPROVALS_DIR, "Email");
    if (fs.existsSync(emailDir)) {
      const files = fs.readdirSync(emailDir).filter(f => f.endsWith(".md"));
      files.forEach(file => {
        const { metadata, body } = parseMarkdown(path.join(emailDir, file));
        approvals.push({
          id: `email-${file.replace(".md", "")}`,
          type: "email",
          status: "pending",
          created: metadata.date || metadata.created || "",
          recipient: metadata.to || metadata.recipient || "",
          subject: metadata.subject || file,
          content: body,
        });
      });
    }

    // Social drafts
    const socialDir = path.join(APPROVALS_DIR, "Social");
    if (fs.existsSync(socialDir)) {
      const files = fs.readdirSync(socialDir).filter(f => f.endsWith(".md"));
      files.forEach(file => {
        const { metadata, body } = parseMarkdown(path.join(socialDir, file));
        approvals.push({
          id: `social-${file.replace(".md", "")}`,
          type: "social",
          status: "pending",
          created: metadata.date || metadata.created || "",
          platform: metadata.platform || "Facebook + Instagram",
          content: body,
        });
      });
    }

    return NextResponse.json({ approvals });
  } catch (error) {
    console.error("Error reading approvals:", error);
    return NextResponse.json({ error: "Failed to read approvals" }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const { id, action } = await request.json();

    if (!id || !action || !["approve", "reject"].includes(action)) {
      return NextResponse.json(
        { error: "Invalid request. Required: id and action (approve/reject)" },
        { status: 400 }
      );
    }

    const dashIndex = id.indexOf("-");
    const type = id.substring(0, dashIndex);
    const fileName = id.substring(dashIndex + 1);
    const fileNameWithExt = `${fileName}.md`;

    let sourceDir = "";
    if (type === "email") sourceDir = path.join(APPROVALS_DIR, "Email");
    else if (type === "social") sourceDir = path.join(APPROVALS_DIR, "Social");

    const sourcePath = path.join(sourceDir, fileNameWithExt);
    if (!fs.existsSync(sourcePath)) {
      return NextResponse.json({ error: "File not found" }, { status: 404 });
    }

    const { metadata, body } = parseMarkdown(sourcePath);

    if (action === "approve" && type === "email") {
      // Send email immediately via MCP
      const to = metadata.to || metadata.recipient || "";
      const subject = metadata.subject || "No Subject";

      // Extract plain text body (strip markdown headers)
      const textBody = body
        .replace(/^##.*$/gm, "")
        .replace(/\*\*.*?\*\*/g, "")
        .replace(/- \[.*?\]/g, "")
        .trim();

      try {
        const mcpRes = await fetch(MCP_EMAIL_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-api-key": MCP_API_KEY,
          },
          body: JSON.stringify({ to, subject, text: textBody }),
        });

        const mcpData = await mcpRes.json();

        if (!mcpRes.ok || !mcpData.success) {
          return NextResponse.json({
            success: false,
            error: `Email MCP error: ${mcpData.error || "Unknown error"}`,
          }, { status: 500 });
        }

        // Move to Done after successful send
        const doneDir = path.join(process.cwd(), "..", "Done", "Email");
        if (!fs.existsSync(doneDir)) fs.mkdirSync(doneDir, { recursive: true });
        fs.renameSync(sourcePath, path.join(doneDir, fileNameWithExt));

        return NextResponse.json({
          success: true,
          message: `Email sent to ${to} and moved to Done`,
          messageId: mcpData.messageId,
        });

      } catch (mcpError: any) {
        return NextResponse.json({
          success: false,
          error: `Cannot reach Email MCP (localhost:3005): ${mcpError.message}`,
        }, { status: 500 });
      }
    }

    // For reject OR social approve — just move to Approved/Rejected folder
    const targetDir = action === "approve"
      ? path.join(process.cwd(), "..", "Approved")
      : path.join(process.cwd(), "..", "Rejected");

    if (!fs.existsSync(targetDir)) fs.mkdirSync(targetDir, { recursive: true });
    fs.renameSync(sourcePath, path.join(targetDir, fileNameWithExt));

    return NextResponse.json({
      success: true,
      message: `${action === "approve" ? "Approved" : "Rejected"} successfully`,
    });

  } catch (error: any) {
    console.error("Error processing approval:", error);
    return NextResponse.json({ error: "Failed to process approval" }, { status: 500 });
  }
}
