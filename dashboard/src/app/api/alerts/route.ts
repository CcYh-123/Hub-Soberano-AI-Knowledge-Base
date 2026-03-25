import { NextResponse, type NextRequest } from 'next/server';
export const dynamic = "force-dynamic";
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

export async function GET(request: NextRequest) {
    try {
        const cookieStore = await cookies()
        const supabase = createServerClient(
            process.env.VITE_SUPABASE_URL!,
            process.env.VITE_SUPABASE_ANON_KEY!,
            {
                cookies: {
                    getAll() {
                        return cookieStore.getAll()
                    },
                    setAll(cookiesToSet) {
                        try {
                            cookiesToSet.forEach(({ name, value, options }) =>
                                cookieStore.set(name, value, options)
                            )
                        } catch (error) { }
                    },
                },
            }
        )

        let customAlerts: any[] = [];

        const { data: { user } } = await supabase.auth.getUser();
        if (!user) {
            return NextResponse.json({ alerts: [] }, { status: 401 });
        }

        const { data: profile } = await supabase
            .from('profiles')
            .select('organization_id')
            .eq('id', user.id)
            .single();

        const orgId = profile?.organization_id;

        if (!orgId) {
            return NextResponse.json({ alerts: [] });
        }

        let query = supabase
            .from('historical_data')
            .select('*')
            .eq('organization_id', orgId)
            .order('timestamp', { ascending: false })
            .limit(10);

        const { data: dbData, error } = await query;

        if (!error && dbData && dbData.length > 0) {
            dbData.forEach(dbAlert => {
                customAlerts.push({
                    sector: dbAlert.sector || "general",
                    item: dbAlert.item_key || "Unknown Item",
                    price: dbAlert.price || 0,
                    timestamp: dbAlert.timestamp,
                    metadata: {
                        intelligence_note: dbAlert.metadata_json?.intelligence_note || "Registro Histórico Detectado",
                        trend: dbAlert.metadata_json?.trend || "neutral"
                    }
                });
            });
        } else if (error) {
            console.error("Supabase Error fetch alerts:", error);
        }

        return NextResponse.json({ alerts: customAlerts });
    } catch (error) {
        console.error("Error fetching alerts:", error);
        return NextResponse.json({ alerts: [] }, { status: 500 });
    }
}
