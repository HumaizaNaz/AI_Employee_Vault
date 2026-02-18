import { NextResponse } from "next/server";

export const dynamic = 'force-dynamic';

const FB_TOKEN = process.env.FACEBOOK_PAGE_ACCESS_TOKEN!;
const IG_ACCOUNT_ID = process.env.INSTAGRAM_ACCOUNT_ID!;
const IG_TOKEN = process.env.INSTAGRAM_USER_TOKEN!;
const LI_TOKEN = process.env.LINKEDIN_ACCESS_TOKEN;
const LI_URN = process.env.LINKEDIN_MEMBER_URN;
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
    const img = imageUrl || "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camponotus_flavomarginatus_ant.jpg/320px-Camponotus_flavomarginatus_ant.jpg";

    const containerRes = await fetch(`${GRAPH_URL}/${IG_ACCOUNT_ID}/media`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image_url: img, caption, access_token: IG_TOKEN }),
    });
    const containerData = await containerRes.json();
    if (!containerData.id) return { success: false, error: containerData.error?.message || "Container creation failed" };

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

async function postToLinkedIn(text: string): Promise<{ success: boolean; postId?: string; error?: string }> {
  try {
    if (!LI_TOKEN || !LI_URN) {
      return { success: false, error: "LinkedIn token not configured" };
    }
    const res = await fetch("https://api.linkedin.com/v2/ugcPosts", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${LI_TOKEN}`,
        "X-Restli-Protocol-Version": "2.0.0",
      },
      body: JSON.stringify({
        author: `urn:li:person:${LI_URN}`,
        lifecycleState: "PUBLISHED",
        specificContent: {
          "com.linkedin.ugc.ShareContent": {
            shareCommentary: { text },
            shareMediaCategory: "NONE",
          },
        },
        visibility: {
          "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC",
        },
      }),
    });
    const data = await res.json();
    if (res.ok && data.id) return { success: true, postId: data.id };
    return { success: false, error: data.message || data.status || "LinkedIn post failed" };
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
    if (platforms.includes("linkedin")) {
      results.linkedin = await postToLinkedIn(message);
    }

    const allSuccess = Object.values(results).every((r) => r.success);
    const anySuccess = Object.values(results).some((r) => r.success);

    return NextResponse.json({ success: anySuccess, allSuccess, results });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

// GET: test connection status
export async function GET() {
  try {
    const res = await fetch(`${GRAPH_URL}/me?access_token=${FB_TOKEN}&fields=name,id`);
    const data = await res.json();

    // Check LinkedIn profile
    let linkedinStatus: { connected: boolean; name?: string; error?: string } = { connected: false };
    if (LI_TOKEN && LI_URN) {
      try {
        const liRes = await fetch("https://api.linkedin.com/v2/me", {
          headers: { Authorization: `Bearer ${LI_TOKEN}` },
        });
        const liData = await liRes.json();
        if (liRes.ok) {
          linkedinStatus = {
            connected: true,
            name: `${liData.localizedFirstName} ${liData.localizedLastName}`,
          };
        } else {
          linkedinStatus = { connected: false, error: liData.message || "Token invalid" };
        }
      } catch {
        linkedinStatus = { connected: false, error: "Cannot reach LinkedIn" };
      }
    } else {
      linkedinStatus = { connected: false, error: "Token not configured" };
    }

    return NextResponse.json({
      facebook: data.error ? { connected: false, error: data.error.message } : { connected: true, name: data.name, id: data.id },
      instagram: { connected: !!IG_TOKEN && !!IG_ACCOUNT_ID, accountId: IG_ACCOUNT_ID },
      linkedin: linkedinStatus,
    });
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
