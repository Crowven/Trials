const STORAGE_KEY = "pixelpress_articles";

function getArticles() {
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored ? JSON.parse(stored) : [];
}

function saveArticles(articles) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(articles));
}

function seedDemoContent() {
  const existing = getArticles();
  if (existing.length) return existing;

  const demoAnalysis = {
    id: crypto.randomUUID(),
    title: "Análisis - Nébula Raiders",
    summary: "Disparos espaciales con ritmo arcade y capas roguelike.",
    cover:
      "https://images.unsplash.com/photo-1527443224154-d130c1a7c160?auto=format&fit=crop&w=1200&q=80",
    type: "analysis",
    content:
      "Nébula Raiders apuesta por encuentros cortos, builds locas y un mapa que siempre sorprende. La progresión mete presión desde el primer salto hiperlumínico.",
    createdAt: new Date().toISOString(),
    analysis: buildAnalysisContent({
      title: "Nébula Raiders",
      platform: "PC / Xbox Series",
      developer: "Sunbyte Labs",
      genre: "Shooter roguelike",
      modes: "Singleplayer",
      screenshots: [
        "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?auto=format&fit=crop&w=900&q=80",
        "https://images.unsplash.com/photo-1447433819943-74a20887a81e?auto=format&fit=crop&w=900&q=80",
      ],
    }),
  };

  const demoStandard = {
    id: crypto.randomUUID(),
    title: "Evento multijugador sorpresa en Pixel City",
    summary: "El juego sandbox recibirá 3 mapas gratuitos y un modo foto colaborativo.",
    cover:
      "https://images.unsplash.com/photo-1527437934671-61474b530017?auto=format&fit=crop&w=1200&q=80",
    type: "standard",
    content:
      "Pixel City añade cuatro eventos dinámicos semanales y desbloquea skins temáticas. Las partidas privadas ahora permiten moderación en vivo.",
    createdAt: new Date().toISOString(),
  };

  const seed = [demoAnalysis, demoStandard];
  saveArticles(seed);
  return seed;
}

function renderArticles() {
  const listContainer = document.getElementById("listado");
  if (!listContainer) return;
  const articles = getArticles();
  if (!articles.length) {
    listContainer.innerHTML = `<div class="card">Aún no hay artículos. Abre el panel de redactor para crear uno.</div>`;
    return;
  }

  listContainer.innerHTML = articles
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    .map((article) => {
      const typeLabel = article.type === "analysis" ? "Análisis" : "Estándar";
      return `
        <article class="card">
          <span class="type">${typeLabel}</span>
          ${article.cover ? `<img src="${article.cover}" alt="${article.title}">` : ""}
          <div class="meta">${new Date(article.createdAt).toLocaleDateString("es-ES")}</div>
          <h3>${article.title}</h3>
          <p>${article.summary}</p>
          <a class="btn secondary" href="article.html?id=${article.id}">Leer</a>
        </article>
      `;
    })
    .join("");
}

function getArticleFromQuery() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get("id");
  const articles = getArticles();
  if (!id) return articles[0];
  return articles.find((a) => a.id === id);
}

function renderArticleDetail() {
  const article = getArticleFromQuery();
  const container = document.getElementById("articleDetail");
  if (!container) return;
  if (!article) {
    container.innerHTML = "<p>No se encontró el artículo solicitado.</p>";
    return;
  }

  container.querySelector("h1").textContent = article.title;
  container.querySelector(".summary").textContent = article.summary;
  const coverEl = container.querySelector(".cover");
  if (article.cover) {
    coverEl.src = article.cover;
    coverEl.alt = article.title;
    coverEl.classList.remove("hidden");
  } else {
    coverEl.classList.add("hidden");
  }

  container.querySelector(".article-meta").innerHTML = `
    <span class="badge">${article.type === "analysis" ? "Análisis" : "Artículo"}</span>
    <span class="meta">${new Date(article.createdAt).toLocaleString("es-ES")}</span>
  `;

  container.querySelector(".content").innerHTML = `<p>${article.content}</p>`;

  const analysisBlock = document.getElementById("analysisBlock");
  if (article.type === "analysis" && analysisBlock) {
    analysisBlock.innerHTML = renderAnalysisSection(article.analysis);
    analysisBlock.classList.remove("hidden");
  } else {
    analysisBlock.classList.add("hidden");
  }

  setupComments(article.id);
}

function setupComments(articleId) {
  const list = document.getElementById("commentList");
  const form = document.getElementById("commentForm");
  if (!list || !form) return;

  const key = `${STORAGE_KEY}_comments_${articleId}`;

  function loadComments() {
    return JSON.parse(localStorage.getItem(key) || "[]");
  }

  function saveComments(comments) {
    localStorage.setItem(key, JSON.stringify(comments));
  }

  function renderComments() {
    const comments = loadComments();
    if (!comments.length) {
      list.innerHTML = '<p class="meta">Sé el primero en comentar.</p>';
      return;
    }
    list.innerHTML = comments
      .map(
        (comment) => `
          <div class="comment">
            <div class="meta">${comment.author} · ${new Date(comment.date).toLocaleString("es-ES")}</div>
            <p>${comment.text}</p>
          </div>
        `
      )
      .join("");
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const author = document.getElementById("commentAuthor").value.trim() || "Anónimo";
    const text = document.getElementById("commentText").value.trim();
    if (!text) return;
    const comments = loadComments();
    comments.push({ author, text, date: new Date().toISOString() });
    saveComments(comments);
    form.reset();
    renderComments();
  });

  renderComments();
}

function attachActions() {
  const seedBtn = document.getElementById("seedContent");
  if (seedBtn) {
    seedBtn.addEventListener("click", () => {
      localStorage.removeItem(STORAGE_KEY);
      seedDemoContent();
      renderArticles();
    });
  }
}

function init() {
  seedDemoContent();
  renderArticles();
  renderArticleDetail();
  attachActions();
}

document.addEventListener("DOMContentLoaded", init);

// Exponer helpers
window.getArticles = getArticles;
window.saveArticles = saveArticles;
window.seedDemoContent = seedDemoContent;
