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
        <Card className="col-span-1 md:col-span-4 lg:col-span-2 bg-white border-slate-200 shadow-sm overflow-hidden h-full flex flex-col">
            <CardHeader className="bg-slate-50/50 pb-4 border-b border-slate-100">
                <CardTitle className="text-lg font-bold flex items-center gap-2 text-slate-800 tracking-tight">
                    <Target className="h-4.5 w-4.5 text-blue-600" /> What-If Simulator
                </CardTitle>
                <CardDescription className="text-slate-500 font-medium text-xs mt-1">Projected Scenario Analysis</CardDescription>
            </CardHeader>

            <CardContent className="p-6 space-y-6 flex-1 flex flex-col">
                {tenantTier === "pro" ? (
                    <>
                        {/* Sliders Area */}
                        <div className="space-y-6 flex-1">
                            <div className="space-y-3">
                                <div className="flex justify-between text-xs font-semibold uppercase tracking-wider text-slate-500">
                                    <span className="flex items-center gap-1.5"><DollarSign className="h-3.5 w-3.5 text-slate-400" /> Target Price</span>
                                    <span className="text-blue-600 font-mono font-bold">${params.price}</span>
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
                                <div className="flex justify-between text-xs font-semibold uppercase tracking-wider text-slate-500">
                                    <span className="flex items-center gap-1.5"><Users className="h-3.5 w-3.5 text-slate-400" /> Est. Volume</span>
                                    <span className="text-blue-600 font-mono font-bold">{params.volume} uts</span>
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
                                <div className="flex justify-between text-xs font-semibold uppercase tracking-wider text-slate-500">
                                    <span className="flex items-center gap-1.5"><PieChart className="h-3.5 w-3.5 text-slate-400" /> Marketing Spend</span>
                                    <span className="text-blue-600 font-mono font-bold">${params.marketing_spend}</span>
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
