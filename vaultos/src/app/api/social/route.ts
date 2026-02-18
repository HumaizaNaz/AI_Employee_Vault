import { NextResponse } from "next/server";

export const dynamic = 'force-dynamic';

const FB_TOKEN = process.env.FACEBOOK_PAGE_ACCESS_TOKEN!;
const IG_ACCOUNT_ID = process.env.INSTAGRAM_ACCOUNT_ID!;
const IG_TOKEN = process.env.INSTAGRAM_USER_TOKEN!;
const GRAPH_URL = "https://graph.facebook.com/v18.0";

async function postToFacebook(message: string): Promise<{ success: boolean; postId?: string; error?: string }> {
  try {
    const res = await fetch(`${GRAPH_URL}/me/feed`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, access_token: FB_TOKEN }),
    });
    const data = await res.json();
    if (data.id) return { success: true, postId: data.id };
    return { success: false, error: data.error?.message || "Unknown error" };
  } catch (e: any) {
    return { success: false, error: e.message };
  }
}

async function postToInstagram(caption: string, imageUrl?: string): Promise<{ success: boolean; postId?: string; error?: string }> {
  try {
    // Instagram requires an image for posts
    const img = imageUrl || "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camponotus_flavomarginatus_ant.jpg/320px-Camponotus_flavomarginatus_ant.jpg";

    // Step 1: Create media container
    const containerRes = await fetch(`${GRAPH_URL}/${IG_ACCOUNT_ID}/media`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image_url: img, caption, access_token: IG_TOKEN }),
    });
    const containerData = await containerRes.json();
    if (!containerData.id) return { success: false, error: containerData.error?.message || "Container creation failed" };

    // Step 2: Publish
    const publishRes = await fetch(`${GRAPH_URL}/${IG_ACCOUNT_ID}/media_publish`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ creation_id: containerData.id, access_token: IG_TOKEN }),
    });
    const publishData = await publishRes.json();
    if (publishData.id) return { success: true, postId: publishData.id };
    return { success: false, error: publishData.error?.message || "Publish failed" };
  } catch (e: any) {
    return { success: false, error: e.message };
  }
}

export async function POST(request: Request) {
  try {
    const { message, platforms, imageUrl } = await request.json();

    if (!message?.trim()) {
      return NextResponse.json({ error: "Message is required" }, { status: 400 });
    }

    const results: Record<string, { success: boolean; postId?: string; error?: string }> = {};

    if (platforms.includes("facebook")) {
      results.facebook = await postToFacebook(message);
    }
    if (platforms.includes("instagram")) {
      results.instagram = await postToInstagram(message, imageUrl);
    }

    const allSuccess = Object.values(results).every((r) => r.success);
    const anySuccess = Object.values(results).some((r) => r.success);

    return NextResponse.json({
      success: anySuccess,
      allSuccess,
      results,
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

// GET: test connection
export async function GET() {
  try {
    const res = await fetch(`${GRAPH_URL}/me?access_token=${FB_TOKEN}&fields=name,id`);
    const data = await res.json();
    return NextResponse.json({
      facebook: data.error ? { connected: false, error: data.error.message } : { connected: true, name: data.name, id: data.id },
      instagram: { connected: !!IG_TOKEN && !!IG_ACCOUNT_ID, accountId: IG_ACCOUNT_ID },
    });
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
