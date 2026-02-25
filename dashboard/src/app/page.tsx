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
  Pill
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
    const interval = setInterval(fetchData, 30000); // Polling cada 30s
    return () => clearInterval(interval);
  }, [activeSector]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-950 text-white">
        <div className="animate-pulse flex flex-col items-center gap-4">
          <Zap className="h-12 w-12 text-blue-500 animate-bounce" />
          <span className="text-xl font-light tracking-widest uppercase">Initializing Antigravity...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 p-6 font-sans">
      {/* Header */}
      <header className="flex justify-between items-center mb-10 pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-4xl font-black tracking-tighter bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
            ANTIGRAVITY CONSOLE
          </h1>
          <p className="text-slate-400 mt-2 flex items-center gap-4">
            <span className="flex items-center gap-1">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              Tenant: <span className="text-slate-200 font-bold uppercase">{DEFAULT_TENANT}</span>
            </span>
            <Badge variant="outline" className={`${tenant?.tier === 'pro' ? 'border-amber-500/50 text-amber-500 bg-amber-500/5' : 'border-slate-500 text-slate-500'} font-black flex items-center gap-1`}>
              {tenant?.tier === 'pro' ? <><Crown className="h-3 w-3" /> PRO</> : 'FREE'}
            </Badge>
          </p>
        </div>

        {/* Heartbeat Widget */}
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-700/50 p-4 rounded-2xl flex items-center gap-4">
          <div className="flex flex-col items-end">
            <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">System Status</span>
            <span className="text-sm font-bold text-emerald-400">{health?.overall_health}</span>
          </div>
          <div className="h-10 w-10 rounded-full bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
            <Activity className="h-6 w-6 text-emerald-400 animate-[pulse_2s_infinite]" />
          </div>
        </div>
      </header>

      {/* Bento Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-6 gap-6 grid-rows-auto">

        {/* Alertas Críticas (Large Area) */}
        <Card className="col-span-1 md:col-span-4 lg:col-span-4 bg-slate-900/30 backdrop-blur-2xl border-slate-800/50 shadow-2xl overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between border-b border-slate-800/50 bg-slate-900/20">
            <div>
              <CardTitle className="text-xl flex items-center gap-2">
                <Zap className="h-5 w-5 text-amber-400" /> Brain Intelligence Alerts
              </CardTitle>
              <CardDescription className="text-slate-500">D003 Intelligence rules active</CardDescription>
            </div>
            <div className="flex gap-2">
              <Badge key="re" variant="outline" className="border-slate-700 text-slate-400">
                <Home className="h-3 w-3 mr-1" /> RE
              </Badge>
              <Badge key="pha" variant="outline" className="border-slate-700 text-slate-400">
                <Pill className="h-3 w-3 mr-1" /> PHA
              </Badge>
              <Badge key="fas" variant="outline" className="border-indigo-500/50 text-indigo-400 bg-indigo-500/5">
                <ShoppingBag className="h-3 w-3 mr-1" /> FAS
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="p-0 max-h-[500px] overflow-y-auto">
            <div className="divide-y divide-slate-800/50 text-white">
              {alerts.length > 0 ? (
                alerts.map((alert, idx) => (
                  <div key={idx} className="p-4 hover:bg-slate-800/20 transition-all flex items-start gap-4 group">
                    <div className={`p-3 rounded-xl bg-${alert.sector === 'real_estate' ? 'blue' : 'indigo'}-500/10 border border-${alert.sector === 'real_estate' ? 'blue' : 'indigo'}-500/20`}>
                      <AlertTriangle className="h-5 w-5 text-amber-500" />
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between items-start">
                        <span className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-1">{alert.sector}</span>
                        <span className="text-[10px] text-slate-600 font-mono italic">
                          {new Date(alert.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <h4 className="text-md font-bold text-slate-200 group-hover:text-white transition-colors">
                        {alert.metadata?.tag || "POTENCIAL OPORTUNIDAD"}: {alert.item}
                      </h4>
                      <p className="text-sm text-slate-400 mt-1">
                        {alert.metadata?.intelligence_note || "Análisis táctico en curso."}
                      </p>
                    </div>
                    <div className="text-right flex flex-col items-end gap-2">
                      <span className="text-lg font-black text-slate-100">${alert.price.toLocaleString()}</span>
                      <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/20">
                        {alert.sector === 'fashion' ? 'VIRAL 🔥' : 'DROP 🚨'}
                      </Badge>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-12 text-center text-slate-500 flex flex-col items-center gap-4">
                  <Activity className="h-10 w-10 text-slate-700" />
                  No high-priority alerts detected in the last scan.
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Gráfico de Tendencias (Wide Area) */}
        <Card className="col-span-1 md:col-span-4 lg:col-span-6 bg-slate-900/30 backdrop-blur-2xl border-slate-800/50 shadow-2xl">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <TrendingDown className="h-5 w-5 text-indigo-400" /> Sector Market Trends
              </CardTitle>
              <CardDescription className="text-slate-500">Historical price evolution from SQLAlchemy Engine</CardDescription>
            </div>
            <Tabs defaultValue="fashion" className="w-[300px]" onValueChange={setActiveSector}>
              <TabsList className="bg-slate-950/50 border border-slate-800">
                <TabsTrigger value="fashion">Fashion</TabsTrigger>
                <TabsTrigger value="real_estate">RE</TabsTrigger>
                <TabsTrigger value="pharmacy">Pharma</TabsTrigger>
              </TabsList>
            </Tabs>
          </CardHeader>
          <CardContent className="h-[300px] w-full pt-4 text-white">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends}>
                <defs>
                  <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis
                  dataKey="timestamp"
                  hide={true}
                />
                <YAxis
                  stroke="#475569"
                  fontSize={10}
                  tickFormatter={(val) => `$${val}`}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '12px' }}
                  itemStyle={{ color: '#e2e8f0', fontWeight: 'bold' }}
                />
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke="#6366f1"
                  strokeWidth={4}
                  fillOpacity={1}
                  fill="url(#colorPrice)"
                  animationDuration={1500}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* KPIs & Simulator (Gated) */}
        <SubscriptionGate
          tier={tenant?.tier || "free"}
          onUpgrade={async () => {
            const res = await fetch(`${API_BASE}/checkout/${DEFAULT_TENANT}`, { method: 'POST' });
            const data = await res.json();
            window.open(data.checkout_url, "_blank");
          }}
        >
          <WhatIfSimulator tenantSlug={DEFAULT_TENANT} tenantTier={tenant?.tier || "free"} />
        </SubscriptionGate>

        <Card className="col-span-1 md:col-span-2 lg:col-span-2 bg-gradient-to-br from-blue-500/10 to-indigo-500/10 backdrop-blur-xl border-blue-500/20">
          <CardHeader className="pb-2">
            <CardDescription className="text-slate-400 flex items-center gap-2">
              <Activity className="h-4 w-4" /> Scan Velocity
            </CardDescription>
            <CardTitle className="text-4xl text-white font-black">1.2s</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-slate-500 text-sm">
              99.9% Success Rate
            </div>
            <div className="mt-4 p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/10 text-[10px] text-emerald-400 font-bold uppercase">
              Engine Stable • D008 Verificado
            </div>
          </CardContent>
        </Card>

      </div>

      <footer className="mt-12 text-center text-[10px] text-slate-600 tracking-widest font-mono uppercase">
        Antigravity Autonomous Agent • Secure Multi-Tenant Architecture • Build 02.25
      </footer>
    </div>
  );
}
