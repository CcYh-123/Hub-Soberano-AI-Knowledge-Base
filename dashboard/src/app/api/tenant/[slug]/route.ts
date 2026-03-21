import { NextResponse, type NextRequest } from 'next/server';
export const dynamic = "force-dynamic";

const API_BASE = process.env.PYTHON_API_URL || "http://localhost:8000";

export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ slug: string }> }
) {
    const { slug } = await params;

    try {
        const response = await fetch(`${API_BASE}/tenant/${slug}`, {
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
            return NextResponse.json({ id: slug, name: "Enterprise Hub", slug: slug, tier: "pro" });
        }

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("Tenant proxy error:", error);
        return NextResponse.json({ id: slug, name: "Enterprise Hub", slug: slug, tier: "pro" });
    }
}
