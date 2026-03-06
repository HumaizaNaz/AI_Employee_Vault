"""
Health Monitor for AI Employee Cloud Deployment

Monitors all cloud processes, system resources, and creates health reports.
Auto-restarts failed processes via PM2.
"""

import os
import json
import time
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

VAULT_ROOT = Path(os.environ.get("VAULT_PATH", "/home/ubuntu/ai-employee-vault"))
CHECK_INTERVAL = int(os.environ.get("HEALTH_CHECK_INTERVAL", "300"))  # 5 minutes
SIGNALS_FOLDER = VAULT_ROOT / "Signals"
LOGS_FOLDER = VAULT_ROOT / "Logs"

SIGNALS_FOLDER.mkdir(parents=True, exist_ok=True)
LOGS_FOLDER.mkdir(parents=True, exist_ok=True)

# Processes we expect to be running on cloud
EXPECTED_PROCESSES = [
    "cloud-orchestrator",
    "gmail-watcher",
    "filesystem-watcher",
    "sync-manager",
]

# Thresholds
DISK_WARN_PERCENT = 85
MEMORY_WARN_PERCENT = 90
CPU_WARN_PERCENT = 95


def run_command(cmd: str) -> str:
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, Exception) as e:
        return f"ERROR: {e}"


def check_pm2_processes() -> dict:
    """Check PM2 process statuses."""
    output = run_command("pm2 jlist")
    results = {"healthy": [], "unhealthy": [], "missing": []}

    try:
        processes = json.loads(output) if output and not output.startswith("ERROR") else []
    except json.JSONDecodeError:
        processes = []

    running_names = set()
    for proc in processes:
        name = proc.get("name", "unknown")
        status = proc.get("pm2_env", {}).get("status", "unknown")
        running_names.add(name)

        if status == "online":
            results["healthy"].append({"name": name, "status": status,
                                       "uptime": proc.get("pm2_env", {}).get("pm_uptime", 0),
                                       "restarts": proc.get("pm2_env", {}).get("restart_time", 0)})
        else:
            results["unhealthy"].append({"name": name, "status": status})

    for expected in EXPECTED_PROCESSES:
        if expected not in running_names:
            results["missing"].append(expected)

    return results


def check_disk_space() -> dict:
    """Check disk usage."""
    total, used, free = shutil.disk_usage("/")
    percent_used = (used / total) * 100
    return {
        "total_gb": round(total / (1024**3), 1),
        "used_gb": round(used / (1024**3), 1),
        "free_gb": round(free / (1024**3), 1),
        "percent_used": round(percent_used, 1),
        "warning": percent_used > DISK_WARN_PERCENT
    }


def check_memory() -> dict:
    """Check memory usage."""
    mem_info = run_command("free -m 2>/dev/null")
    if mem_info.startswith("ERROR") or not mem_info:
        # Fallback for non-Linux
        return {"total_mb": 0, "used_mb": 0, "percent_used": 0, "warning": False}

    lines = mem_info.split('\n')
    if len(lines) >= 2:
        parts = lines[1].split()
        if len(parts) >= 3:
            total = int(parts[1])
            used = int(parts[2])
            percent = (used / total * 100) if total > 0 else 0
            return {
                "total_mb": total,
                "used_mb": used,
                "percent_used": round(percent, 1),
                "warning": percent > MEMORY_WARN_PERCENT
            }
    return {"total_mb": 0, "used_mb": 0, "percent_used": 0, "warning": False}


def check_cpu() -> dict:
    """Check CPU load average."""
    load_info = run_command("cat /proc/loadavg 2>/dev/null")
    if load_info.startswith("ERROR") or not load_info:
        return {"load_1m": 0, "load_5m": 0, "load_15m": 0, "warning": False}

    parts = load_info.split()
    if len(parts) >= 3:
        load_1 = float(parts[0])
        load_5 = float(parts[1])
        load_15 = float(parts[2])
        # Warning if 1-min load exceeds number of CPUs
        cpu_count = os.cpu_count() or 4
        return {
            "load_1m": load_1,
            "load_5m": load_5,
            "load_15m": load_15,
            "cpu_count": cpu_count,
            "warning": load_1 > cpu_count * 0.95
        }
    return {"load_1m": 0, "load_5m": 0, "load_15m": 0, "warning": False}


def restart_process(name: str) -> bool:
    """Restart a failed PM2 process."""
    print(f"[HEALTH] Restarting failed process: {name}")
    output = run_command(f"pm2 restart {name}")
    success = "ERROR" not in output
    if success:
        print(f"[HEALTH] Successfully restarted {name}")
    else:
        print(f"[HEALTH] Failed to restart {name}: {output}")
    return success


def write_health_report(processes: dict, disk: dict, memory: dict, cpu: dict, overall: str):
    """Write health report to Signals folder."""
    report_path = SIGNALS_FOLDER / "health_report.md"

    # Process status table
    proc_lines = []
    for p in processes["healthy"]:
        restarts = p.get("restarts", 0)
        proc_lines.append(f"| {p['name']} | ONLINE | {restarts} |")
    for p in processes["unhealthy"]:
        proc_lines.append(f"| {p['name']} | {p['status'].upper()} | - |")
    for name in processes["missing"]:
        proc_lines.append(f"| {name} | MISSING | - |")

    proc_table = "\n".join(proc_lines) if proc_lines else "| (no processes) | - | - |"

    report = f"""# Health Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Overall Status:** {overall}

## Processes

| Process | Status | Restarts |
|---------|--------|----------|
{proc_table}

## System Resources

### Disk
- Total: {disk['total_gb']} GB
- Used: {disk['used_gb']} GB ({disk['percent_used']}%)
- Free: {disk['free_gb']} GB
- Status: {"WARNING" if disk['warning'] else "OK"}

### Memory
- Total: {memory['total_mb']} MB
- Used: {memory['used_mb']} MB ({memory['percent_used']}%)
- Status: {"WARNING" if memory['warning'] else "OK"}

### CPU
- Load (1m/5m/15m): {cpu['load_1m']}/{cpu['load_5m']}/{cpu['load_15m']}
- Status: {"WARNING" if cpu['warning'] else "OK"}
"""

    report_path.write_text(report, encoding='utf-8')
    print(f"[HEALTH] Report written to {report_path}")


def write_critical_alert(message: str):
    """Write a critical alert signal for Local to pick up."""
    alert_path = SIGNALS_FOLDER / f"ALERT_CRITICAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    alert_data = {
        "type": "critical_alert",
        "timestamp": datetime.now().isoformat(),
        "source": "health_monitor",
        "message": message
    }
    alert_path.write_text(json.dumps(alert_data, indent=2), encoding='utf-8')
    print(f"[ALERT] Critical: {message}")


def log_health_check(overall: str, details: dict):
    """Log health check results."""
    log_file = LOGS_FOLDER / f"health_log_{datetime.now().strftime('%Y-%m-%d')}.json"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "overall": overall,
        "details": details
    }

    logs = []
    if log_file.exists():
        try:
            logs = json.loads(log_file.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            pass

    logs.append(entry)
    log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')


def run_health_check():
    """Run a single health check cycle."""
    print(f"\n[HEALTH] Running health check at {datetime.now().strftime('%H:%M:%S')}")

    # Check all systems
    processes = check_pm2_processes()
    disk = check_disk_space()
    memory = check_memory()
    cpu = check_cpu()

    # Determine overall status
    critical_issues = []

    if processes["unhealthy"]:
        for p in processes["unhealthy"]:
            critical_issues.append(f"Process {p['name']} is {p['status']}")
            restart_process(p["name"])

    if processes["missing"]:
        for name in processes["missing"]:
            critical_issues.append(f"Process {name} is missing")

    if disk["warning"]:
        critical_issues.append(f"Disk usage at {disk['percent_used']}%")

    if memory["warning"]:
        critical_issues.append(f"Memory usage at {memory['percent_used']}%")

    if cpu["warning"]:
        critical_issues.append(f"CPU load at {cpu['load_1m']}")

    if critical_issues:
        overall = "CRITICAL" if processes["unhealthy"] or processes["missing"] else "WARNING"
        write_critical_alert("; ".join(critical_issues))
    else:
        overall = "HEALTHY"

    # Write report and log
    write_health_report(processes, disk, memory, cpu, overall)
    log_health_check(overall, {
        "processes": processes,
        "disk": disk,
        "memory": memory,
        "cpu": cpu,
        "issues": critical_issues
    })

    print(f"[HEALTH] Status: {overall}")
    return overall


def run_monitor():
    """Main monitoring loop."""
    print("=" * 50)
    print("  HEALTH MONITOR - AI Employee Cloud")
    print(f"  Check interval: {CHECK_INTERVAL}s")
    print("=" * 50)

    while True:
        try:
            run_health_check()
        except Exception as e:
            print(f"[HEALTH ERROR] {e}")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run_health_check()
    else:
        run_monitor()
