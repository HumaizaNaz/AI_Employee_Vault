import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export const dynamic = 'force-dynamic';

const HEALTH_REPORT = path.join(process.cwd(), "..", "Signals", "health_report.md");

export async function GET() {
  try {
    // Read health report
    let healthStatus = {
      cloud: { status: "online", ip: "80.225.222.19" },
      cpu: 12,
      memory: { used: 680, total: 1024 },
      disk: { used: 4.2, total: 50 },
      pm2Processes: [
        { name: "cloud-orchestrator", status: "online", cpu: "0.1%", memory: "45 MB", restarts: 0 },
        { name: "health-monitor", status: "online", cpu: "0.0%", memory: "38 MB", restarts: 0 },
        { name: "sync-manager", status: "online", cpu: "0.0%", memory: "41 MB", restarts: 0 },
      ],
      recentActivity: [],
    };

    // Try to read health report if it exists
    if (fs.existsSync(HEALTH_REPORT)) {
      const content = fs.readFileSync(HEALTH_REPORT, "utf-8");
      
      // Parse the health report (simple parsing)
      const lines = content.split("\n");
      lines.forEach(line => {
        if (line.includes("CPU")) {
          const match = line.match(/(\d+)%/);
          if (match) healthStatus.cpu = parseInt(match[1]);
        }
        if (line.includes("Memory")) {
          const match = line.match(/(\d+)\/(\d+)/);
          if (match) {
            healthStatus.memory.used = parseInt(match[1]);
            healthStatus.memory.total = parseInt(match[2]);
          }
        }
      });
    }

    // Try to get PM2 process list (if PM2 is available)
    try {
      const { execSync } = require("child_process");
      const pm2Output = execSync("pm2 list --json", { encoding: "utf-8" });
      const processes = JSON.parse(pm2Output);
      
      healthStatus.pm2Processes = processes.map((p: any) => ({
        name: p.name,
        status: p.pm2_env?.status || "unknown",
        cpu: p.pm2_env?.cpu || "0%",
        memory: p.pm2_env?.memory || "0 MB",
        restarts: p.pm2_env?.restart_time || 0,
      }));
    } catch (e) {
      // PM2 not available or not installed, use mock data
      console.log("PM2 not available, using mock data");
    }

    return NextResponse.json(healthStatus);
  } catch (error) {
    console.error("Error reading cloud status:", error);
    return NextResponse.json(
      { error: "Failed to read cloud status" },
      { status: 500 }
    );
  }
}
