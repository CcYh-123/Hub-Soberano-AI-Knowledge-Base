import { NextResponse } from "next/server";
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
    const cookieStore = await cookies();
    const supabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
            cookies: {
                getAll() {
                    return cookieStore.getAll();
                },
                setAll(cookiesToSet) {
                    try {
                        cookiesToSet.forEach(({ name, value, options }) =>
                            cookieStore.set(name, value, options)
                        );
                    } catch (error) {}
                },
            },
        }
    );

    try {
        const { sku, old_price, new_price, gap_recovered } = await req.json();

        if (!sku || new_price === undefined) {
            return NextResponse.json({ success: false, message: "Missing data" }, { status: 400 });
        }

        const { data, error } = await supabase
            .from("price_logs")
            .insert([
                { 
                    sku, 
                    old_price, 
                    new_price, 
                    gap_recovered: gap_recovered || 0
                }
            ])
            .select();

        if (error) throw error;

        // Opcional: Actualizar también la tabla de productos si existe el SKU
        await supabase
            .from("products")
            .update({ price: new_price })
            .eq("name", sku); // Asumiendo que name es el SKU en productos

        return NextResponse.json({ 
            success: true, 
            message: `Precio aplicado: ${sku}`, 
            data 
        });

    } catch (err: any) {
        console.error("[apply-price] Error:", err.message);
        return NextResponse.json({ success: false, message: err.message }, { status: 500 });
    }
}
