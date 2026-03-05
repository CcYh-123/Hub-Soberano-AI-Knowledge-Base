import { NextResponse } from "next/server";

export async function POST(req: Request) {
    try {
        const { sku, new_price } = await req.json();
        if (!sku || !new_price) {
            return NextResponse.json({ success: false, message: "Missing sku or new_price" }, { status: 400 });
        }
        console.log(`[apply-price] ${new Date().toISOString()} | SKU: ${sku} | Precio: $${new_price}`);
        return NextResponse.json({ success: true, message: `Price queued for ${sku}`, sku, new_price, queued_at: new Date().toISOString() });
    } catch (err) {
        console.error("[apply-price] Error:", err);
        return NextResponse.json({ success: false, message: "Internal error" }, { status: 500 });
    }
}
