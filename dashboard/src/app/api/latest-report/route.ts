import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';
import { existsSync, readdirSync, readFileSync, statSync } from 'fs';
import { join } from 'path';

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

const REPORTS_DIR = join(process.cwd(), '..', 'reports');
const FALLBACK_REPORTS_DIR = join(process.cwd(), 'reports');

export interface MartyrRow {
  item: string;
  price: number;
  stock: number;
  margin: number;
  gap: number;
  suggested_price: number;
  level: string;
}

export async function OPTIONS() {
  return new NextResponse(null, { status: 204, headers: CORS_HEADERS });
}

function parseCsv(content: string): MartyrRow[] {
  const lines = content.trim().split(/\r?\n/);
  if (lines.length < 2) return [];
  const headers = lines[0].split(',').map((h) => h.trim().toLowerCase());
  const rows: MartyrRow[] = [];
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map((v) => v.trim());
    const row: Record<string, string | number> = {};
    headers.forEach((h, j) => {
      const v = values[j];
      if (v === '' || v === undefined) {
        row[h] = h === 'sku' || h === 'level' ? '' : 0;
      } else if (h === 'cost_supa' || h === 'price' || h === 'margin' || h === 'gap' || h === 'suggested_price' || h === 'stock') {
        row[h] = Number(v) || 0;
      } else {
        row[h] = v;
      }
    });
    rows.push(row as unknown as MartyrRow);
  }
  return rows;
}

function getReportsDir(): string | null {
  try {
    const dir = existsSync(REPORTS_DIR) ? REPORTS_DIR : FALLBACK_REPORTS_DIR;
    if (existsSync(dir)) return dir;
  } catch {
    // ignore
  }
  return null;
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const sector = searchParams.get('sector') || 'fashion';

  // AGRO: solo Python; nunca CSV (evita JSON fashion y gap $0 en el cliente)
  if (sector === 'agro') {
    const apiBase = (process.env.PYTHON_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
    try {
      const response = await fetch(`${apiBase}/get-martires`, { cache: 'no-store' });
      if (response.ok) {
        const data = await response.json();
        const rows = Array.isArray(data.productos) ? data.productos : [];
        // Suma monetaria de pérdida por volumen (gap por producto, mismo criterio que api_bridge)
        const totalGapMoney = rows.reduce((sum: number, p: Record<string, unknown>) => {
          return sum + (Number(p.gap) || 0);
        }, 0);
        return NextResponse.json(
          {
            gap: totalGapMoney,
            recuperado: 0,
            products: rows,
          },
          { headers: CORS_HEADERS }
        );
      }
      console.error('[latest-report] AGRO: API respondió', response.status, await response.text().catch(() => ''));
    } catch (e) {
      console.error('Fallo de conexión con Antigravity API Bridge (PYTHON_API_URL):', e);
    }
    return NextResponse.json({ gap: 0, recuperado: 0, products: [] }, { headers: CORS_HEADERS });
  }

  try {
    const dir = getReportsDir();
    if (!dir) {
      return NextResponse.json({ criticalCount: 0, martyrs: [], latestFile: null }, { headers: CORS_HEADERS });
    }

    const files = readdirSync(dir)
      .filter((f) => f.startsWith('reporte_margen_') && f.endsWith('.csv'))
      .map((f) => ({ name: f, mtime: statSync(join(dir, f)).mtime.getTime() }))
      .sort((a, b) => b.mtime - a.mtime);

    if (files.length === 0) {
      return NextResponse.json({ criticalCount: 0, martyrs: [], latestFile: null }, { headers: CORS_HEADERS });
    }

    const latestPath = join(dir, files[0].name);
    const content = readFileSync(latestPath, 'utf-8');
    const martyrs = parseCsv(content);
    const criticalCount = martyrs.filter((m) => m.margin < 15 || (m.level && m.level.toUpperCase() === 'CRITICO')).length;

    return NextResponse.json(
      {
        criticalCount,
        martyrs,
        latestFile: files[0].name,
      },
      { headers: CORS_HEADERS }
    );
  } catch (error) {
    console.error('Error reading latest margin report:', error);
    return NextResponse.json(
      { criticalCount: 0, martyrs: [], error: String(error) },
      { status: 500, headers: CORS_HEADERS }
    );
  }
}
