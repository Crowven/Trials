const ADMIN_PASSWORD = "pressstart";

function toggleAnalysisFields(type) {
  document.querySelectorAll(".analysis-only").forEach((field) => {
    field.classList.toggle("hidden", type !== "analysis");
  });
}

function openAdminPanel() {
  document.getElementById("adminPanel").classList.add("active");
}

function closeAdminPanel() {
  document.getElementById("adminPanel").classList.remove("active");
}

function handleAuth() {
  const password = document.getElementById("adminPassword").value;
  const authSection = document.getElementById("authSection");
  const editorSection = document.getElementById("editorSection");
  if (password === ADMIN_PASSWORD) {
    authSection.classList.add("hidden");
    editorSection.classList.remove("hidden");
  } else {
    alert("Contraseña incorrecta. Pista: pressstart");
  }
}

function resetForm() {
  document.getElementById("articleForm").reset();
  toggleAnalysisFields("standard");
}

function handleArticleSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const title = document.getElementById("title").value.trim();
  const summary = document.getElementById("summary").value.trim();
  const cover = document.getElementById("cover").value.trim();
  const type = document.getElementById("type").value;
  const content = document.getElementById("content").value.trim();
  const platform = document.getElementById("platform").value.trim();
  const developer = document.getElementById("developer").value.trim();
  const genre = document.getElementById("genre").value.trim();
  const modes = document.getElementById("modes").value.trim();
  const screenshots = document
    .getElementById("screenshots")
    .value.split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  if (!title || !summary || !content) {
    alert("Completa título, resumen y contenido.");
    return;
  }

  const newArticle = {
    id: crypto.randomUUID(),
    title,
    summary,
    cover,
    type,
    content,
    createdAt: new Date().toISOString(),
  };

  if (type === "analysis") {
    newArticle.analysis = buildAnalysisContent({
      title,
      platform,
      developer,
      genre,
      modes,
      screenshots,
    });
  }

  const articles = getArticles();
  articles.push(newArticle);
  saveArticles(articles);
  renderArticles();
  resetForm();
  closeAdminPanel();
}

function initAdmin() {
  const openBtn = document.getElementById("openAdmin");
  const closeBtn = document.getElementById("closeAdmin");
  const loginBtn = document.getElementById("loginBtn");
  const typeSelect = document.getElementById("type");
  const form = document.getElementById("articleForm");

  if (openBtn) openBtn.addEventListener("click", openAdminPanel);
  if (closeBtn) closeBtn.addEventListener("click", closeAdminPanel);
  if (loginBtn) loginBtn.addEventListener("click", handleAuth);
  if (typeSelect)
    typeSelect.addEventListener("change", (e) => toggleAnalysisFields(e.target.value));
  if (form) form.addEventListener("submit", handleArticleSubmit);
}

document.addEventListener("DOMContentLoaded", initAdmin);
