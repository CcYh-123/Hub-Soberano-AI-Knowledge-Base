import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { supabase } from '@/utils/supabase'; // Important: if checking via Server, supabase must have context (cookies)

export async function GET(request: Request) {
    try {
        const rootDir = process.cwd().replace(/\\/g, '/');
        // From dashboard to project root where reports folder is located
        const reportsDir = path.join(rootDir, '..', 'reports');

        let customAlerts: any[] = [];

        // Example check: retrieve org ID from Headers. Or simply use Auth if supabase context is available.
        // If not utilizing RLS specifically by cookies, pass it to supabase query.
        const orgId = request.headers.get('x-organization-id');

        // DB Fetch Phase > Hardcoded mocks
        let query = supabase
            .from('historical_data')
            .select('*')
            .eq('sector', 'pharmacy')
            .order('timestamp', { ascending: false })
            .limit(5);

        // Optional context fallback if doing server-level routing bypass
        if (orgId) {
            query = query.eq('organization_id', orgId);
        }

        const { data: dbData, error } = await query;

        if (!error && dbData && dbData.length > 0) {
            // Find specific db_sync high impact alerts
            const criticalDbAlerts = dbData.filter(d =>
                d.metadata_json?.trend === 'critical' || d.metadata_json?.source === 'db_sync'
            );

            criticalDbAlerts.forEach(dbAlert => {
                customAlerts.push({
                    sector: dbAlert.sector,
                    item: dbAlert.item_key,
                    price: dbAlert.price,
                    timestamp: dbAlert.timestamp,
                    metadata: {
                        intelligence_note: dbAlert.metadata_json?.intelligence_note || "CRÍTICA: ALERTA DESCONOCIDA"
                    }
                });
            });
        }

        // Fallbacks if no DB critical alert was found
        if (customAlerts.length === 0) {
            customAlerts.push({
                sector: "pharmacy",
                item: "IMPACTO > $10,000",
                price: 15400,
                timestamp: new Date().toISOString(),
                metadata: {
                    intelligence_note: "CRÍTICA: OPORTUNIDAD FARMACIA (MOCK) - ALZA DE PRECIOS DETECTADA"
                }
            });
        }

        // Standard warnings
        customAlerts.push({
            sector: "fashion",
            item: "VOLUMEN DE VENTAS -5.2%",
            price: 0,
            timestamp: new Date().toISOString(),
            metadata: {
                intelligence_note: "ADVERTENCIA: AJUSTE DE STOCK NECESARIO EN MODA"
            }
        });

        if (fs.existsSync(reportsDir)) {
            const files = fs.readdirSync(reportsDir).filter(f => f.endsWith('.md'));
            if (files.length > 0) {
                // Sort specifically by ctime or mtime
                const latestFile = files.sort((a, b) => {
                    return fs.statSync(path.join(reportsDir, b)).mtime.getTime() - fs.statSync(path.join(reportsDir, a)).mtime.getTime();
                })[0];

                customAlerts.unshift({
                    sector: "global",
                    item: "ESTRATEGIA",
                    price: 0,
                    timestamp: new Date().toISOString(),
                    metadata: {
                        intelligence_note: `CRÍTICA: REPORTE GENERADO LECTURA OBLIGATORIA (${latestFile})`
                    }
                });
            }
        }

        return NextResponse.json({ alerts: customAlerts });
    } catch (error) {
        console.error("Error reading reports:", error);
        return NextResponse.json({ alerts: [] }, { status: 500 });
    }
}
