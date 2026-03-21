const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const root = path.join(__dirname, "..");
const t = fs.readFileSync(path.join(root, "nticx_pro_notion.md"), "utf8");
const parts = t.split(/^### MISIÓN \d+:/m).slice(1);
const missions = [];
for (let i = 0; i < parts.length; i++) {
  const title = parts[i].split(/\n/)[0].trim();
  const b = parts[i];
  const g = (re) => {
    const m = b.match(re);
    return m ? m[1].trim() : null;
  };
  let Estado = g(/\*\*Estado:\*\*\s*([^\n]+)/);
  if (Estado) Estado = Estado.replace(/ \(se desbloquea[^)]*\)/, "");
  let tema = g(/\*\*Tema Clase:\*\*\s*([^\n]+)/);
  if (tema === "Internet y conectividad") tema = "Internet y Conectividad";
  missions.push({
    Name: `Misión ${i + 1}: ${title}`,
    Semana: Number(g(/\*\*Semana:\*\*\s*(\d+)/)),
    Tipo: g(/\*\*Tipo:\*\*\s*([^\n]+)/),
    Estado,
    Dificultad: g(/\*\*Dificultad:\*\*\s*([^\n]+)/),
    "Tema Clase": tema,
    Nivel: Number(g(/\*\*Nivel:\*\*\s*(\d+)/)),
  });
}

const chunk = (arr, n) => {
  const out = [];
  for (let i = 0; i < arr.length; i += n) out.push(arr.slice(i, i + n));
  return out;
};

const batches = chunk(missions, 12);
batches.forEach((batch, bi) => {
  const pages = batch.map((p) => ({
    properties: p,
    content:
      "### 📋 Contenido\nAbrí `nticx_pro_notion.md` en el proyecto, buscá esta misión y copiá el bloque completo (Objetivo, Misión, Entrega) dentro de esta página.",
  }));
  fs.writeFileSync(
    path.join(root, `missions_batch_${bi + 1}.json`),
    JSON.stringify({ pages }, null, 2),
    "utf8"
  );
});
console.log("Wrote missions_batch_1.json ..", batches.length);
