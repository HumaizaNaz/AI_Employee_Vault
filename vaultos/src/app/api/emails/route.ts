import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export const dynamic = 'force-dynamic';

// Path to the Needs_Action/Email directory
const EMAILS_DIR = path.join(process.cwd(), "..", "Needs_Action", "Email");

export async function GET() {
  try {
    // Check if directory exists
    if (!fs.existsSync(EMAILS_DIR)) {
      return NextResponse.json({ emails: [], error: "Email directory not found" });
    }

    // Read all markdown files
    const files = fs.readdirSync(EMAILS_DIR).filter(file => file.endsWith(".md"));
    
    const emails = files.map(file => {
      const filePath = path.join(EMAILS_DIR, file);
      const content = fs.readFileSync(filePath, "utf-8");
      
      // Parse frontmatter and content
      const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)/);
      let metadata: Record<string, string> = {};
      let body = content;
      
      if (match) {
        const frontmatter = match[1];
        body = match[2];
        
        // Parse frontmatter key-value pairs
        frontmatter.split("\n").forEach(line => {
          const [key, ...valueParts] = line.split(":");
          if (key && valueParts.length) {
            metadata[key.trim()] = valueParts.join(":").trim();
          }
        });
      }
      
      return {
        id: file.replace(".md", ""),
        fileName: file,
        from: metadata.from || "Unknown",
        subject: metadata.subject || file,
        date: metadata.date || metadata.created || "",
        status: "needs_action",
        draftReady: body.includes("[DRAFT]") || body.includes("draft"),
        content: body,
      };
    });

    return NextResponse.json({ emails });
  } catch (error) {
    console.error("Error reading emails:", error);
    return NextResponse.json(
      { error: "Failed to read emails" },
      { status: 500 }
    );
  }
}
