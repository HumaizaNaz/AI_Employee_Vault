import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export const dynamic = 'force-dynamic';

const APPROVALS_DIR = path.join(process.cwd(), "..", "Pending_Approval");

export async function GET() {
  try {
    if (!fs.existsSync(APPROVALS_DIR)) {
      return NextResponse.json({ approvals: [], error: "Approvals directory not found" });
    }

    const approvals: any[] = [];

    // Search for email drafts
    const emailDir = path.join(APPROVALS_DIR, "Email");
    if (fs.existsSync(emailDir)) {
      const files = fs.readdirSync(emailDir).filter(f => f.endsWith(".md"));
      files.forEach(file => {
        const content = fs.readFileSync(path.join(emailDir, file), "utf-8");
        const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)/);
        let metadata: Record<string, string> = {};
        let body = content;
        
        if (match) {
          const frontmatter = match[1];
          body = match[2];
          frontmatter.split("\n").forEach(line => {
            const [key, ...valueParts] = line.split(":");
            if (key && valueParts.length) {
              metadata[key.trim()] = valueParts.join(":").trim();
            }
          });
        }

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

    // Search for social media drafts
    const socialDir = path.join(APPROVALS_DIR, "Social");
    if (fs.existsSync(socialDir)) {
      const files = fs.readdirSync(socialDir).filter(f => f.endsWith(".md"));
      files.forEach(file => {
        const content = fs.readFileSync(path.join(socialDir, file), "utf-8");
        const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)/);
        let metadata: Record<string, string> = {};
        let body = content;
        
        if (match) {
          const frontmatter = match[1];
          body = match[2];
          frontmatter.split("\n").forEach(line => {
            const [key, ...valueParts] = line.split(":");
            if (key && valueParts.length) {
              metadata[key.trim()] = valueParts.join(":").trim();
            }
          });
        }

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
    return NextResponse.json(
      { error: "Failed to read approvals" },
      { status: 500 }
    );
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

    // Find the file and move it to appropriate directory
    const [type, fileName] = id.split("-");
    const fileNameWithExt = `${fileName}.md`;
    
    let sourceDir = "";
    if (type === "email") {
      sourceDir = path.join(APPROVALS_DIR, "Email");
    } else if (type === "social") {
      sourceDir = path.join(APPROVALS_DIR, "Social");
    }

    const sourcePath = path.join(sourceDir, fileNameWithExt);
    
    if (!fs.existsSync(sourcePath)) {
      return NextResponse.json({ error: "File not found" }, { status: 404 });
    }

    // Move to Approved or Rejected directory
    const targetDir = action === "approve" 
      ? path.join(process.cwd(), "..", "Approved")
      : path.join(process.cwd(), "..", "Rejected");
    
    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
    }

    const targetPath = path.join(targetDir, fileNameWithExt);
    fs.renameSync(sourcePath, targetPath);

    return NextResponse.json({ 
      success: true, 
      message: `Approval ${action}d successfully` 
    });
  } catch (error) {
    console.error("Error processing approval:", error);
    return NextResponse.json(
      { error: "Failed to process approval" },
      { status: 500 }
    );
  }
}
