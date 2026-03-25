"use client";

import React, { useState, useEffect } from "react";
import { 
  TrendingUp, 
  AlertTriangle, 
  ShieldCheck, 
  Zap, 
  ArrowRight, 
  CheckCircle2, 
  Activity, 
  Pill, 
  ShoppingBag,
  Crown
} from "lucide-react";
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from "recharts";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { createClient } from '@supabase/supabase-js';

// Init Supabase Client
const supabaseUrl = process.env.VITE_SUPABASE_URL!;
const supabaseKey = process.env.VITE_SUPABASE_ANON_KEY!;
const supabase = createClient(supabaseUrl, supabaseKey);

interface Alert {
  item: string;
  price: number;
  timestamp: string;
  sector: string;
  metadata?: {
    intelligence_note?: string;
  };
}

interface Trend {
  timestamp: string;
  price: number;
}

interface WarTableRow {
  sku: string;
  cost_supa: number;
  price: number;
  margin: number;
  gap: number;
  suggested_price: number;
  stock: number;
  applied?: boolean;
  reason?: string;
}

/** Fashion/CSV: criticalCount + martyrs. AGRO (Python): gap + recuperado + products */
interface MarginReport {
  latestFile?: string | null;
  criticalCount?: number;
  martyrs?: WarTableRow[];
  gap?: number;
  recuperado?: number;
  products?: WarTableRow[];
}

interface Tenant {
  name: string;
  tier: 'free' | 'pro' | 'enterprise';
  sector?: string;
}

interface Health {
  overall_health: string;
  last_check: string;
}

export default function DashboardPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [health, setHealth] = useState<Health | null>(null);
  const [trends, setTrends] = useState<Trend[]>([]);
  const [tenant, setTenant] = useState<Tenant | null>(null);
  const [orgId, setOrgId] = useState<string>("demo-saas");
  const [activeSector, setActiveSector] = useState("agro");
  const [loading, setLoading] = useState(true);
  const [marginReport, setMarginReport] = useState<MarginReport | null>(null);
  const [recoveredTotal, setRecoveredTotal] = useState<number>(0);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        let currentSector = activeSector;
        
        // Fetch Tenant/Profile
        const { data: { user } } = await supabase.auth.getUser();
        if (user) {
          const { data: profile } = await supabase
            .from('profiles')
            .select('*')
            .eq('id', user.id)
            .single();
            
          if (profile) {
            setTenant({
              name: profile.full_name || "Soberano User",
              tier: (profile.tier as any) || 'pro',
              sector: profile.sector
            });
            setOrgId(profile.org_id || "demo-saas");
            // If user has a locked sector, we might want to respect it, 
            // but for Phase 5 we default to agro if it's the first load
          }
        }

        // Parallel Fetch for widgets
        const [alertsRes, healthRes, trendsRes, tenantRes, reportRes] = await Promise.all([
          fetch(`/api/alerts?sector=${currentSector}`),
          fetch(`/api/health?org_id=${orgId}`),
          fetch(`/api/trends?sector=${currentSector}`),
          fetch(`/api/tenant/${orgId}`),
          // API App Router: dashboard/src/app/api/latest-report/route.ts → sector=agro devuelve { gap, recuperado, products }
          fetch(`/api/latest-report?sector=${currentSector}`)
        ]);

        const alertsData = await alertsRes.json();
        const healthData = await healthRes.json();
        const trendsData = await trendsRes.json();
        const tenantData = await tenantRes.json();
        const reportData = await reportRes.json();

        if (currentSector === "agro") {
          console.log("🚜 [DEBUG AGRO] latest-report:", {
            gap: reportData.gap,
            recuperado: reportData.recuperado,
            productsCount: reportData.products?.length,
          });
        }

        setAlerts(Array.isArray(alertsData) ? alertsData : (alertsData.alerts || []));
        setHealth(healthData);
        setTrends(trendsData || []);
        setTenant(tenantData);

        const isAgroApi =
          currentSector === "agro" &&
          reportData != null &&
          typeof reportData === "object" &&
          typeof (reportData as { gap?: unknown }).gap === "number" &&
          Array.isArray((reportData as { products?: unknown }).products);

        if (isAgroApi) {
          const raw = reportData as {
            gap: number;
            recuperado?: number;
            products?: unknown[];
            latestFile?: string;
          };
          const products: WarTableRow[] = Array.isArray(raw.products)
            ? raw.products.map((p: unknown) => {
                const row = p as Record<string, unknown>;
                return {
                  sku: String(row.sku ?? ""),
                  cost_supa: Number(row.cost_supa) || 0,
                  price: Number(row.price) || 0,
                  margin: Number(row.margin) || 0,
                  gap: Number(row.gap) || 0,
                  suggested_price: Number(row.suggested_price) || 0,
                  stock: Number(row.stock) || 0,
                };
              })
            : [];
          const gapMoney = products.reduce((s, p) => s + (Number(p.gap) || 0), 0);
          setMarginReport({
            gap: gapMoney,
            recuperado: raw.recuperado ?? 0,
            products,
            latestFile: raw.latestFile ?? "LIVE_API_SYNC",
          });
        } else {
          setMarginReport({
            criticalCount: reportData.criticalCount ?? 0,
            martyrs: reportData.martyrs ?? [],
            latestFile: reportData.latestFile,
          });
        }

        // Fetch recovered total
        const { data: logs } = await supabase
          .from('price_logs')
          .select('recovered_gap');
        
        if (logs) {
          const total = logs.reduce((sum, log) => sum + (Number(log.recovered_gap) || 0), 0);
          setRecoveredTotal(total);
        }

      } catch (err) {
        console.error("❌ CRITICAL: Error fetching dashboard data:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [orgId, activeSector]);

  const handleApplyPrice = async (martyr: any) => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        alert("Sesión expirada. Por favor, ingresá nuevamente.");
        return;
      }

      const { error } = await supabase.from('price_logs').insert([{
        sku: martyr.sku,
        old_price: martyr.price,
        new_price: martyr.suggested_price,
        recovered_gap: martyr.gap,
        user_id: user.id,
        sector: activeSector
      }]);

      if (error) throw error;

      // Update Local State
      setMarginReport(prev => {
        if (!prev) return null;
        if (activeSector === "agro" && prev.products) {
          return {
            ...prev,
            products: prev.products.map(m =>
              m.sku === martyr.sku ? { ...m, applied: true } : m
            ),
          };
        }
        return {
          ...prev,
          martyrs: (prev.martyrs ?? []).map(m =>
            m.sku === martyr.sku ? { ...m, applied: true } : m
          ),
        };
      });

      // Update Recovered Counter
      setRecoveredTotal(prev => prev + (Number(martyr.gap) || 0));
      
      alert(`✅ PRECIO APLICADO: ${martyr.sku} ahora rinde +$${martyr.gap.toLocaleString()}`);

    } catch (err: any) {
      console.error("Error applying price:", err);
      alert("Error al aplicar precio: " + err.message);
    }
  };

  if (loading && !marginReport) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-8">
        <div className="relative">
          <Activity className="h-12 w-12 text-blue-600 animate-pulse" />
          <div className="absolute inset-0 border-4 border-blue-600/20 border-t-blue-600 rounded-full animate-spin"></div>
        </div>
        <p className="mt-6 text-slate-500 font-bold uppercase tracking-widest text-xs animate-pulse">Sincronizando con Antigravity Engine...</p>
      </div>
    );
  }

  const warRows: WarTableRow[] =
    activeSector === "agro"
      ? marginReport?.products ?? []
      : marginReport?.martyrs ?? [];

  const gapDisplay =
    activeSector === "agro"
      ? marginReport?.products?.reduce((acc, p) => acc + (Number(p.gap) || 0), 0) ??
        marginReport?.gap ??
        0
      : marginReport?.martyrs?.reduce((acc, m) => acc + (m.gap || 0), 0) ?? 0;

  const showWarCard =
    marginReport &&
    (activeSector === "agro"
      ? (marginReport.products?.length ?? 0) > 0
      : (marginReport.criticalCount ?? 0) > 0 ||
        (marginReport.martyrs?.length ?? 0) > 0);

  const warCardBorderCritical =
    activeSector === "agro"
      ? warRows.some((m) => m.margin < 25)
      : (marginReport?.criticalCount ?? 0) > 0;

  return (
      <main className="min-h-screen bg-slate-50 p-4 md:p-8 font-sans">
        <div className="max-w-7xl mx-auto space-y-8">
          
          {/* HEADER PRINCIPAL */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm mb-6">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-sm">
                  <Activity className="h-5 w-5 text-white" />
                </div>
                <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Antigravity <span className="text-blue-600">Hub</span></h1>
                <Badge variant="outline" className="bg-emerald-50 text-emerald-600 border-emerald-200 px-2 py-0.5 text-[10px] uppercase font-semibold tracking-wider ml-2">LIVE SYSTEM</Badge>
              </div>
              <p className="text-slate-500 text-xs font-medium uppercase tracking-wider pl-10">Consola de Inteligencia Competitiva</p>
            </div>

            <div className="flex items-center gap-2">
              <button 
                id="selector-agro"
                onClick={() => {
                  console.log("🌾 Forzando cambio a AGRO - Fase 5");
                  setActiveSector("agro");
                }}
                className={`px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase transition-all z-50 ${activeSector === "agro" ? "bg-emerald-600 text-white shadow-md shadow-emerald-500/20" : "bg-slate-100 text-slate-500 hover:bg-slate-200"}`}
              >
                🌾 AGRO (ACTIVE)
              </button>
              <button 
                id="selector-fashion"
                onClick={() => {
                  console.log("👕 Cambiando a FASHION");
                  setActiveSector("fashion");
                }}
                className={`px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase transition-all z-50 ${activeSector === "fashion" ? "bg-blue-600 text-white shadow-md shadow-blue-500/20" : "bg-slate-100 text-slate-500 hover:bg-slate-200"}`}
              >
                👕 FASHION
              </button>
              <div className={`px-4 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider flex items-center gap-2 ${tenant?.tier === 'pro' ? 'bg-slate-900 text-white shadow-sm hover:bg-slate-800 transition-colors' : 'bg-slate-100 text-slate-600 border border-slate-200'}`}>
                {tenant?.tier === 'pro' ? <Crown className="h-3.5 w-3.5 text-amber-400" /> : null}
                {tenant?.tier || 'FREE'}
              </div>
            </div>
          </div>

          {/* ESTADO DE CUENTA - FASE 4 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="bg-blue-600 text-white rounded-2xl shadow-xl overflow-hidden border-none transform hover:scale-[1.02] transition-all">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-xs uppercase tracking-[0.2em] font-black opacity-80">Suscripción Antigravity</CardTitle>
                  <Crown className="h-4 w-4" />
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-black">Plan Enterprise PRO</p>
                <div className="flex items-center gap-2 mt-2">
                    <Badge className="bg-white/20 hover:bg-white/30 text-white border-none text-[10px] uppercase font-bold">ACTIVO</Badge>
                    <span className="text-xs font-medium opacity-80">$29.900 / mes</span>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white border-slate-200 rounded-2xl shadow-sm overflow-hidden flex flex-col justify-center p-6 border-l-4 border-l-emerald-500">
               <p className="text-[10px] text-slate-500 uppercase font-black tracking-widest mb-1">Fee Variable Acumulado</p>
               <p className="text-3xl font-black text-slate-900 tabular-nums">
                ${(recoveredTotal * 0.10).toLocaleString("es-AR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
               </p>
               <p className="text-xs text-slate-400 mt-1">10% de ganancia recuperada real</p>
            </Card>

            <div className="flex flex-col gap-4">
               <button 
                  onClick={() => {
                    const top3 = [...warRows]
                        .sort((a, b) => b.gap - a.gap)
                        .slice(0, 3)
                        .map(m => `- ${m.sku}: +$${m.gap.toLocaleString()}`)
                        .join('\n');
                        
                    const report = `
# 🛡️ Reporte Táctico Antigravity | ${new Date().toLocaleDateString('es-AR')}
## 📊 Resumen de la Sesión
- **Ganancia Recuperada**: $${recoveredTotal.toLocaleString()}
- **Comisión Generada**: $${(recoveredTotal * 0.10).toLocaleString()}
- **Estado de Cuenta**: Suscripción Base Pro Active

## 🚀 Top 3 Optimizaciones
${top3}

---
Asegurando el "Profitability North Star" para la organización.
`;
                    navigator.clipboard.writeText(report);
                    alert("¡Reporte generado y copiado al portapapeles!");
                  }}
                  className="bg-slate-900 text-white font-bold h-full rounded-2xl flex items-center justify-center gap-3 hover:bg-slate-800 transition-all shadow-lg active:scale-95"
               >
                 <ShieldCheck className="h-5 w-5 text-emerald-400" /> Generar Walkthrough
               </button>
            </div>
          </div>

          {/* INDICADORES DE GANANCIA - Siempre Visibles */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className={`rounded-2xl border-2 p-6 md:p-8 text-center bg-red-500/15 border-red-500 text-red-900 shadow-lg shadow-red-500/10`}>
              <p className="text-sm font-semibold uppercase tracking-wider opacity-90 mb-1">GAP de ganancia</p>
              <h2 className="text-5xl md:text-6xl font-black tracking-tighter tabular-nums">
                ${gapDisplay.toLocaleString("es-AR")}
              </h2>
              <p className="text-xs mt-2 opacity-80 uppercase font-bold tracking-tight">
                {activeSector === "agro"
                  ? "Pérdida potencial acumulada (Σ gap · productos críticos)"
                  : "Oportunidad de optimización detectada"}
              </p>
            </div>

            <div className="rounded-2xl border-2 border-emerald-500 p-6 md:p-8 text-center bg-emerald-500/15 text-emerald-900 shadow-lg shadow-emerald-500/10">
              <p className="text-sm font-semibold uppercase tracking-wider opacity-90 mb-1">Ya recuperado</p>
              <h2 className="text-5xl md:text-6xl font-black tracking-tighter tabular-nums">
                ${recoveredTotal.toLocaleString("es-AR")}
              </h2>
              <p className="text-xs mt-2 opacity-80 uppercase font-bold tracking-tight">Ganancia asegurada - Fase 4</p>
            </div>
          </div>

          {/* CONTENIDO TÁCTICO — Mesa de guerra + tendencias */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div className="lg:col-span-12 space-y-6">
              {showWarCard ? (
                <Card className={`rounded-2xl shadow-sm overflow-hidden border-2 ${warCardBorderCritical ? "border-red-200 bg-red-50/50" : "border-amber-200 bg-amber-50/30"}`}>
                  <CardHeader className="pb-3 border-b border-slate-100">
                    <CardTitle className="text-lg font-bold text-slate-800 flex items-center gap-2 tracking-tight">
                      Radar de Márgenes (Sector AGRO)
                    </CardTitle>
                    <CardDescription className="text-slate-500 text-xs mt-1">
                      Último reporte: {marginReport?.latestFile || "—"}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="p-0">
                    <div className="max-h-[500px] overflow-y-auto custom-scrollbar">
                      <table className="w-full text-sm">
                        <thead className="bg-slate-50 sticky top-0 z-10 border-b">
                          <tr>
                            <th className="text-left py-3 px-4 font-semibold text-slate-700">SKU</th>
                            <th className="text-right py-3 px-4 font-semibold text-slate-700">Costo</th>
                            <th className="text-right py-3 px-4 font-semibold text-slate-700">Margen</th>
                            <th className="text-right py-3 px-4 font-semibold text-slate-700">Stock</th>
                            <th className="text-right py-3 px-4 font-semibold text-slate-700">Gap Total</th>
                            <th className="text-right py-3 px-4 font-semibold text-slate-700">Sugerido</th>
                            <th className="text-center py-3 px-4 font-semibold text-slate-700">Acción</th>
                          </tr>
                        </thead>
                        <tbody>
                          {warRows.map((m, idx) => (
                            <tr key={idx} className={`border-b border-slate-100 ${m.applied ? "bg-emerald-100/50" : "bg-white"}`}>
                              <td className="py-3 px-4 font-medium">{m.sku}</td>
                              <td className="py-3 px-4 text-right">${Number(m.cost_supa).toLocaleString()}</td>
                              <td className="py-3 px-4 text-right font-bold text-red-600">{Number(m.margin).toFixed(1)}%</td>
                              <td className="py-3 px-4 text-right">{m.stock}</td>
                              <td className="py-3 px-4 text-right font-black text-red-600">${Number(m.gap).toLocaleString()}</td>
                              <td className="py-3 px-4 text-right font-black">${Number(m.suggested_price).toLocaleString()}</td>
                              <td className="py-3 px-4 text-center">
                                {m.applied ? (
                                  <Badge className="bg-emerald-100 text-emerald-700">APLICADO</Badge>
                                ) : (
                                  <button onClick={() => handleApplyPrice(m)} className="bg-slate-900 text-white text-[10px] px-3 py-1 rounded font-bold">APLICAR</button>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <Card className="rounded-2xl p-8 text-center text-slate-500">Sin alertas críticas detectadas.</Card>
              )}

              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                <div className="lg:col-span-4">
                  <Card className="bg-white border-slate-200 rounded-2xl shadow-sm overflow-hidden">
                    <CardHeader className="pb-3 border-b border-slate-100">
                      <CardTitle className="text-lg font-bold text-slate-800 flex items-center gap-2 tracking-tight">
                        <AlertTriangle className="h-4.5 w-4.5 text-blue-600" />
                        Intelligence Alerts
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 max-h-[600px] overflow-y-auto">
                      {alerts.length > 0 ? (
                        <div className="space-y-3">
                          {alerts.map((alert, idx) => (
                            <div key={idx} className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                              <h4 className="text-xs font-bold text-slate-700">{alert.item}</h4>
                              <p className="text-[10px] text-slate-500 mt-1">{alert.metadata?.intelligence_note}</p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-xs text-slate-400 text-center py-8">No hay alertas activas.</p>
                      )}
                    </CardContent>
                  </Card>
                </div>
                <div className="lg:col-span-8">
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={trends}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="timestamp" hide />
                      <YAxis hide />
                      <Tooltip />
                      <Area type="monotone" dataKey="price" stroke="#2563eb" fill="#dbeafe" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
  );
}
