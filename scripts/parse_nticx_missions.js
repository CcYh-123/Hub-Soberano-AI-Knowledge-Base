const fs = require("fs");
const t = fs.readFileSync("nticx_pro_notion.md", "utf8");
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
  missions.push({
    num: i + 1,
    title,
    Semana: Number(g(/\*\*Semana:\*\*\s*(\d+)/)),
    Tipo: g(/\*\*Tipo:\*\*\s*([^\n]+)/),
    Estado,
    Dificultad: g(/\*\*Dificultad:\*\*\s*([^\n]+)/),
    tema: g(/\*\*Tema Clase:\*\*\s*([^\n]+)/),
    Nivel: Number(g(/\*\*Nivel:\*\*\s*(\d+)/)),
  });
}
const map = { "Internet y conectividad": "Internet y Conectividad" };
missions.forEach((m) => {
  if (map[m.tema]) m.tema = map[m.tema];
});
console.log(JSON.stringify(missions, null, 2));
