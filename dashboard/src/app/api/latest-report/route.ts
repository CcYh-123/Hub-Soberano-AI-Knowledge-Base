import { NextResponse } from 'next/server';
import { existsSync, readdirSync, readFileSync, statSync } from 'fs';
import { join } from 'path';


const REPORTS_DIR = join(process.cwd(), '..', 'reports');
const FALLBACK_REPORTS_DIR = join(process.cwd(), 'reports');

export interface MartyrRow {
  sku: string;
  cost_supa: number;
  price: number;
  margin: number;
  gap: number;
  suggested_price: number;
  level: string;
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
      } else if (h === 'cost_supa' || h === 'price' || h === 'margin' || h === 'gap' || h === 'suggested_price') {
        row[h] = Number(v) || 0;
      } else {
        row[h] = v;
      }
    });
    rows.push(row as MartyrRow);
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

export async function GET() {
  try {
    const dir = getReportsDir();
    if (!dir) {
      return NextResponse.json({ criticalCount: 0, martyrs: [], latestFile: null });
    }

    const files = readdirSync(dir)
      .filter((f) => f.startsWith('reporte_margen_') && f.endsWith('.csv'))
      .map((f) => ({ name: f, mtime: statSync(join(dir, f)).mtime.getTime() }))
      .sort((a, b) => b.mtime - a.mtime);

    if (files.length === 0) {
      return NextResponse.json({ criticalCount: 0, martyrs: [], latestFile: null });
    }

    const latestPath = join(dir, files[0].name);
    const content = readFileSync(latestPath, 'utf-8');
    const martyrs = parseCsv(content);
    const criticalCount = martyrs.filter((m) => m.margin < 15 || (m.level && m.level.toUpperCase() === 'CRITICO')).length;

    return NextResponse.json({
      criticalCount,
      martyrs,
      latestFile: files[0].name,
    });
  } catch (error) {
    console.error('Error reading latest margin report:', error);
    return NextResponse.json({ criticalCount: 0, martyrs: [], error: String(error) }, { status: 500 });
  }
}
