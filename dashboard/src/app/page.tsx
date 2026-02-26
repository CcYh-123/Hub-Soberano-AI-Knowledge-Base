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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
  ArrowRight
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
          fetch(`${API_BASE}/alerts/${DEFAULT_TENANT}`),
          fetch(`${API_BASE}/health`),
          fetch(`${API_BASE}/trends/${DEFAULT_TENANT}/${activeSector}`),
          fetch(`${API_BASE}/tenant/${DEFAULT_TENANT}`)
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
      <div className="h-screen bg-black flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <AuthGate>
      <main className="min-h-screen bg-slate-950 p-4 md:p-8 font-sans selection:bg-indigo-500/30">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/40 p-6 rounded-3xl border border-slate-800/50 backdrop-blur-sm">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 bg-indigo-500 rounded-lg flex items-center justify-center">
                  <Activity className="h-5 w-5 text-white" />
                </div>
                <h1 className="text-2xl font-black text-white tracking-tight italic">ANTIGRAVITY <span className="text-indigo-500 not-italic">HUB</span></h1>
                <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 px-2 py-0 text-[10px] uppercase font-black tracking-widest ml-2 animate-pulse">LIVE SYSTEM</Badge>
              </div>
              <p className="text-slate-400 text-xs font-medium uppercase tracking-wider pl-10">Consola de Inteligencia Competitiva</p>
            </div>

            <div className="flex items-center gap-3">
              <div className="hidden md:flex items-center gap-6 px-6 py-2 bg-slate-950/50 rounded-2xl border border-slate-800/50">
                <div className="text-center group">
                  <p className="text-[10px] text-slate-500 uppercase font-bold tracking-tighter">Status</p>
                  <p className="text-xs text-white font-black flex items-center gap-1">
                    <span className="h-1.5 w-1.5 bg-emerald-500 rounded-full"></span>
                    ACTIVE
                  </p>
                </div>
                <div className="h-6 w-px bg-slate-800/50"></div>
                <div className="text-center">
                  <p className="text-[10px] text-slate-500 uppercase font-bold tracking-tighter">Health</p>
                  <p className="text-xs text-indigo-400 font-extrabold">{health?.overall_health || "98.2%"}</p>
                </div>
              </div>

              <div className="flex items-center gap-2 bg-white/5 p-1 rounded-2xl border border-white/10">
                <div className={`px-4 py-1.5 rounded-xl text-xs font-black uppercase tracking-widest flex items-center gap-2 ${tenant?.tier === 'pro' ? 'bg-indigo-500 text-white shadow-lg shadow-indigo-500/20' : 'bg-slate-800 text-slate-400'}`}>
                  {tenant?.tier === 'pro' ? <Crown className="h-3 w-3" /> : null}
                  {tenant?.tier || 'FREE'}
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Left Column: Metrics & Alerts */}
            <div className="lg:col-span-4 space-y-6">
              <Card className="bg-slate-900/50 border-slate-800/50 rounded-3xl overflow-hidden backdrop-blur-md">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg font-black text-white flex items-center gap-2 uppercase tracking-tighter italic">
                      <AlertTriangle className="h-4 w-4 text-amber-500" />
                      Intelligence Alerts
                    </CardTitle>
                    <Badge className="bg-amber-500/20 text-amber-500 border-none text-[10px] font-black">{alerts.length} NEW</Badge>
                  </div>
                  <CardDescription className="text-slate-400 text-xs font-medium">Critical market shifts detected by Antigravity Scraper.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 pt-4">
                  <div className="max-h-[500px] overflow-y-auto pr-2 space-y-3 custom-scrollbar">
                    {alerts.length > 0 ? (
                      alerts.map((alert, idx) => (
                        <div key={idx} className="p-4 bg-slate-950/50 rounded-2xl border border-slate-800/30 hover:border-amber-500/30 transition-all group relative overflow-hidden">
                          <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-30 transition-opacity">
                            {alert.sector === 'pharmacy' ? <Pill className="h-8 w-8 text-indigo-400" /> : <ShoppingBag className="h-8 w-8 text-indigo-400" />}
                          </div>
                          <div className="flex items-start justify-between mb-2">
                            <div className="space-y-1">
                              <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">{alert.sector}</p>
                              <h4 className="text-sm font-black text-white leading-tight uppercase tracking-tight">{alert.item}</h4>
                            </div>
                            <Badge className="bg-slate-900 text-emerald-400 border border-emerald-400/20 text-[10px] font-black">${alert.price}</Badge>
                          </div>
                          {alert.metadata?.intelligence_note && (
                            <div className="mt-3 text-[11px] text-slate-400 bg-slate-900/50 p-2 rounded-lg border-l-2 border-amber-500 flex items-start gap-2">
                              <Zap className="h-3 w-3 text-amber-500 mt-0.5 shrink-0" />
                              <span>{alert.metadata.intelligence_note}</span>
                            </div>
                          )}
                          <div className="mt-3 flex items-center justify-between text-[10px] text-slate-500 font-bold uppercase tracking-tighter">
                            <span>{new Date(alert.timestamp).toLocaleTimeString()}</span>
                            <span className="flex items-center gap-1 group-hover:text-indigo-400 transition-colors">
                              DETAILS <ArrowRight className="h-2.5 w-2.5" />
                            </span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="py-12 text-center space-y-2">
                        <div className="h-12 w-12 bg-slate-800/30 rounded-full flex items-center justify-center mx-auto">
                          <ShieldCheck className="h-6 w-6 text-slate-600" />
                        </div>
                        <p className="text-slate-500 text-xs font-bold uppercase tracking-widest tracking-tighter">No Active Alerts</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Right Column: Chart & Simulator */}
            <div className="lg:col-span-8 space-y-6">
              <Card className="bg-slate-900/50 border-slate-800/50 rounded-3xl overflow-hidden backdrop-blur-md h-[400px] flex flex-col">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <CardTitle className="text-xl font-black text-white uppercase italic tracking-tighter flex items-center gap-2">
                        <TrendingUp className="h-5 w-5 text-emerald-500" />
                        Historical Price Velocity
                      </CardTitle>
                      <CardDescription className="text-slate-400 text-xs font-medium">Sector: {activeSector.toUpperCase()} | 24h Monitoring Interval</CardDescription>
                    </div>
                    <div className="flex gap-2">
                      {['fashion', 'pharmacy', 'luxury'].map((s) => (
                        <button
                          key={s}
                          onClick={() => setActiveSector(s)}
                          className={`px-4 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-wider transition-all border ${activeSector === s ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-600/20' : 'bg-slate-950 border-slate-800 text-slate-500 hover:text-slate-300'}`}
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="flex-1 pt-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={trends}>
                      <defs>
                        <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                      <XAxis
                        dataKey="timestamp"
                        stroke="#475569"
                        fontSize={10}
                        tickFormatter={(str) => new Date(str).toLocaleTimeString()}
                      />
                      <YAxis
                        stroke="#475569"
                        fontSize={10}
                        tickFormatter={(val) => `$${val}`}
                      />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px' }}
                        labelStyle={{ color: '#94a3b8', fontSize: '10px', textTransform: 'uppercase', fontWeight: 900 }}
                      />
                      <Area
                        type="monotone"
                        dataKey="price"
                        stroke="#6366f1"
                        strokeWidth={3}
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
                <WhatIfSimulator tenantSlug={DEFAULT_TENANT} tenantTier={tenant?.tier || 'free'} />
              </SubscriptionGate>
            </div>
          </div>
        </div>
      </main>
    </AuthGate>
  );
}
