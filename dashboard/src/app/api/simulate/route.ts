import { NextResponse } from "next/server";

export async function POST(req: Request) {
    try {
        const { price, volume, marketing_spend, unit_cost, fixed_costs } = await req.json();

        const revenue = price * volume;
        const variable_costs = unit_cost * volume;
        const total_costs = variable_costs + fixed_costs + marketing_spend;
        const profit = revenue - total_costs;
        const mer = marketing_spend > 0
            ? parseFloat((revenue / marketing_spend).toFixed(2))
            : 0;
        const roi = marketing_spend > 0
            ? `${Math.round((profit / marketing_spend) * 100)}%`
            : "0%";
        const break_even_units = price > unit_cost
            ? Math.ceil((fixed_costs + marketing_spend) / (price - unit_cost))
            : 0;

        return NextResponse.json({ revenue, profit, mer, roi, break_even_units });

    } catch (err) {
        console.error("[simulate] Error:", err);
        return NextResponse.json(
            { revenue: 0, profit: 0, mer: 0, roi: "0%", break_even_units: 0 },
            { status: 500 }
        );
    }
}
