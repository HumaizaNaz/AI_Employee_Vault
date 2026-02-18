import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export const dynamic = 'force-dynamic';

const LOGS_DIR = path.join(process.cwd(), "..", "Logs");

export async function GET() {
  try {
    if (!fs.existsSync(LOGS_DIR)) {
      return NextResponse.json({ logs: [], error: "Logs directory not found" });
    }

    // Read all JSON log files
    const files = fs.readdirSync(LOGS_DIR).filter(file => file.endsWith(".json"));
    
    const allLogs: any[] = [];
    
    files.forEach(file => {
      const filePath = path.join(LOGS_DIR, file);
      const content = fs.readFileSync(filePath, "utf-8");
      
      try {
        const logData = JSON.parse(content);
        
        // Handle both array and single object logs
        const logs = Array.isArray(logData) ? logData : [logData];
        
        logs.forEach((log: any, index: number) => {
          allLogs.push({
            id: `${file}-${index}`,
            timestamp: log.timestamp || log.date || log.created || "",
            level: log.level || log.type || "info",
            source: log.source || log.service || file.replace(".json", ""),
            message: log.message || log.msg || log.text || "",
          });
        });
      } catch (e) {
        // Skip invalid JSON files
        console.error(`Error parsing ${file}:`, e);
      }
    });

    // Sort by timestamp (newest first)
    allLogs.sort((a, b) => {
      const dateA = new Date(a.timestamp || 0);
      const dateB = new Date(b.timestamp || 0);
      return dateB.getTime() - dateA.getTime();
    });

    return NextResponse.json({ logs: allLogs });
  } catch (error) {
    console.error("Error reading logs:", error);
    return NextResponse.json(
      { error: "Failed to read logs" },
      { status: 500 }
    );
  }
}
