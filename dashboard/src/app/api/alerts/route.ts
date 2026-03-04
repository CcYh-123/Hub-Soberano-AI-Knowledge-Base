import { NextResponse } from 'next/server';
import { supabase } from '@/utils/supabase';

export async function GET(request: Request) {
    try {
        let customAlerts: any[] = [];

        // Example check: retrieve org ID from Headers. Or simply use Auth if supabase context is available.
        // For testing purposes, default to the known test org if not provided
        const orgId = request.headers.get('x-organization-id') || "kixnlqjuiqtodzdubydb";

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
