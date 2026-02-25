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
    TrendingUp,
    Target,
    DollarSign,
    Users,
    PieChart,
    Repeat
} from "lucide-react";

export function WhatIfSimulator({ tenantSlug, tenantTier }: { tenantSlug: string, tenantTier: string }) {
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

    useEffect(() => {
        if (tenantTier !== "pro") return;

        const delayDebounce = setTimeout(async () => {
            setLoading(true);
            try {
                const response = await fetch("http://localhost:8000/simulate", {
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
    }, [params, tenantSlug, tenantTier]);

    const handleSliderChange = (name: string, value: number[]) => {
        setParams(prev => ({ ...prev, [name]: value[0] }));
    };

    return (
        <Card className="col-span-1 md:col-span-4 lg:col-span-2 bg-slate-900/40 backdrop-blur-3xl border-indigo-500/20 shadow-xl overflow-hidden">
            <CardHeader className="bg-indigo-500/5 pb-4 border-b border-white/5">
                <CardTitle className="text-xl flex items-center gap-2 text-indigo-300">
                    <Target className="h-5 w-5" /> What-If Simulator
                </CardTitle>
                <CardDescription className="text-slate-500">Projected Scenario Analysis</CardDescription>
            </CardHeader>

            <CardContent className="p-5 space-y-6">
                {tenantTier === "pro" ? (
                    <>
                        {/* Sliders Area */}
                        <div className="space-y-5">
                            <div className="space-y-3">
                                <div className="flex justify-between text-xs font-bold uppercase tracking-widest text-slate-400">
                                    <span className="flex items-center gap-1"><DollarSign className="h-3 w-3" /> Target Price</span>
                                    <span className="text-indigo-400 font-mono">${params.price}</span>
                                </div>
                                <Slider
                                    defaultValue={[params.price]}
                                    max={1000}
                                    step={1}
                                    onValueChange={(v) => handleSliderChange("price", v)}
                                    className="py-2"
                                />
                            </div>

                            <div className="space-y-3">
                                <div className="flex justify-between text-xs font-bold uppercase tracking-widest text-slate-400">
                                    <span className="flex items-center gap-1"><Users className="h-3 w-3" /> Est. Volume</span>
                                    <span className="text-indigo-400 font-mono">{params.volume} uts</span>
                                </div>
                                <Slider
                                    defaultValue={[params.volume]}
                                    max={5000}
                                    step={10}
                                    onValueChange={(v) => handleSliderChange("volume", v)}
                                    className="py-2"
                                />
                            </div>

                            <div className="space-y-3">
                                <div className="flex justify-between text-xs font-bold uppercase tracking-widest text-slate-400">
                                    <span className="flex items-center gap-1"><PieChart className="h-3 w-3" /> Marketing Spend</span>
                                    <span className="text-indigo-400 font-mono">${params.marketing_spend}</span>
                                </div>
                                <Slider
                                    defaultValue={[params.marketing_spend]}
                                    max={10000}
                                    step={100}
                                    onValueChange={(v) => handleSliderChange("marketing_spend", v)}
                                    className="py-2"
                                />
                            </div>
                        </div>

                        {/* Results Area */}
                        <div className="grid grid-cols-2 gap-3 pt-4 border-t border-slate-800">
                            <div className="p-3 rounded-xl bg-slate-950/50 border border-slate-800 flex flex-col gap-1">
                                <span className="text-[10px] text-slate-500 uppercase font-black">Profit</span>
                                <span className={`text-lg font-black ${results.profit >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                    ${results.profit.toLocaleString()}
                                </span>
                            </div>
                            <div className="p-3 rounded-xl bg-slate-950/50 border border-slate-800 flex flex-col gap-1">
                                <span className="text-[10px] text-slate-500 uppercase font-black">MER</span>
                                <span className="text-lg font-black text-indigo-400">x{results.mer}</span>
                            </div>
                            <div className="p-3 rounded-xl bg-slate-950/50 border border-slate-800 flex flex-col gap-1">
                                <span className="text-[10px] text-slate-500 uppercase font-black">ROI</span>
                                <span className="text-md font-black text-slate-200">{results.roi}</span>
                            </div>
                            <div className="p-3 rounded-xl bg-slate-950/50 border border-slate-800 flex flex-col gap-1">
                                <span className="text-[10px] text-slate-500 uppercase font-black">Break-Even</span>
                                <span className="text-md font-black text-slate-200">{results.break_even_units} uts</span>
                            </div>
                        </div>
                    </>
                ) : (
                    <div className="h-full flex flex-col items-center justify-center py-10 text-center space-y-4">
                        <div className="p-4 bg-indigo-500/10 rounded-full border border-indigo-500/20">
                            <Repeat className="h-8 w-8 text-indigo-400 animate-spin-slow" />
                        </div>
                        <h4 className="text-white font-black text-lg">Interactive Simulation Locked</h4>
                        <p className="text-slate-500 text-xs px-10">
                            Predict your financial future. Pro members can simulate unlimited scenarios and optimize marketing ROMI.
                        </p>
                    </div>
                )}

                <div className="flex justify-center pt-2">
                    <Badge variant="outline" className={`${loading ? 'animate-pulse' : ''} border-indigo-500/30 text-indigo-400 bg-indigo-500/5`}>
                        <Repeat className="h-3 w-3 mr-1" /> Real-time Calculation Sync
                    </Badge>
                </div>
            </CardContent>
        </Card>
    );
}
