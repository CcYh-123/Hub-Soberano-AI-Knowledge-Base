"use client";

import React, { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  AlertTriangle,
  TrendingDown,
  TrendingUp,
  Activity,
  ShieldCheck,
  Zap,
  ShoppingBag,
  Home,
  Pill,
  ArrowRight,
  CheckCircle2
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

import { WhatIfSimulator } from "@/components/what-if-simulator";
import { SubscriptionGate } from "@/components/subscription-gate";
import { Crown } from "lucide-react";
import { AuthGate } from "@/components/auth-gate";

const API_BASE = "http://localhost:8000";
const DEFAULT_TENANT = "demo-saas";

interface Tenant {
  id: string;
  name: string;
  slug: string;
  tier: string;
}

interface Alert {
  sector: string;
  item: string;
  price: number;
  timestamp: string;
  metadata?: {
    tag?: string;
    indicator?: string;
    intelligence_note?: string;
  };
}

interface Health {
  overall_health: string;
  last_sync: string;
}

interface Trend {
  timestamp: string;
  price: number;
  item: string;
}

export default function DashboardPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [health, setHealth] = useState<Health | null>(null);
  const [trends, setTrends] = useState<Trend[]>([]);
  const [tenant, setTenant] = useState<Tenant | null>(null);
  const [activeSector, setActiveSector] = useState("fashion");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [alertsRes, healthRes, trendsRes, tenantRes] = await Promise.all([
          fetch(`/api/alerts`),
          fetch(`${API_BASE}/health`).catch(() => new Response(JSON.stringify({ overall_health: "LOCAL (PYTHON OFFLINE)", last_sync: new Date().toISOString() }))),
          fetch(`${API_BASE}/trends/${DEFAULT_TENANT}/${activeSector}`).catch(() => new Response(JSON.stringify([]))),
          fetch(`${API_BASE}/tenant/${DEFAULT_TENANT}`).catch(() => new Response(JSON.stringify({ id: DEFAULT_TENANT, name: "Demo SaaS", slug: DEFAULT_TENANT, tier: "pro" })))
        ]);

        const alertsData = await alertsRes.json();
        const healthData = await healthRes.json();
        const trendsData = await trendsRes.json();
        const tenantData = await tenantRes.json();

        setAlerts(alertsData.alerts || []);
        setHealth(healthData);
        setTrends(trendsData || []);
        setTenant(tenantData);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [activeSector]);

  if (loading) {
    return (
      <div className="h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <AuthGate>
      <main className="min-h-screen bg-slate-50 p-4 md:p-8 font-sans">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
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

            <div className="flex items-center gap-3">
              <div className="hidden md:flex items-center gap-6 px-6 py-2 bg-slate-50 rounded-xl border border-slate-200">
                <div className="text-center group">
                  <p className="text-[10px] text-slate-500 uppercase font-semibold tracking-wide">Status</p>
                  <p className="text-xs text-slate-700 font-bold flex items-center gap-1.5">
                    <span className="h-2 w-2 bg-emerald-500 rounded-full shadow-[0_0_8px_rgba(16,185,129,0.4)]"></span>
                    ACTIVE
                  </p>
                </div>
                <div className="h-6 w-px bg-slate-200"></div>
                <div className="text-center">
                  <p className="text-[10px] text-slate-500 uppercase font-semibold tracking-wide">Health</p>
                  <p className="text-xs text-blue-600 font-bold">{health?.overall_health || "98.2%"}</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <div className={`px-4 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider flex items-center gap-2 ${tenant?.tier === 'pro' ? 'bg-blue-600 text-white shadow-sm hover:bg-blue-700 transition-colors' : 'bg-slate-100 text-slate-600 border border-slate-200'}`}>
                  {tenant?.tier === 'pro' ? <Crown className="h-3.5 w-3.5" /> : null}
                  {tenant?.tier || 'FREE'}
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Left Column: Metrics & Alerts */}
            <div className="lg:col-span-4 space-y-6">
              <Card className="bg-white border-slate-200 rounded-2xl shadow-sm overflow-hidden">
                <CardHeader className="pb-3 border-b border-slate-100">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg font-bold text-slate-800 flex items-center gap-2 tracking-tight">
                      <AlertTriangle className="h-4.5 w-4.5 text-blue-600" />
                      Intelligence Alerts
                    </CardTitle>
                    {alerts.length > 0 && (
                      <Badge className="bg-blue-50 text-blue-600 border hover:bg-blue-100 border-blue-200 text-[10px] font-bold px-2 py-0.5">{alerts.length} NEW</Badge>
                    )}
                  </div>
                  <CardDescription className="text-slate-500 text-xs mt-1">Market shifts detected by Antigravity Engine.</CardDescription>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="max-h-[500px] overflow-y-auto w-full custom-scrollbar">
                    {alerts.length > 0 ? (
                      <div className="p-4 space-y-3">
                        {alerts.map((alert, idx) => {
                          const note = alert.metadata?.intelligence_note || "";
                          const isCritical = note.includes("CRÍTICA");
                          const isWarning = note.includes("ADVERTENCIA");

                          let borderColor = "border-slate-200 hover:border-blue-300";
                          let iconColor = "text-blue-500";
                          let noteColor = "border-blue-200 text-slate-600 bg-blue-50";
                          let badgeColor = "bg-slate-50 text-slate-700 border-slate-200";

                          if (isCritical) {
                            borderColor = "border-rose-200 hover:border-rose-300 bg-rose-50/30";
                            iconColor = "text-rose-500";
                            noteColor = "border-rose-200 text-rose-700 bg-rose-50";
                            badgeColor = "bg-white text-rose-600 border-rose-200";
                          } else if (isWarning) {
                            borderColor = "border-amber-200 hover:border-amber-300 bg-amber-50/30";
                            iconColor = "text-amber-500";
                            noteColor = "border-amber-200 text-amber-700 bg-amber-50";
                            badgeColor = "bg-white text-amber-600 border-amber-200";
                          }

                          return (
                            <div key={idx} className={`p-4 bg-white rounded-xl border transition-all hover:shadow-sm group relative overflow-hidden ${borderColor}`}>
                              <div className="absolute top-0 right-0 p-3 opacity-5 group-hover:opacity-10 transition-opacity">
                                {alert.sector === 'pharmacy' ? <Pill className={`h-12 w-12 ${iconColor}`} /> : <ShoppingBag className={`h-12 w-12 ${iconColor}`} />}
                              </div>
                              <div className="flex items-start justify-between mb-2 relative z-10">
                                <div className="space-y-1">
                                  <p className={`text-[10px] font-bold uppercase tracking-wider ${iconColor}`}>{alert.sector}</p>
                                  <h4 className="text-sm font-semibold text-slate-800 leading-tight tracking-tight">{alert.item}</h4>
                                </div>
                                <Badge className={`text-xs font-semibold px-2.5 py-0.5 ${badgeColor}`}>
                                  {alert.price > 0 ? `$${alert.price.toLocaleString()}` : 'N/A'}
                                </Badge>
                              </div>
                              {alert.metadata?.intelligence_note && (
                                <div className={`mt-3 text-xs p-2.5 rounded-md border-l-2 flex flex-col items-start gap-1.5 relative z-10 ${noteColor}`}>
                                  <div className="flex items-center gap-1.5 font-semibold">
                                    <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
                                    {isCritical ? "ACTION REQUIRED" : "REVIEW NEEDED"}
                                  </div>
                                  <span className="opacity-90 leading-snug">{alert.metadata.intelligence_note}</span>
                                </div>
                              )}
                              <div className="mt-3 flex items-center justify-between text-[10px] text-slate-400 font-medium uppercase tracking-wider relative z-10">
                                <span>{new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                <span className="flex items-center gap-1 text-blue-600 hover:text-blue-700 transition-colors cursor-pointer font-semibold">
                                  DETAILS <ArrowRight className="h-3 w-3" />
                                </span>
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    ) : (
                      <div className="py-16 px-6 text-center flex flex-col items-center justify-center">
                        <div className="h-14 w-14 bg-slate-50 border border-slate-100 rounded-full flex items-center justify-center mb-4 shadow-sm">
                          <CheckCircle2 className="h-7 w-7 text-emerald-500" />
                        </div>
                        <h3 className="text-slate-800 font-semibold mb-1">Todo en orden</h3>
                        <p className="text-slate-500 text-sm">No se detectaron anomalías en la organización.</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Right Column: Chart & Simulator */}
            <div className="lg:col-span-8 space-y-6">
              <Card className="bg-white border-slate-200 rounded-2xl shadow-sm h-[400px] flex flex-col overflow-hidden">
                <CardHeader className="pb-3 border-b border-slate-100">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="space-y-1">
                      <CardTitle className="text-lg font-bold text-slate-800 tracking-tight flex items-center gap-2">
                        <TrendingUp className="h-4.5 w-4.5 text-blue-600" />
                        Historical Price Velocity
                      </CardTitle>
                      <CardDescription className="text-slate-500 text-xs">Sector: <span className="uppercase font-semibold text-slate-600">{activeSector}</span> | 24h Monitoring Interval</CardDescription>
                    </div>
                    <div className="flex gap-2 bg-slate-50 p-1 rounded-lg border border-slate-100">
                      {['fashion', 'pharmacy', 'luxury'].map((s) => (
                        <button
                          key={s}
                          onClick={() => setActiveSector(s)}
                          className={`px-3 py-1.5 rounded-md text-xs font-semibold capitalize transition-all ${activeSector === s ? 'bg-white border border-slate-200 text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="flex-1 p-6">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={trends}>
                      <defs>
                        <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#2563eb" stopOpacity={0.2} />
                          <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                      <XAxis
                        dataKey="timestamp"
                        stroke="#64748b"
                        fontSize={11}
                        tickMargin={10}
                        tickLine={false}
                        axisLine={false}
                        tickFormatter={(str) => {
                          const d = new Date(str);
                          return isNaN(d.getTime()) ? '' : d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                        }}
                      />
                      <YAxis
                        stroke="#64748b"
                        fontSize={11}
                        tickLine={false}
                        axisLine={false}
                        tickFormatter={(val) => `$${val}`}
                      />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        labelStyle={{ color: '#64748b', fontSize: '11px', fontWeight: 600, marginBottom: '4px' }}
                        itemStyle={{ color: '#0f172a', fontWeight: 700, fontSize: '13px' }}
                      />
                      <Area
                        type="monotone"
                        dataKey="price"
                        stroke="#2563eb"
                        strokeWidth={2.5}
                        fillOpacity={1}
                        fill="url(#colorPrice)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <SubscriptionGate
                tier={tenant?.tier || 'free'}
                onUpgrade={() => {
                  fetch(`${API_BASE}/checkout/${DEFAULT_TENANT}`, { method: 'POST' })
                    .then(res => res.json())
                    .then(data => { if (data.checkout_url) window.location.href = data.checkout_url; });
                }}
              >
                <WhatIfSimulator tenantSlug={DEFAULT_TENANT} tenantTier={tenant?.tier || 'pro'} />
              </SubscriptionGate>
            </div>
          </div>
        </div>
      </main>
    </AuthGate>
  );
}
