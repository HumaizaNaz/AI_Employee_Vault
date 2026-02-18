import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export const dynamic = 'force-dynamic';

const WA_DIR = path.join(process.cwd(), "..", "Needs_Action", "WhatsApp");
const DONE_DIR = path.join(process.cwd(), "..", "Done");

export async function GET() {
  try {
    if (!fs.existsSync(WA_DIR)) {
      return NextResponse.json({ messages: [] });
    }

    const files = fs.readdirSync(WA_DIR).filter((f) => f.endsWith(".md"));

    const messages = files.map((file) => {
      const content = fs.readFileSync(path.join(WA_DIR, file), "utf-8");
      const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)/);
      let metadata: Record<string, string> = {};
      let body = content;

      if (match) {
        match[1].split("\n").forEach((line) => {
          const [key, ...val] = line.split(":");
          if (key && val.length) metadata[key.trim()] = val.join(":").trim();
        });
        body = match[2];
      }

      return {
        id: file.replace(".md", ""),
        from: metadata.from || "Unknown",
        message: metadata.message || body.trim().slice(0, 200),
        date: metadata.date || metadata.received || "",
        status: metadata.status || "needs_action",
        keywords: metadata.keywords || "",
      };
    });

    return NextResponse.json({ messages });
  } catch (error) {
    return NextResponse.json({ error: "Failed to read WhatsApp messages", messages: [] });
  }
}

export async function POST(request: Request) {
  try {
    const { id } = await request.json();
    const src = path.join(WA_DIR, `${id}.md`);
    if (!fs.existsSync(src)) return NextResponse.json({ error: "File not found" }, { status: 404 });
    if (!fs.existsSync(DONE_DIR)) fs.mkdirSync(DONE_DIR, { recursive: true });
    fs.renameSync(src, path.join(DONE_DIR, `${id}.md`));
    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json({ error: "Failed to process message" }, { status: 500 });
  }
}
