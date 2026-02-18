import { NextResponse } from "next/server";

export const dynamic = 'force-dynamic';

const ODOO_MCP = "http://localhost:3006";

export async function GET() {
  try {
    const [invoicesRes, partnersRes] = await Promise.all([
      fetch(`${ODOO_MCP}/search-invoices`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain: [], limit: 50 }),
      }),
      fetch(`${ODOO_MCP}/search-partners`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain: [], limit: 10 }),
      }),
    ]);

    const invoicesData = await invoicesRes.json();
    const partnersData = await partnersRes.json();

    const invoices = invoicesData.invoices || [];
    const draft = invoices.filter((i: any) => i.state === "draft").length;
    const paid = invoices.filter((i: any) => i.state === "posted").length;
    const revenue = invoices
      .filter((i: any) => i.state === "posted")
      .reduce((sum: number, i: any) => sum + (i.amount_total || 0), 0);

    return NextResponse.json({
      invoices,
      partners: partnersData.partners || [],
      stats: { draft, paid, revenue },
    });
  } catch (error) {
    return NextResponse.json({ error: "Odoo MCP not reachable", invoices: [], stats: { draft: 0, paid: 0, revenue: 0 } });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const res = await fetch(`${ODOO_MCP}/create-invoice`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error: "Failed to create invoice" }, { status: 500 });
  }
}
