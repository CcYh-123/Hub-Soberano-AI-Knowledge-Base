"use client";
import { useState } from "react";

const MARTYRS = [
    { sku: "Amoxicilina 500mg x 12", old: 3542.60, suggested: 3659.13, gap: 116.53, level: "CRITICO" },
    { sku: "Atorvastatina 20mg x 30", old: 3240.38, suggested: 3346.96, gap: 106.58, level: "CRITICO" },
    { sku: "Losartan 50mg x 30", old: 2813.95, suggested: 2906.51, gap: 92.56, level: "CRITICO" },
    { sku: "Metformina 850mg x 30", old: 2149.07, suggested: 2219.76, gap: 70.69, level: "CRITICO" },
    { sku: "Ibuprofeno 400mg x 20", old: 1874.72, suggested: 1936.38, gap: 61.66, level: "CRITICO" },
    { sku: "Omeprazol 20mg x 14", old: 1672.67, suggested: 1727.69, gap: 55.02, level: "CRITICO" },
    { sku: "Enalapril 10mg x 30", old: 1422.78, suggested: 1469.58, gap: 46.80, level: "URGENTE" },
    { sku: "Paracetamol 500mg x 16", old: 980.25, suggested: 1020.36, gap: 40.11, level: "URGENTE" },
    { sku: "Diclofenac 75mg x 10", old: 776.40, suggested: 808.18, gap: 31.78, level: "URGENTE" },
    { sku: "Cetirizina 10mg x 10", old: 633.60, suggested: 659.54, gap: 25.94, level: "URGENTE" },
];

const TOTAL_GAP = MARTYRS.reduce((a, m) => a + m.gap, 0);
type Status = "idle" | "loading" | "applied" | "error";

export default function ProfitGapWidget() {
    const [statuses, setStatuses] = useState<Record<string, Status>>({});
    const [applied, setApplied] = useState<Set<string>>(new Set());

    const totalRecovered = [...applied].reduce((acc, sku) => {
        const p = MARTYRS.find((m) => m.sku === sku);
        return acc + (p?.gap ?? 0);
    }, 0);

    async function handleApply(sku: string, newPrice: number) {
        setStatuses((s) => ({ ...s, [sku]: "loading" }));
        try {
            const res = await fetch("/api/apply-price", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ sku, new_price: newPrice }),
            });
            if (!res.ok) throw new Error();
            setStatuses((s) => ({ ...s, [sku]: "applied" }));
            setApplied((prev) => new Set([...prev, sku]));
        } catch {
            setStatuses((s) => ({ ...s, [sku]: "error" }));
        }
    }

    const rowColor = (level: string) =>
        level === "CRITICO" ? "border-red-500/30 bg-red-500/5" : "border-yellow-500/30 bg-yellow-500/5";

    const badge = (level: string) =>
        level === "CRITICO"
            ? "bg-red-500/20 text-red-400 border border-red-500/30"
            : "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30";

    return (
        <div className="min-h-screen bg-[#0a0a0f] text-white p-6 font-mono">
            <div className="mb-8">
                <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">🛰️</span>
                    <h1 className="text-xl font-bold tracking-widest uppercase text-white/90">
                        Antigravity — Profit Gap Radar
                    </h1>
                    <span className="ml-auto text-xs text-white/30 tracking-widest">FASE 6 / OPERATIVO</span>
                </div>
                <div className="h-px bg-gradient-to-r from-red-500/60 via-orange-400/40 to-transparent" />
            </div>

            <div className="grid grid-cols-3 gap-4 mb-8">
                <Card label="Recuperación potencial" value={`$${TOTAL_GAP.toFixed(2)}`} sub="por ciclo de venta" color="text-emerald-400" />
                <Card label="Productos mártires" value={`${MARTYRS.length}`} sub={`${MARTYRS.filter((m) => m.level === "CRITICO").length} críticos / ${MARTYRS.filter((m) => m.level === "URGENTE").length} urgentes`} color="text-red-400" />
                <Card label="Ya recuperado" value={`$${totalRecovered.toFixed(2)}`} sub={`${applied.size} precios aplicados`} color="text-blue-400" />
            </div>

            <div className="border border-white/10 rounded-lg overflow-hidden">
                <div className="grid grid-cols-[2fr_1fr_1fr_1fr_90px_120px] gap-4 px-4 py-3 bg-white/5 border-b border-white/10 text-[11px] tracking-widest uppercase text-white/40">
                    <span>Producto</span>
                    <span className="text-right">Actual</span>
                    <span className="text-right">Sugerido</span>
                    <span className="text-right">Gap/u</span>
                    <span className="text-center">Estado</span>
                    <span className="text-center">Acción</span>
                </div>

                {MARTYRS.map((m) => {
                    const st = statuses[m.sku] ?? "idle";
                    const isApplied = applied.has(m.sku);
                    return (
                        <div key={m.sku} className={`grid grid-cols-[2fr_1fr_1fr_1fr_90px_120px] gap-4 px-4 py-3 border-b border-white/5 items-center transition-all duration-300 ${rowColor(m.level)} ${isApplied ? "opacity-40" : "hover:bg-white/5"}`}>
                            <span className="text-sm text-white/85 truncate">{m.sku}</span>
                            <span className="text-right text-sm text-white/50 tabular-nums">${m.old.toFixed(2)}</span>
                            <span className="text-right text-sm text-emerald-400 tabular-nums font-semibold">${m.suggested.toFixed(2)}</span>
                            <span className={`text-right text-sm tabular-nums font-bold ${m.level === "CRITICO" ? "text-red-400" : "text-yellow-400"}`}>+${m.gap.toFixed(2)}</span>
                            <div className="flex justify-center">
                                <span className={`text-[10px] px-2 py-1 rounded tracking-widest ${badge(m.level)}`}>{m.level}</span>
                            </div>
                            <div className="flex justify-center">
                                {isApplied ? (
                                    <span className="text-[11px] text-emerald-400 tracking-widest">✓ APLICADO</span>
                                ) : (
                                    <button onClick={() => handleApply(m.sku, m.suggested)} disabled={st === "loading"} className={`text-[11px] px-3 py-1.5 rounded border tracking-widest transition-all duration-200 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed ${st === "error" ? "border-red-500 text-red-400" : "border-white/20 text-white/60 hover:border-emerald-500/60 hover:text-emerald-400 hover:bg-emerald-500/10"}`}>
                                        {st === "loading" ? "..." : st === "error" ? "ERROR" : "APLICAR"}
                                    </button>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>

            <div className="mt-4 flex justify-between text-[11px] text-white/25 tracking-widest">
                <span>TENANT: demo-saas | SECTOR: pharmacy</span>
                <span>INFLACIÓN: 5% mensual | TARGET: 25%</span>
            </div>
        </div>
    );
}

function Card({ label, value, sub, color }: { label: string; value: string; sub: string; color: string }) {
    return (
        <div className="border border-white/10 rounded-lg p-4 bg-white/3">
            <div className="text-[11px] tracking-widest uppercase text-white/35 mb-2">{label}</div>
            <div className={`text-2xl font-bold tabular-nums ${color}`}>{value}</div>
            <div className="text-[11px] text-white/30 mt-1">{sub}</div>
        </div>
    );
}
