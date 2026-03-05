"use client";

import React, { useState, useEffect } from "react";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle
} from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import {
    Target,
    DollarSign,
    Users,
    PieChart,
    Repeat,
    BarChart3
} from "lucide-react";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip as RechartTooltip,
    ResponsiveContainer,
    Cell
} from "recharts";

export function WhatIfSimulator({ tenantSlug, tenantTier, sector }: { tenantSlug: string, tenantTier: string, sector?: string }) {
    const [params, setParams] = useState({
        price: 150,
        volume: 500,
        marketing_spend: 2000,
        unit_cost: 45,
        fixed_costs: 5000
    });

    const [results, setResults] = useState({
        revenue: 0,
        profit: 0,
        mer: 0,
        roi: "0%",
        break_even_units: 0
    });

    const [loading, setLoading] = useState(false);

    // Flexibilización de Tier para permitir simulación en demo
    const isPro = tenantTier === "pro" || tenantSlug === "demo-saas";

    useEffect(() => {
        if (!isPro) return;

        const delayDebounce = setTimeout(async () => {
            setLoading(true);
            try {
                const response = await fetch("/api/simulate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ ...params, tenant_slug: tenantSlug }),
                });
                const data = await response.json();
                setResults(data);
            } catch (error) {
                console.error("Simulation error:", error);
            } finally {
                setLoading(false);
            }
        }, 300);

        return () => clearTimeout(delayDebounce);
    }, [params, tenantSlug, isPro]);

    const handleSliderChange = (name: string, value: number[]) => {
        setParams(prev => ({ ...prev, [name]: value[0] }));
    };

    const chartData = [
        { name: "Ingresos", value: results.revenue, color: "#3b82f6" },
        { name: "Ganancia", value: results.profit, color: "#10b981" }
    ];

    return (
        <Card className="col-span-1 md:col-span-4 lg:col-span-2 bg-white border-slate-200 shadow-sm overflow-hidden h-full flex flex-col">
            <CardHeader className="bg-slate-50/50 pb-4 border-b border-slate-100">
                <CardTitle className="text-lg font-bold flex items-center gap-2 text-slate-800 tracking-tight">
                    <Target className="h-4.5 w-4.5 text-blue-600" /> What-If Simulator
                </CardTitle>
                <CardDescription className="text-slate-500 font-bold text-[10px] mt-1 uppercase tracking-wider">
                    {sector ? `Análisis de Impacto: ${sector}` : "Projected Scenario Analysis"}
                </CardDescription>
            </CardHeader>

            <CardContent className="p-6 space-y-6 flex-1 flex flex-col">
                {isPro ? (
                    <>
                        {/* Sliders Area */}
                        <div className="space-y-6 flex-1">
                            <div className="space-y-3">
                                <div className="flex justify-between text-xs font-semibold uppercase tracking-wider text-slate-500">
                                    <span className="flex items-center gap-1.5"><DollarSign className="h-3.5 w-3.5 text-slate-400" /> Precio Objetivo</span>
                                    <span className="text-blue-600 font-mono font-bold">${params.price}</span>
                                </div>
                                <Slider
                                    value={[params.price]}
                                    max={1000}
                                    step={1}
                                    onValueChange={(v) => handleSliderChange("price", v)}
                                    className="py-2"
                                />
                            </div>

                            <div className="space-y-3">
                                <div className="flex justify-between text-xs font-semibold uppercase tracking-wider text-slate-500">
                                    <span className="flex items-center gap-1.5"><Users className="h-3.5 w-3.5 text-slate-400" /> Volumen Esperado</span>
                                    <span className="text-blue-600 font-mono font-bold">{params.volume} uts</span>
                                </div>
                                <Slider
                                    value={[params.volume]}
                                    max={5000}
                                    step={10}
                                    onValueChange={(v) => handleSliderChange("volume", v)}
                                    className="py-2"
                                />
                            </div>

                            <div className="space-y-3">
                                <div className="flex justify-between text-xs font-semibold uppercase tracking-wider text-slate-500">
                                    <span className="flex items-center gap-1.5"><PieChart className="h-3.5 w-3.5 text-slate-400" /> Marketing Spend</span>
                                    <span className="text-blue-600 font-mono font-bold">${params.marketing_spend}</span>
                                </div>
                                <Slider
                                    value={[params.marketing_spend]}
                                    max={10000}
                                    step={100}
                                    onValueChange={(v) => handleSliderChange("marketing_spend", v)}
                                    className="py-2"
                                />
                            </div>

                            {/* Chart Integration */}
                            <div className="h-40 w-full mt-4 border border-slate-100 rounded-lg p-2 bg-slate-50/30">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={chartData}>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                                        <XAxis dataKey="name" axisLine={false} tickLine={false} fontSize={10} stroke="#64748b" />
                                        <YAxis hide />
                                        <RechartTooltip
                                            cursor={{ fill: 'transparent' }}
                                            contentStyle={{ fontSize: '10px', borderRadius: '8px' }}
                                        />
                                        <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                                            {chartData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={entry.color} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Results Area */}
                        <div className="grid grid-cols-2 gap-3 pt-6 border-t border-slate-100">
                            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 flex flex-col gap-1.5 shadow-sm">
                                <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Profit</span>
                                <span className={`text-lg font-bold tracking-tight ${results.profit >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                                    ${results.profit.toLocaleString()}
                                </span>
                            </div>
                            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 flex flex-col gap-1.5 shadow-sm">
                                <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">MER</span>
                                <span className="text-lg font-bold tracking-tight text-blue-600">x{results.mer}</span>
                            </div>
                            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 flex flex-col gap-1.5 shadow-sm">
                                <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">ROI</span>
                                <span className="text-lg font-bold tracking-tight text-slate-700">{results.roi}</span>
                            </div>
                            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 flex flex-col gap-1.5 shadow-sm">
                                <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Break-Even</span>
                                <span className="text-lg font-bold tracking-tight text-slate-700">{results.break_even_units} uts</span>
                            </div>
                        </div>
                    </>
                ) : (
                    <div className="h-full flex flex-col items-center justify-center py-10 text-center space-y-4">
                        <div className="p-4 bg-blue-50 rounded-full border border-blue-100 shadow-sm">
                            <Repeat className="h-8 w-8 text-blue-500 animate-spin-slow" />
                        </div>
                        <h4 className="text-slate-800 font-bold text-lg">Interactive Simulation Locked</h4>
                        <p className="text-slate-500 text-sm px-10">
                            Predict your financial future. Pro members can simulate unlimited scenarios and optimize marketing ROMI.
                        </p>
                    </div>
                )}

                <div className="flex justify-center pt-4">
                    <Badge variant="outline" className={`${loading ? 'opacity-100' : 'opacity-70'} px-3 py-1 text-xs border-blue-200 text-blue-600 bg-blue-50 transition-opacity`}>
                        <Repeat className={`h-3 w-3 mr-1.5 ${loading ? 'animate-spin' : ''}`} /> Real-time Sync
                    </Badge>
                </div>
            </CardContent>
        </Card>
    );
}
