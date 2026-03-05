import { NextResponse } from 'next/server';

const API_BASE = process.env.PYTHON_API_URL || "http://localhost:8000";

export async function GET() {
    try {
        const response = await fetch(`${API_BASE}/health`, {
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
            return NextResponse.json({
                overall_health: "LOCAL (PYTHON OFFLINE)",
                last_sync: new Date().toISOString()
            });
        }

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("Health proxy error:", error);
        return NextResponse.json({
            overall_health: "LOCAL (PYTHON OFFLINE)",
            last_sync: new Date().toISOString()
        });
    }
}
