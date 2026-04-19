// ── UI 控制模組 ─────────────────────────────────────────────────────────

const FONT_SIZE_MAP = {
  S: { base: 12, result: 16, status: 12, tag: 11 },
  M: { base: 14, result: 16, status: 12, tag: 11 },
  L: { base: 16, result: 18, status: 13, tag: 12 },
  XL: { base: 18, result: 20, status: 14, tag: 12 },
};

function id(x) { return document.getElementById(x); }

function setFontSize(size) {
  const normalized = FONT_SIZE_MAP[size] ? size : "M";
  applyFontSize(normalized);
  localStorage.setItem("gitlab_ui_font_size", normalized);
}

function applyFontSize(size) {
  const cfg = FONT_SIZE_MAP[size] || FONT_SIZE_MAP.M;
  const root = document.documentElement;
  root.style.setProperty("--font-size-base", `${cfg.base}px`);
  root.style.setProperty("--font-size-result", `${cfg.result}px`);
  root.style.setProperty("--font-size-status", `${cfg.status}px`);
  root.style.setProperty("--font-size-tag", `${cfg.tag}px`);
  if (window.S) window.S.fontSize = size;
  
  document.querySelectorAll("[data-font-size]").forEach(btn => {
    const active = btn.dataset.fontSize === size;
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-pressed", active ? "true" : "false");
  });
}

function setTheme(theme) {
  const normalized = theme === "light" ? "light" : "dark";
  document.documentElement.dataset.theme = normalized;
  if (window.S) window.S.theme = normalized;
  localStorage.setItem("gitlab_ui_theme", normalized);
  const btn = id("theme-toggle");
  if (btn) btn.textContent = normalized === "light" ? "暗色" : "亮色";
}

function toggleTheme() {
  setTheme(document.documentElement.dataset.theme === "light" ? "dark" : "light");
}

function enterWorkspace() {
  document.body.classList.add("workspace-ready");
  updateSidebarStatus();
  requestAnimationFrame(() => scrollToSection("step1"));
}

function toggleConfigPanel() {
  const panel = id("sidebar-config-panel");
  const btn   = id("btn-config-toggle");
  if (!panel) return;
  const isOpen = panel.style.display === "flex";
  panel.style.display = isOpen ? "none" : "flex";
  if (btn) {
    btn.style.borderColor = isOpen ? "" : "var(--accent-dim)";
    btn.style.color       = isOpen ? "" : "var(--text-bright)";
  }
  // 展開時自動列入已儲存的內容
  if (!isOpen) updateSidebarStatus();
}

function updateSidebarStatus() {
  if (!window.S) return;
  const mode = window.S.projectId && window.S.token ? "API 模式" : "Selenium 模式";
  const project = window.S.projectId ? `Project ${window.S.projectId}` : "未設定 Project";
  const timeout = `Timeout ${window.S.timeout || 300}s`;
  const model = id("run-model") && id("run-model").value ? id("run-model").value : "尚未選模型";
  const el = id("sidebar-status");
  if (el) el.innerHTML = `${mode}<br>${project}<br>${timeout}<br>${model}`;
}

function scrollToSection(sectionId) {
  const el = id(sectionId);
  if (!el) return;
  el.scrollIntoView({ behavior: "smooth", block: "start" });
  setActiveNav(sectionId);
}

function setActiveNav(sectionId) {
  document.querySelectorAll(".nav-link").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.sectionTarget === sectionId);
  });
}

function switchMainView(viewId) {
  // 如果沒有這兩個 view（例如 login/dashboard 獨立頁面）則走頁面跳轉
  const dashView  = id('view-dashboard');
  const issueView = id('view-issue-tool');
  if (!dashView || !issueView) {
    if (viewId === 'dashboard') { window.location.href = '/dashboard'; return; }
    if (viewId === 'issue-tool') { window.location.href = '/issuearrange'; return; }
    return;
  }

  const isDash = viewId === 'dashboard';
  // 使用 visibility 控制顯示/隱藏，避免改 display 造成對內容的重繪
  dashView.style.display  = isDash ? 'flex' : 'none';
  issueView.style.display = isDash ? 'none' : 'contents';

  const navDash  = id('nav-dashboard');
  const navIssue = id('nav-issue-tool');
  if (navDash)  navDash.classList.toggle('active',  isDash);
  if (navIssue) navIssue.classList.toggle('active', !isDash);

  // 切到 Issue 整理左滾動到頃部
  if (!isDash) {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else {
    // 切回 Dashboard 時不需重載，將滾動迺回頁面頂部
    window.scrollTo({ top: 0, behavior: 'instant' });
  }
}

function initSectionObserver() {
  if (!("IntersectionObserver" in window)) return;
  const sections = ["step1", "step2", "step3"].map(id).filter(Boolean);
  const observer = new IntersectionObserver(entries => {
    const visible = entries
      .filter(entry => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (visible && id('view-issue-tool').style.display !== 'none') {
      // 這裡暫時不用自動改變側邊導航，因為被換成 views 切換了
    }
  }, { rootMargin: "-20% 0px -55% 0px", threshold: [0.1, 0.3, 0.6] });
  sections.forEach(section => observer.observe(section));
}

function openToolPanel(panel) {
  switchToolPanel(panel || "history");
  id("tool-panel-modal").classList.add("open");
  if (panel === "history" && window.loadHistory) window.loadHistory();
}

function switchToolPanel(panel) {
  const normalized = panel === "prompt" ? "prompt" : "history";
  const content = id("side-col");
  if (content) content.dataset.activePanel = normalized;
  const title = id("tool-panel-title");
  if (title) title.textContent = normalized === "prompt" ? "Prompt Review" : "歷史存檔";
  const historyTab = id("tool-tab-history");
  const promptTab = id("tool-tab-prompt");
  if (historyTab) historyTab.classList.toggle("active", normalized === "history");
  if (promptTab) promptTab.classList.toggle("active", normalized === "prompt");
}

function closeToolPanel(e) {
  if (e.target === id("tool-panel-modal")) closeToolPanelDirect();
}

function closeToolPanelDirect() {
  const modal = id("tool-panel-modal");
  if (modal) modal.classList.remove("open");
}

function closeModal(e) { if (e.target === id("modal")) closeModalDirect(); }
function closeModalDirect() {
  id("modal").classList.remove("open");
  if (window.S) window.S.activeModalFile = null;
  id("modal-rerun-llm").style.display = "none";
  id("modal-export-result").style.display = "none";
}

function copyModalContent() {
  navigator.clipboard.writeText(id("modal-content").textContent);
}

function openNewPromptModal() {
  id("new-prompt-name").value    = "";
  id("new-prompt-content").value = "";
  id("new-prompt-error").style.display = "none";
  id("modal-prompt").classList.add("open");
}

function closePromptModal(e)   { if (e.target === id("modal-prompt")) closePromptModalDirect(); }
function closePromptModalDirect() { id("modal-prompt").classList.remove("open"); }

function showSt(elId, type, msg) {
  const el = id(elId);
  if (!el) return;
  el.className = `status ${type}`;
  el.innerHTML = `<span class="dot"></span>${msg}`;
}

function setActive(stepId) {
  const el = id(stepId);
  if(!el) return;
  el.classList.remove("done"); el.classList.add("active");
  el.scrollIntoView({ behavior:"smooth", block:"nearest" });
  if (["step1", "step2", "step3"].includes(stepId)) setActiveNav(stepId);
}
function setDone(stepId) {
  const el = id(stepId);
  if(!el) return;
  el.classList.remove("active"); el.classList.add("done");
}

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function copyEl(elId) {
  const el = id(elId);
  if(!el) return;
  const text = el.tagName === "TEXTAREA" ? el.value : (el.dataset.raw || el.textContent);
  navigator.clipboard.writeText(text);
}

// init
document.addEventListener("DOMContentLoaded", () => {
    setTheme(localStorage.getItem("gitlab_ui_theme") || (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark"));
    applyFontSize(localStorage.getItem("gitlab_ui_font_size") || "M");
    initSectionObserver();

    // ── 無論在哪個頁面，都先把 Token / Project ID 恢復到 S ──
    // 這是多頁面架構的關鍵：dashboard.html / issuearrange.html 沒有登入表單，
    // 但仍需要 S.token / S.projectId，否則 API 請求不帶認證 header。
    const savedToken = sessionStorage.getItem("gitlab_token");
    const savedPid   = localStorage.getItem("gitlab_project_id");

    if (window.S) {
        if (savedToken) S.token     = savedToken;
        if (savedPid)   S.projectId = savedPid;
    }

    // 如果頁面上有 login 表單元素，也一并填入（login.html / issuearrange 的 step-config 區塊）
    if (savedPid) {
        const pidEl = id("cfg-project-id");
        if (pidEl) { pidEl.value = savedPid; }
        const remEl = id("cfg-remember-pid");
        if (remEl) remEl.checked = true;
    }
    if (savedToken) {
        const tokEl = id("cfg-token");
        if (tokEl) tokEl.value = savedToken;
    }
});
