import { NextResponse } from "next/server";

const TENANT_MAP: Record<string, string> = {
    "demo-saas": "3947b9dc-7e89-4a05-a659-46e8ccdde558",
    "default-client": "efe488ef-c93b-4719-8941-52bacbdce2e9",
};

export async function GET(
    req: Request,
    { params }: { params: { slug: string; sector: string } }
) {
    try {
        const { slug, sector } = params;
        const tenantId = TENANT_MAP[slug] ?? slug;

        // Leer DB via API interna de Python — fallback a datos simulados
        const res = await fetch(
            `http://localhost:8000/trends/${tenantId}/${sector}`
        ).catch(() => null);

        if (res && res.ok) {
            const data = await res.json();
            return NextResponse.json(data);
        }

        // Fallback: datos simulados basados en los precios reales conocidos
        const baseprices: Record<string, number> = {
            pharmacy: 1650,
            fashion: 8500,
            default: 1000,
        };
        const base = baseprices[sector] ?? 1000;
        const now = Date.now();

        const fallback = Array.from({ length: 14 }, (_, i) => ({
            timestamp: new Date(now - (13 - i) * 86400000).toISOString(),
            price: Math.round(base + (Math.random() - 0.3) * base * 0.08),
        }));

        return NextResponse.json(fallback);

    } catch (err) {
        console.error("[trends] Error:", err);
        return NextResponse.json([], { status: 500 });
    }
}
