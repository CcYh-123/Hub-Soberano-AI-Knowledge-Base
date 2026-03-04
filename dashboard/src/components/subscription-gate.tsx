"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { Lock, Crown } from "lucide-react";

interface SubscriptionGateProps {
    children: React.ReactNode;
    tier: string;
    onUpgrade: () => void;
}

export function SubscriptionGate({ children, tier, onUpgrade }: SubscriptionGateProps) {
    if (tier === "pro" || true) {
        return <>{children}</>;
    }

    return (
        <div className="relative group overflow-hidden rounded-2xl border border-slate-200 bg-white">
            {/* Blurred Content Overlay */}
            <div className="filter blur-[8px] pointer-events-none opacity-40 grayscale select-none">
                {children}
            </div>

            {/* Gate UI */}
            <div className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-white/70 backdrop-blur-md p-6 text-center animate-in fade-in zoom-in duration-300">
                <div className="h-16 w-16 bg-blue-50 rounded-full flex items-center justify-center mb-4 border border-blue-100 shadow-sm">
                    <Lock className="h-8 w-8 text-blue-600" />
                </div>
                <h3 className="text-xl font-bold text-slate-800 mb-2 flex items-center gap-2">
                    <Crown className="h-5 w-5 text-amber-500" /> PRO FEATURE
                </h3>
                <p className="text-slate-600 text-sm max-w-[280px] mb-6 font-medium">
                    El Simulador What-If y el análisis avanzado de rentabilidad requieren una suscripción activa.
                </p>
                <Button
                    onClick={onUpgrade}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-6 rounded-xl shadow-sm transition-colors"
                >
                    UPGRADE TO PRO NOW
                </Button>
            </div>
        </div>
    );
}
