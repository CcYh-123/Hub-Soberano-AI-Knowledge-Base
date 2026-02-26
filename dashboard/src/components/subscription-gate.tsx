
"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { Lock, Crown } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

interface SubscriptionGateProps {
    children: React.ReactNode;
    tier: string;
    onUpgrade: () => void;
}

export function SubscriptionGate({ children, tier, onUpgrade }: SubscriptionGateProps) {
    if (tier === "pro") {
        return <>{children}</>;
    }

    return (
        <div className="relative group overflow-hidden rounded-xl border border-white/5">
            {/* Blurred Content Overlay */}
            <div className="filter blur-[8px] pointer-events-none opacity-50 grayscale select-none">
                {children}
            </div>

            {/* Gate UI */}
            <div className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-slate-950/40 backdrop-blur-md p-6 text-center animate-in fade-in zoom-in duration-300">
                <div className="h-16 w-16 bg-indigo-500/20 rounded-full flex items-center justify-center mb-4 border border-indigo-500/30">
                    <Lock className="h-8 w-8 text-indigo-400" />
                </div>
                <h3 className="text-xl font-black text-white mb-2 flex items-center gap-2">
                    <Crown className="h-5 w-5 text-amber-400" /> PRO FEATURE
                </h3>
                <p className="text-slate-400 text-sm max-w-[280px] mb-6">
                    El Simulador What-If y el análisis avanzado de rentabilidad requieren una suscripción activa.
                </p>
                <Button
                    onClick={onUpgrade}
                    className="bg-indigo-600 hover:bg-indigo-500 text-white font-black px-8 py-6 rounded-xl shadow-lg shadow-indigo-500/20 border-t border-indigo-400/30 transition-all hover:scale-105"
                >
                    UPGRADE TO PRO NOW
                </Button>
            </div>
        </div>
    );
}
