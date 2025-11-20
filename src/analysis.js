const ANALYSIS_BADGES = ["Rendimiento sólido", "Narrativa destacada", "Innovación", "Modo cooperativo", "Gran banda sonora"];

function buildAnalysisContent(game) {
  const fallback = {
    title: game.title || "Juego misterioso",
    platform: game.platform || "PC",
    developer: game.developer || "Estudio indie",
    genre: game.genre || "Acción",
    modes: game.modes || "Singleplayer",
    screenshots: game.screenshots || [],
  };

  return {
    techSheet: [
      { label: "Plataforma", value: fallback.platform },
      { label: "Desarrolladora", value: fallback.developer },
      { label: "Género", value: fallback.genre },
      { label: "Modos", value: fallback.modes },
    ],
    pros: ["Gunplay satisfactorio", "Arte cuidado", "Soporte postlanzamiento", "Buen rendimiento"],
    cons: ["UI sobrecargada", "Misiones secundarias repetitivas"],
    summary: `${fallback.title} sabe equilibrar su identidad con mecánicas familiares. La campaña mantiene ritmo y las actividades secundarias se sienten más vivas gracias a eventos dinámicos.`,
    comparison: `Si disfrutas de ${fallback.genre.toLowerCase()} como los clásicos recientes, encontrarás sensaciones similares pero con una capa de personalidad propia.`,
    verdict: "Una propuesta que brilla por su pulido técnico y ritmo constante, ideal para sesiones cortas y largas.",
    metacritic: simulateMetacritic(),
    screenshots: fallback.screenshots,
  };
}

function simulateMetacritic() {
  return Math.floor(70 + Math.random() * 30);
}

function renderAnalysisSection(analysis) {
  if (!analysis) return "";
  const pros = analysis.pros?.map((item) => `<li>${item}</li>`).join("") || "";
  const cons = analysis.cons?.map((item) => `<li>${item}</li>`).join("") || "";
  const tech = analysis.techSheet
    ?.map((entry) => `<div class="badge">${entry.label}: ${entry.value}</div>`)
    .join("") || "";
  const shots = analysis.screenshots?.length
    ? `<div class="screenshot-grid">${analysis.screenshots
        .map((src) => `<img src="${src.trim()}" alt="Captura">`)
        .join("")}</div>`
    : "";
  const badges = ANALYSIS_BADGES.sort(() => 0.5 - Math.random())
    .slice(0, 3)
    .map((badge) => `<span class="badge">${badge}</span>`) 
    .join("");

  return `
    <div class="grid-two">
      <div>
        <h3>Ficha técnica</h3>
        <div class="tag-list">${tech}</div>
      </div>
      <div>
        <h3>Valoración global</h3>
        <p>${analysis.verdict}</p>
        <div class="tag-list">${badges}</div>
        <p class="meta-score">Metacritic simulado: <strong>${analysis.metacritic}</strong>/100</p>
      </div>
    </div>
    <div class="pros-cons">
      <div>
        <h3>Pros</h3>
        <ul>${pros}</ul>
      </div>
      <div>
        <h3>Contras</h3>
        <ul>${cons}</ul>
      </div>
    </div>
    <div>
      <h3>Resumen</h3>
      <p>${analysis.summary}</p>
    </div>
    <div>
      <h3>Comparativa</h3>
      <p>${analysis.comparison}</p>
    </div>
    <div>
      <h3>Capturas</h3>
      ${shots || '<p class="meta">Aún no hay capturas añadidas.</p>'}
    </div>
  `;
}

// Exponer funciones en window para otros scripts
window.buildAnalysisContent = buildAnalysisContent;
window.renderAnalysisSection = renderAnalysisSection;
window.simulateMetacritic = simulateMetacritic;
