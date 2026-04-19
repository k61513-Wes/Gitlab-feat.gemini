// ── 業務層邏輯 ────────────────────────────────────────────────────────

window.S = {
  username: "", password: "", projectId: "", token: "", timeout: 300,
  running: false, stopFlag: false, modelChain: [], selectedModel: "", fontSize: "M", theme: "dark",
  issueJobs: [], selectedIssueId: "", historyFiles: [], activeModalFile: null,
  lastResultMeta: null, lastExportMeta: null,
  dash: { issues: [], milestones: [], projectId: null, pageOffset: 1, hasMore: false, repoUrl: "" }
};
let _abortController = null;

async function api(path, body, signalOrMethod) {
  const isSignal = signalOrMethod instanceof AbortSignal;
  const opts = {
    method: (typeof signalOrMethod === "string" ? signalOrMethod : null) || (body ? "POST" : "GET"),
    headers: body ? { "Content-Type": "application/json" } : {},
  };
  if (body) opts.body = JSON.stringify(body);
  if (isSignal) opts.signal = signalOrMethod;
  const res = await fetch(path, opts);
  let data;
  try {
    data = await res.json();
  } catch {
    throw new Error(`伺服器錯誤（HTTP ${res.status}），回應非 JSON 格式`);
  }
  if (!res.ok && data.error) {
    throw new Error(data.error);
  }
  return data;
}

// ── Config ─────────────────────────────────────────────────────────────
function saveConfig() {
  const pid     = id("cfg-project-id").value.trim();
  const tok     = id("cfg-token").value.trim();
  const u       = id("cfg-user").value.trim();
  const p       = id("cfg-pass").value.trim();
  const timeout = parseInt(id("cfg-timeout").value.trim()) || 300;

  const hasApi = pid && tok;
  const hasSel = u && p;

  if (!hasApi && !hasSel) {
    showSt("st-config","error","請填寫 Project ID + API Token（或備用帳號密碼）");
    return;
  }
  S.projectId = pid; S.token = tok;
  S.username  = u;   S.password = p;
  S.timeout   = timeout;

  // 暫存設定到 localStorage
  if (id("cfg-remember-pid").checked) {
    localStorage.setItem("gitlab_project_id", pid);
  } else {
    localStorage.removeItem("gitlab_project_id");
  }
  // Token 暫存（sessionStorage 開瀏覽器進程內有效）
  if (tok) sessionStorage.setItem("gitlab_token", tok);
  else sessionStorage.removeItem("gitlab_token");

  const modeLabel = hasApi ? `API 模式（Project ${pid}）` : "Selenium 模式（備用）";
  showSt("st-config","success",`✓ 設定已儲存（${modeLabel}，Timeout ${timeout}s）`);
  // 這些元素只存在於 issuearrange.html，login.html 上不存在
  const badgeEl = id("badge-config");
  if (badgeEl) badgeEl.textContent = hasApi ? "API 模式" : "Selenium";
  if (id("step-config")) setDone("step-config");
  if (id("btn-start"))      id("btn-start").disabled      = false;
  if (id("btn-scrape-only"))id("btn-scrape-only").disabled = false;
  if (id("btn-llm-only"))   id("btn-llm-only").disabled   = false;
  if (id("btn-excel"))      id("btn-excel").disabled      = false;
  if (id("step1"))          enterWorkspace();
  // 儲存完成後跳轉到 Dashboard
  setTimeout(() => { window.location.href = '/dashboard'; }, 300);
}

async function checkHealth() {
  const btn = id("btn-health");
  btn.disabled = true; btn.textContent = "檢查中...";
  showSt("st-config","info","正在檢查 Gemini CLI...");
  try {
    const d = await api("/api/health");
    S.modelChain = Array.isArray(d.model_chain) ? d.model_chain : [];
    refreshModelSelect();
    if (d.cli_found) {
      let msg = `✓ Gemini CLI 可用\n路徑: ${d.gemini_cli}\nTimeout: ${d.timeout}s`;
      const enabledModels = S.modelChain.filter(item => item && item.allowed).map(item => item.label);
      if (enabledModels.length) {
        msg += `\n可用模型: ${enabledModels.join(" / ")}`;
      }
      showSt("st-config","success", msg.split("\n").join(" | "));
    }
    else showSt("st-config","error",`找不到 Gemini CLI：${d.gemini_cli}，請確認已安裝或設定 GEMINI_CLI_PATH`);
  } catch(e) { showSt("st-config","error",`健康檢查失敗：${e.message}`); }
  finally { btn.disabled = false; btn.textContent = "檢查 Gemini CLI"; }
}

async function resolveModelChain() {
  if (Array.isArray(S.modelChain) && S.modelChain.length) return S.modelChain;
  const d = await api("/api/health");
  S.modelChain = Array.isArray(d.model_chain) ? d.model_chain : [];
  refreshModelSelect();
  return S.modelChain;
}

function refreshModelSelect() {
  const sel = id("run-model");
  if (!sel) return;
  const current = S.selectedModel || sel.value;
  const models = (S.modelChain || []).filter(item => item && item.allowed && item.model_id);
  sel.innerHTML = "";
  if (!models.length) {
    sel.innerHTML = '<option value="">請先檢查 Gemini CLI</option>';
    S.selectedModel = "";
    return;
  }
  models.forEach(item => {
    const opt = document.createElement("option");
    opt.value = item.model_id;
    opt.textContent = `${item.label} (${item.model_id})`;
    sel.appendChild(opt);
  });
  sel.value = models.some(item => item.model_id === current) ? current : models[0].model_id;
  S.selectedModel = sel.value;
  updateSidebarStatus();
}

function getSelectedModel() {
  const selected = id("run-model").value.trim();
  const model = (S.modelChain || []).find(item => item.model_id === selected);
  if (!selected || !model || !model.allowed) return null;
  S.selectedModel = selected;
  return model;
}

function isFilterUrl(text) {
  const lines = text.trim().split("\n").filter(l => l.trim());
  if (lines.length !== 1) return false;
  return /\/-\/issues\/?\?/.test(lines[0].trim());
}

function renderIssuePreviewList(issues, headerText) {
  id("load-count").textContent = headerText;
  const listEl = id("load-issue-list");
  listEl.innerHTML = issues.map(iss => {
    const assigneesText = (iss.assignees || []).join(", ") || "—";
    const milestoneText = iss.milestone ? iss.milestone.title : "—";
    const stateColor    = iss.state === "opened"
      ? "rgba(61,214,140,0.1);color:var(--green)"
      : "rgba(110,110,136,0.2);color:var(--text-dim)";
    return `
      <div style="padding:8px 10px;background:var(--bg3);border:1px solid var(--border);border-radius:6px;display:flex;align-items:flex-start;gap:8px">
        <span style="font-family:var(--mono);font-size:10px;color:var(--text-dim);flex-shrink:0;padding-top:3px;min-width:30px">#${iss.iid}</span>
        <div style="flex:1;min-width:0">
          <div style="font-size:12px;color:var(--text);overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${iss.title}">${iss.title}</div>
          <div style="font-size:10px;color:var(--text-dim);margin-top:3px;display:flex;gap:10px;flex-wrap:wrap;font-family:var(--mono)">
            <span title="被指派人">👤 ${assigneesText}</span>
            <span title="Milestone">🏁 ${milestoneText}</span>
          </div>
        </div>
        <span style="font-size:10px;padding:1px 6px;border-radius:3px;background:${stateColor};flex-shrink:0;white-space:nowrap">${iss.state}</span>
      </div>`;
  }).join("");
  id("load-preview").style.display = "flex";
}

async function smartLoadList() {
  const raw = id("url-list").value.trim();
  if (!raw) { showSt("st-load", "error", "請先貼入 URL"); return; }
  if (isFilterUrl(raw)) {
    await resolveFilterUrl(raw.trim());
  } else {
    const urls = raw.split("\n").map(u => u.trim()).filter(u => u.startsWith("http"));
    if (!urls.length) {
      showSt("st-load", "error", "未偵測到有效的 Issue URL（需以 http 開頭）");
      return;
    }
    await previewIssueUrls(urls);
  }
}

async function previewIssueUrls(urls) {
  const projectId = parseInt(S.projectId) || parseInt(id("cfg-project-id").value.trim());
  const token     = S.token || id("cfg-token").value.trim();
  const btn = id("btn-load");
  btn.disabled = true; btn.textContent = "取得中...";
  showSt("st-load", "info", `正在取得 ${urls.length} 個 Issue 資訊...`);
  id("load-preview").style.display = "none";
  try {
    if (!projectId) throw new Error("請先在「連線設定」填寫 Project ID 並儲存");
    const payload = { urls, project_id: projectId };
    if (token) payload.private_token = token;
    const d = await api("/api/preview_issues", payload);
    if (d.error) throw new Error(d.error);
    const errCount = (d.errors || []).length;
    const header   = errCount ? `${d.count} 個 Issue（${errCount} 筆無法取得）` : `${d.count} 個 Issue`;
    renderIssuePreviewList(d.issues, header);
    createIssueJobs(d.issues.map(i => i.web_url), d.issues);
    const msg = errCount ? `✓ 已載入 ${d.count} 筆，${errCount} 筆失敗（見清單）` : `✓ 已載入 ${d.count} 個 Issue`;
    showSt("st-load", "success", msg);
  } catch(e) {
    id("load-preview").style.display = "none";
    showSt("st-load", "error", `無法取得 Issue 詳情：${e.message}`);
  } finally {
    btn.disabled = false; btn.textContent = "🔍 載入清單";
  }
}

async function resolveFilterUrl(filterUrl) {
  const projectId = parseInt(S.projectId) || parseInt(id("cfg-project-id").value.trim());
  const token     = S.token || id("cfg-token").value.trim();
  if (!filterUrl) { showSt("st-load", "error", "請先貼入篩選頁面 URL"); return; }
  if (!projectId) { showSt("st-load", "error", "請先在「連線設定」填寫 Project ID 並儲存"); return; }
  const btn = id("btn-load");
  btn.disabled = true; btn.textContent = "取得中...";
  showSt("st-load", "info", "正在呼叫 GitLab API...");
  id("load-preview").style.display = "none";
  const payload = { filter_url: filterUrl, project_id: projectId };
  if (token) payload.private_token = token;
  try {
    const d = await api("/api/resolve_filter_url", payload);
    if (d.error) throw new Error(d.error);
    id("url-list").value = d.issues.map(i => i.web_url).join("\n");
    renderIssuePreviewList(d.issues, `找到 ${d.count} 個 Issue（專案：${d.project}）`);
    createIssueJobs(d.issues.map(i => i.web_url), d.issues);
    showSt("st-load", "success", `✓ 已解析 ${d.count} 個 Issue，URL 已填入清單，可直接開始處理`);
  } catch(e) {
    showSt("st-load", "error", e.message);
  } finally {
    btn.disabled = false; btn.textContent = "🔍 載入清單";
  }
}

// ── Batch processing ───────────────────────────────────────────────────
async function startBatch() { await runBatch("all"); }

function getRunContext(requireModel = false) {
  const useApi = S.projectId && S.token;
  if (!useApi && (!S.username || !S.password)) {
    throw new Error("請先儲存連線設定（Project ID + API Token，或備用帳號密碼）");
  }
  let selectedModel = null;
  if (requireModel) {
    selectedModel = getSelectedModel();
    if (!selectedModel) throw new Error("請先選擇一個可用的 LLM 模型");
  }
  return { useApi, selectedModel };
}

function extractIssueId(url, fallback) {
  try {
    const m = new URL(url).pathname.match(/\/(?:issues|work_items)\/(\d+)$/);
    return m ? m[1] : String(fallback + 1);
  } catch {
    return String(fallback + 1);
  }
}

function createIssueJobs(urls, previews = []) {
  S.issueJobs = (urls || []).map((url, idx) => {
    const preview = previews.find(item => item.web_url === url) || {};
    const issueId = preview.iid ? String(preview.iid) : extractIssueId(url, idx);
    return {
      uid: `${issueId}-${idx}`,
      id: issueId,
      url,
      title: preview.title || shortUrl(url),
      modelName: S.selectedModel || "",
      promptFilename: id("prompt-select").value || "",
      status: { scrape: "waiting", llm: "waiting", export: "waiting" },
      rawText: "",
      llmResult: "",
      exportResult: "",
      files: { raw: "", result: "", export: "" },
      error: null,
    };
  });
  S.selectedIssueId = S.issueJobs[0] ? S.issueJobs[0].uid : "";
  renderIssueList();
}

function ensureIssueJobsFromInput() {
  const raw = id("url-list").value.trim();
  const urls = raw.split("\n").map(u => u.trim()).filter(u => u.startsWith("http"));
  if (!urls.length) throw new Error("請輸入至少一個有效的 URL");
  const currentUrls = S.issueJobs.map(job => job.url).join("\n");
  if (!S.issueJobs.length || currentUrls !== urls.join("\n")) createIssueJobs(urls);
  return S.issueJobs;
}

async function runBatch(mode) {
  try {
    const jobs = ensureIssueJobsFromInput();
    await resolveModelChain();
    const requireModel = mode === "all" || mode === "llm";
    const ctx = getRunContext(requireModel);
    S.running = true; S.stopFlag = false;
    setBatchButtonsDisabled(true);
    id("btn-stop").disabled = false;
    setActive("step2");
    id("badge-step2").textContent = `0 / ${jobs.length}`;
    let doneCount = 0;
    for (const job of jobs) {
      if (S.stopFlag) break;
      try {
        if (mode === "scrape") {
          await runScrape(job, ctx);
        } else if (mode === "llm") {
          if (job.status.scrape !== "success") {
            markJobSkipped(job, "llm", "尚未 scrape，已略過");
            continue;
          }
          await runLlm(job, ctx.selectedModel);
        } else {
          await runScrape(job, ctx);
          if (S.stopFlag) break;
          await runLlm(job, ctx.selectedModel);
          if (S.stopFlag) break;
          await runExport(job);
        }
        doneCount++;
      } catch (e) {
        job.error = e.name === "AbortError" ? "已中止" : e.message;
        if (e.name === "AbortError" || S.stopFlag) break;
      } finally {
        id("badge-step2").textContent = `${doneCount} / ${jobs.length}`;
        renderIssueList();
      }
    }
    if (!S.stopFlag) {
      showSt("st-batch","success",`批次完成，共 ${doneCount}/${jobs.length} 筆完成`);
      setDone("step2");
      if (S.issueJobs.some(job => job.llmResult || job.exportResult)) {
        setActive("step3");
        id("badge-step3").textContent = "完成";
        setDone("step3");
      }
    } else {
      showSt("st-batch","error","⏹ 已中止");
    }
    loadHistory();
  } catch(e) {
    showSt("st-batch","error", e.message);
  } finally {
    S.running = false; _abortController = null;
    setBatchButtonsDisabled(false);
    id("btn-stop").disabled = true;
  }
}

function setBatchButtonsDisabled(disabled) {
  ["btn-start", "btn-scrape-only", "btn-llm-only", "btn-excel"].forEach(btnId => {
    const el = id(btnId);
    if (el) el.disabled = disabled;
  });
}

function setJobStatus(job, phase, status, error = null) {
  job.status[phase] = status;
  job.error = error;
  renderIssueList();
}

function markJobSkipped(job, phase, reason) {
  job.status[phase] = "skipped";
  job.error = reason;
  renderIssueList();
}

async function runScrapeById(uid) {
  const job = S.issueJobs.find(item => item.uid === uid);
  if (!job) return;
  try {
    const ctx = getRunContext(false);
    setBatchButtonsDisabled(true);
    await runScrape(job, ctx);
    showSt("st-batch", "success", `#${job.id} scrape 完成`);
  } catch(e) {
    job.error = e.message;
    showSt("st-batch", "error", e.message);
    renderIssueList();
  } finally {
    setBatchButtonsDisabled(false);
  }
}

async function runLlmById(uid) {
  const job = S.issueJobs.find(item => item.uid === uid);
  if (!job) return;
  try {
    await resolveModelChain();
    const { selectedModel } = getRunContext(true);
    if (job.status.scrape !== "success") throw new Error("請先完成 Scrape 才能執行 LLM");
    setBatchButtonsDisabled(true);
    await runLlm(job, selectedModel);
    showSt("st-batch", "success", `#${job.id} LLM 完成`);
  } catch(e) {
    job.error = e.message;
    showSt("st-batch", "error", e.message);
    renderIssueList();
  } finally {
    setBatchButtonsDisabled(false);
  }
}

async function runExportById(uid) {
  const job = S.issueJobs.find(item => item.uid === uid);
  if (!job) return;
  try {
    if (job.status.llm !== "success") throw new Error("請先完成 LLM 才能 Export");
    setBatchButtonsDisabled(true);
    await runExport(job);
    showSt("st-batch", "success", `#${job.id} Export 完成`);
  } catch(e) {
    job.error = e.message;
    showSt("st-batch", "error", e.message);
    renderIssueList();
  } finally {
    setBatchButtonsDisabled(false);
  }
}

async function runScrape(job, ctx) {
  setJobStatus(job, "scrape", "running");
  showSt("st-batch","info",`Scrape #${job.id}：${shortUrl(job.url)}`);
  _abortController = new AbortController();
  const payload = ctx.useApi
    ? { url: job.url, project_id: parseInt(S.projectId), private_token: S.token }
    : { url: job.url, username: S.username, password: S.password };
  const scrapeRes = await api(ctx.useApi ? "/api/scrape_api" : "/api/scrape", payload, _abortController.signal);
  if (scrapeRes.error) throw new Error(scrapeRes.error);
  job.rawText = scrapeRes.raw_text || "";
  job.files.raw = scrapeRes.saved_raw || "";
  if (scrapeRes.issue && scrapeRes.issue.title) job.title = scrapeRes.issue.title;
  setJobStatus(job, "scrape", "success");
  return scrapeRes;
}

async function runLlm(job, selectedModel) {
  if (!job.rawText) throw new Error("缺少 raw text，請先執行 Scrape");
  setJobStatus(job, "llm", "running");
  job.modelName = selectedModel.model_id;
  job.promptFilename = id("prompt-select").value || "";
  showSt("st-batch","info",`LLM #${job.id}：${selectedModel.label}`);
  _abortController = new AbortController();
  const processRes = await api("/api/process", {
    raw_text: job.rawText,
    system_prompt: id("process-prompt").value.trim(),
    url: job.url,
    timeout: S.timeout || 300,
    model_name: selectedModel.model_id,
    model_label: selectedModel.label,
  }, _abortController.signal);
  if (processRes.error) throw new Error(processRes.error);
  job.llmResult = processRes.result || "";
  job.files.result = processRes.saved_result || "";
  setJobStatus(job, "llm", "success");
  showLastResult(job.llmResult, job.exportResult || "", {
    url: job.url,
    modelName: processRes.used_model || selectedModel.model_id,
  });
  return processRes;
}

async function runExport(job) {
  if (!job.llmResult) throw new Error("缺少 LLM result，請先執行 LLM");
  setJobStatus(job, "export", "running");
  showSt("st-batch","info",`Export #${job.id}`);
  _abortController = new AbortController();
  const exportRes = await api("/api/export", {
    processed_text: job.llmResult,
    export_prompt: id("export-prompt").value.trim(),
  }, _abortController.signal);
  if (exportRes.error) throw new Error(exportRes.error);
  job.exportResult = exportRes.output || "";
  setJobStatus(job, "export", "success");
  showLastResult(job.llmResult, job.exportResult, {
    url: job.url,
    modelName: job.modelName || "unknown-model",
  });
  return exportRes;
}

function stopBatch() {
  S.stopFlag = true;
  if (_abortController) _abortController.abort();
  id("btn-stop").disabled = true;
  showSt("st-batch","error","⏹ 正在中止...");
}

async function exportExcel() {
  const urls = id("url-list").value.trim().split("\n").map(u => u.trim()).filter(Boolean);
  if (!urls.length) { alert("請先填入 Issue URL"); return; }
  const btn = id("btn-excel");
  btn.disabled = true;
  showSt("st-batch", "info", "⏳ 正在產生 Excel，請稍候...");
  try {
    const res = await api("/api/batch_export_excel", {
      urls,
      project_id: S.projectId ? parseInt(S.projectId) : null,
      private_token: S.token || null,
    });
    if (res.error) throw new Error(res.error);
    const errCount = (res.errors || []).length;
    const msg = errCount
      ? `✓ Excel 已產出（${res.count} 筆成功，${errCount} 筆失敗）`
      : `✓ Excel 已產出，共 ${res.count} 筆`;
    showSt("st-batch", "success", msg);
    const link = document.createElement("a");
    link.href = `/api/outputs/${res.filename}`;
    link.download = res.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    loadHistory();
  } catch(e) {
    showSt("st-batch", "error", `✗ Excel 匯出失敗：${e.message}`);
  } finally {
    btn.disabled = false;
  }
}

function phaseClass(status) {
  if (status === "success") return "done";
  if (status === "error") return "error";
  if (status === "running") return "running";
  if (status === "skipped") return "skipped";
  return "waiting";
}

function phaseText(status) {
  const map = {
    waiting: "等待中", running: "執行中", success: "完成", error: "失敗", skipped: "略過",
  };
  return map[status] || "等待中";
}

function renderIssueList() {
  const list = id("queue-list");
  if (!S.issueJobs.length) {
    list.innerHTML = '<div style="color:var(--text-dim);font-size:12px;padding:8px 0">尚未建立工作清單，請先填入 URL 並點擊「載入清單」或批次按鈕。</div>';
    return;
  }
  list.innerHTML = S.issueJobs.map(job => renderIssueCard(job)).join("");
}

function renderIssueCard(job) {
  const anyRunning = Object.values(job.status).includes("running") || S.running;
  const selected = S.selectedIssueId === job.uid ? " selected" : "";
  const scrapeDisabled = anyRunning ? "disabled" : "";
  const llmDisabled = anyRunning || job.status.scrape !== "success" ? "disabled" : "";
  const exportDisabled = anyRunning || job.status.llm !== "success" ? "disabled" : "";
  const files = [
    job.files.raw ? `<span onclick="viewFile('${escapeHtml(job.files.raw.replace(/\\/g, "/").split("/").pop())}')" title="${escapeHtml(job.files.raw)}">[raw] ${escapeHtml(job.files.raw.replace(/\\/g, "/").split("/").pop())}</span>` : "",
    job.files.result ? `<span onclick="viewFile('${escapeHtml(job.files.result.replace(/\\/g, "/").split("/").pop())}')" title="${escapeHtml(job.files.result)}">[result] ${escapeHtml(job.files.result.replace(/\\/g, "/").split("/").pop())}</span>` : "",
  ].filter(Boolean).join("");
  return `
    <div class="queue-item ${phaseClass(job.status.export === "success" ? "success" : job.status.llm === "success" ? "running" : job.status.scrape)}${selected}" onclick="selectIssueJob('${escapeHtml(job.uid)}')">
      <div class="qi-top">
        <div class="qi-main">
          <div class="qi-title" title="${escapeHtml(job.title)}">#${escapeHtml(job.id)} ${escapeHtml(job.title)}</div>
          <div class="qi-url" title="${escapeHtml(job.url)}">${escapeHtml(job.url)}</div>
        </div>
        <div class="qi-actions" onclick="event.stopPropagation()">
          <button class="btn-ghost" onclick="runScrapeById('${escapeHtml(job.uid)}')" ${scrapeDisabled}>Scrape</button>
          <button class="btn-ghost" onclick="runLlmById('${escapeHtml(job.uid)}')" ${llmDisabled}>Run LLM</button>
          <button class="btn-ghost" onclick="runExportById('${escapeHtml(job.uid)}')" ${exportDisabled}>Export</button>
        </div>
      </div>
      <div class="qi-phases">
        <div class="qi-phase ${phaseClass(job.status.scrape)}"><div class="qi-phase-name">Scrape</div><div class="qi-phase-state">${phaseText(job.status.scrape)}</div></div>
        <div class="qi-phase ${phaseClass(job.status.llm)}"><div class="qi-phase-name">LLM</div><div class="qi-phase-state">${phaseText(job.status.llm)}</div></div>
        <div class="qi-phase ${phaseClass(job.status.export)}"><div class="qi-phase-name">Export</div><div class="qi-phase-state">${phaseText(job.status.export)}</div></div>
      </div>
      <div class="qi-models">${job.modelName ? `<span class="qi-model-pill ok">${escapeHtml(job.modelName)}</span>` : ""}${job.promptFilename ? `<span class="qi-model-pill">${escapeHtml(job.promptFilename)}</span>` : ""}</div>
      ${job.error ? `<div class="qi-error">${escapeHtml(job.error)}</div>` : ""}
      <div class="qi-files">${files}</div>
    </div>`;
}

function selectIssueJob(uid) {
  S.selectedIssueId = uid;
  const job = S.issueJobs.find(item => item.uid === uid);
  renderIssueList();
  if (job && (job.llmResult || job.exportResult)) {
    showLastResult(job.llmResult || "", job.exportResult || "", {
      url: job.url,
      modelName: job.modelName || "unknown-model",
    });
  }
}

// ── Last result ──
const LLM_SECTION_DEFS = [
  { key: "problem", label: "問題說明", aliases: ["問題說明", "問題描述", "Issue 說明", "背景與問題"] },
  { key: "rootCause", label: "根本原因", aliases: ["根本原因", "原因分析", "Root Cause"] },
  { key: "solution", label: "解決方式", aliases: ["解決方式", "處理方式", "解法", "建議方案"] },
  { key: "test", label: "測試建議", aliases: ["測試建議", "測試方式", "測試項目"] },
  { key: "acceptance", label: "驗收標準", aliases: ["驗收標準", "驗收條件", "AC"] },
  { key: "todo", label: "待辦事項", aliases: ["待辦事項", "待辦", "Todo", "Action Items"] },
  { key: "consensus", label: "討論共識", aliases: ["討論共識", "討論結論", "共識"] },
  { key: "extra", label: "補充資訊", aliases: ["補充資訊", "補充內容", "其他", "其他資訊"] },
];

function normalizeHeading(text) {
  return (text || "")
    .replace(/^#+\s*/, "")
    .replace(/[：:]+$/, "")
    .replace(/[【】\[\]]/g, "")
    .trim()
    .toLowerCase();
}

function matchSectionKey(heading) {
  const normalized = normalizeHeading(heading);
  const hit = LLM_SECTION_DEFS.find(def =>
    def.aliases.some(alias => normalized.includes(normalizeHeading(alias)))
  );
  return hit ? hit.key : "other";
}

function parseLlmSections(text) {
  const source = (text || "").trim();
  if (!source) return { ok: false, sections: [] };

  const headingRe = /^#{1,3}\s+(.+?)\s*$/gm;
  const matches = [...source.matchAll(headingRe)];
  if (!matches.length) return { ok: false, sections: [] };

  const buckets = {};
  const order = [];
  matches.forEach((match, idx) => {
    const start = match.index + match[0].length;
    const end = idx + 1 < matches.length ? matches[idx + 1].index : source.length;
    const heading = match[1].trim();
    const key = matchSectionKey(heading);
    const label = key === "other" ? heading : (LLM_SECTION_DEFS.find(def => def.key === key) || {}).label;
    const body = source.slice(start, end).trim();
    const bucketKey = key === "other" ? `other:${heading}` : key;
    if (!buckets[bucketKey]) {
      buckets[bucketKey] = { key: bucketKey, label, body: "" };
      order.push(bucketKey);
    }
    buckets[bucketKey].body = [buckets[bucketKey].body, body].filter(Boolean).join("\n\n");
  });

  const sections = LLM_SECTION_DEFS.map(def => ({
    key: def.key,
    label: def.label,
    body: (buckets[def.key] && buckets[def.key].body) || "",
  }));
  order.filter(key => key.startsWith("other:")).forEach(key => sections.push(buckets[key]));
  return { ok: true, sections };
}

function renderLlmResult(container, text) {
  container.dataset.raw = text || "";
  container.innerHTML = "";
  const parsed = parseLlmSections(text);
  if (!parsed.ok) {
    container.className = "final-out result-fallback";
    container.textContent = text || "";
    return;
  }

  container.className = "final-out result-sections";
  parsed.sections.forEach(section => {
    const card = document.createElement("section");
    card.className = `result-card${section.body ? "" : " empty"}`;
    const title = document.createElement("h3");
    title.className = "result-card-title";
    title.textContent = section.label;
    const body = document.createElement("div");
    body.className = "result-card-body";
    body.textContent = section.body || "此段未由 LLM 輸出。";
    card.append(title, body);
    container.appendChild(card);
  });
}

function showLastResult(result, exportOutput, meta = {}) {
  renderLlmResult(id("last-result"), result);
  id("last-export").textContent = exportOutput;
  id("last-export").dataset.raw = exportOutput || "";
  id("last-result-wrap").style.display = "grid";
  id("last-result-empty").style.display = "none";
  S.lastResultMeta = { url: meta.url || "", modelName: meta.modelName || "unknown-model" };
  S.lastExportMeta = { url: meta.url || "", modelName: meta.modelName || "unknown-model" };
}

// ── History ──
async function loadHistory() {
  try {
    const d = await api("/api/outputs");
    S.historyFiles = d.files || [];
    renderHistoryList();
  } catch(e) {
    id("history-list").innerHTML = `<div style="color:var(--red);font-size:11px">${e.message}</div>`;
  }
}

function renderHistoryList() {
  const list = id("history-list");
  const query = (id("history-search") ? id("history-search").value : "").trim().toLowerCase();
  const kindFilter = id("history-kind") ? id("history-kind").value : "all";
  const files = (S.historyFiles || []).filter(f => {
    const kind = f.kind || inferOutputKind(f.filename);
    const matchKind = kindFilter === "all" || kind === kindFilter;
    const matchQuery = !query || f.filename.toLowerCase().includes(query);
    return matchKind && matchQuery;
  });
  if (!files.length) {
    list.innerHTML = '<div style="color:var(--text-dim);font-size:11px;padding:8px 0">沒有符合條件的存檔</div>';
    return;
  }
  list.innerHTML = files.map(f => {
    const kind = f.kind || inferOutputKind(f.filename);
    const label = kind === "raw" ? "爬取原始" : kind === "excel" ? "Excel" : "LLM 整理";
    return `
      <div class="hist-item" onclick="viewFile('${escapeHtml(f.filename)}')">
        <div class="hist-name">${escapeHtml(f.filename)}</div>
        <div class="hist-meta" style="display:flex;align-items:center;gap:6px;margin-top:3px;flex-wrap:wrap">
          <span class="hist-kind ${kind}">${label}</span>
          <span>${escapeHtml(f.mtime || "")}</span>
          <span>${((f.size || 0)/1024).toFixed(1)} KB</span>
        </div>
      </div>`;
  }).join("");
}

function inferOutputKind(filename) {
  if ((filename || "").endsWith(".xlsx")) return "excel";
  if ((filename || "").includes("_raw_")) return "raw";
  return "result";
}

async function viewFile(filename) {
  try {
    const kind = inferOutputKind(filename);
    if (kind === "excel") {
      const link = document.createElement("a");
      link.href = `/api/outputs/${encodeURIComponent(filename)}`;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      return;
    }
    const d = await api(`/api/outputs/${encodeURIComponent(filename)}`, null, "GET");
    S.activeModalFile = { filename, kind, content: d.content || "" };
    id("modal-title").textContent = filename;
    id("modal-content").textContent = d.content || "";
    id("modal-rerun-llm").style.display = kind === "raw" ? "inline-flex" : "none";
    id("modal-export-result").style.display = kind === "result" ? "inline-flex" : "none";
    id("modal").classList.add("open");
  } catch(e) {
    alert("無法讀取檔案：" + e.message);
  }
}

async function rerunLlmFromModal() {
  if (!S.activeModalFile || S.activeModalFile.kind !== "raw") return;
  try {
    await resolveModelChain();
    const { selectedModel } = getRunContext(true);
    showSt("st-batch", "info", `使用 ${selectedModel.label} 重新處理 raw`);
    const res = await api("/api/process", {
      raw_text: S.activeModalFile.content,
      system_prompt: id("process-prompt").value.trim(),
      url: "",
      timeout: S.timeout || 300,
      model_name: selectedModel.model_id,
      model_label: selectedModel.label,
    });
    if (res.error) throw new Error(res.error);
    showLastResult(res.result, "", { modelName: selectedModel.model_id });
    showSt("st-batch", "success", "Raw 重新執行 LLM 完成");
    closeModalDirect();
  } catch(e) {
    showSt("st-batch", "error", e.message);
  }
}

async function exportFromModal() {
  if (!S.activeModalFile || S.activeModalFile.kind !== "result") return;
  try {
    showSt("st-batch", "info", "正在將 result 重新 Export");
    const res = await api("/api/export", {
      processed_text: S.activeModalFile.content,
      export_prompt: id("export-prompt").value.trim(),
    });
    if (res.error) throw new Error(res.error);
    showLastResult(S.activeModalFile.content, res.output || "", { modelName: "history-result" });
    showSt("st-batch", "success", "Result 重新 Export 完成");
    closeModalDirect();
  } catch(e) {
    showSt("st-batch", "error", e.message);
  }
}

// ── Prompts ──
async function loadPrompts() {
  try {
    const d = await api("/api/prompts");
    const sel = id("prompt-select");
    const current = sel.value;
    sel.innerHTML = '<option value="">── 選擇模板 ──</option>';
    (d.prompts || []).forEach(p => {
      const opt = document.createElement("option");
      opt.value = p.filename;
      opt.textContent = p.name;
      sel.appendChild(opt);
    });
    if (current && [...sel.options].some(o => o.value === current)) sel.value = current;
    const cnt = (d.prompts || []).length;
    id("prompt-count").textContent = cnt ? `${cnt} 個模板` : "";
    if (sel.value) onPromptSelect();
  } catch(e) { console.warn("載入 prompt 清單失敗", e); }
}

async function onPromptSelect() {
  const filename = id("prompt-select").value;
  if (!filename) {
    id("prompt-preview").value = "";
    return;
  }
  try {
    const d = await api(`/api/prompts/${encodeURIComponent(filename)}`, null, "GET");
    if (d.error) throw new Error(d.error);
    id("process-prompt").value = d.content;
    id("prompt-preview").value = d.content;
    id("prompt-preview").readOnly = true;
  } catch(e) { alert("載入模板失敗：" + e.message); }
}

function copyPromptPreview() {
  navigator.clipboard.writeText(id("prompt-preview").value || id("process-prompt").value || "");
}

function togglePromptPreviewEdit() {
  const preview = id("prompt-preview");
  preview.readOnly = !preview.readOnly;
  if (!preview.value) preview.value = id("process-prompt").value;
  if (!preview.readOnly) preview.focus();
}

async function savePromptFromPreview(overwriteCurrent) {
  const content = id("prompt-preview").value.trim();
  const current = id("prompt-select").value;
  const nameInput = id("prompt-new-name").value.trim();
  const filename = overwriteCurrent ? current : nameInput;
  if (!filename) { alert(overwriteCurrent ? "請先選擇要覆蓋的 Prompt" : "請填寫新 Prompt 檔名"); return; }
  if (!content) { alert("Prompt 內容不可為空"); return; }
  if (overwriteCurrent && !confirm(`確定覆蓋「${current}」？`)) return;
  try {
    const normalized = filename.endsWith(".md") ? filename : `${filename}.md`;
    const d = await api("/api/prompts", { filename: normalized, content, overwrite: overwriteCurrent });
    if (d.error) throw new Error(d.error);
    await loadPrompts();
    id("prompt-select").value = d.filename || normalized;
    id("process-prompt").value = content;
    id("prompt-preview").value = content;
    id("prompt-preview").readOnly = true;
    id("prompt-new-name").value = "";
  } catch(e) { alert("儲存 Prompt 失敗：" + e.message); }
}

async function savePromptOverwrite() {
  const filename = id("prompt-select").value;
  const content  = id("process-prompt").value.trim();
  if (!filename) { alert("請先從下拉選單選擇一個模板，才能覆蓋儲存"); return; }
  if (!content)  { alert("Prompt 內容不可為空"); return; }
  if (!confirm(`確定要用目前內容覆蓋「${filename}」？`)) return;
  const btn = document.querySelector('button[onclick="savePromptOverwrite()"]');
  const orig = btn ? btn.textContent : "";
  try {
    const d = await api("/api/prompts", { filename, content, overwrite: true });
    if (d.error) throw new Error(d.error);
    if(btn) {
      btn.textContent = "✓ 已儲存"; btn.disabled = true;
      setTimeout(() => { btn.textContent = orig; btn.disabled = false; }, 1500);
    }
  } catch(e) { alert("覆蓋儲存失敗：" + e.message); }
}

async function deleteCurrentPrompt() {
  const filename = id("prompt-select").value;
  if (!filename) { alert("請先選擇要刪除的模板"); return; }
  if (!confirm(`確定要刪除「${filename}」？此操作無法復原。`)) return;
  try {
    const d = await api(`/api/prompts/${encodeURIComponent(filename)}`, null, "DELETE");
    if (d.error) throw new Error(d.error);
    id("process-prompt").value = "";
    await loadPrompts();
  } catch(e) { alert("刪除失敗：" + e.message); }
}

async function createNewPrompt() {
  const name    = id("new-prompt-name").value.trim();
  const content = id("new-prompt-content").value.trim();
  const errEl   = id("new-prompt-error");
  errEl.style.display = "none";
  if (!name && !content) { errEl.textContent = "⚠ 檔案名稱與 Prompt 內容皆不可為空"; errEl.style.display = "block"; return; }
  if (!name) { errEl.textContent = "⚠ 請填寫檔案名稱"; errEl.style.display = "block"; return; }
  if (!content) { errEl.textContent = "⚠ 請填寫 Prompt 內容"; errEl.style.display = "block"; return; }
  try {
    const filename = name.endsWith(".md") ? name : name + ".md";
    const d = await api("/api/prompts", { filename, content });
    if (d.error) throw new Error(d.error);
    await loadPrompts();
    id("prompt-select").value = filename;
    id("process-prompt").value = content;
    closePromptModalDirect();
  } catch(e) {
    errEl.textContent = "✗ " + e.message;
    errEl.style.display = "block";
  }
}

// init
document.addEventListener("DOMContentLoaded", () => {
  (function restoreProjectId() {
    const saved = localStorage.getItem("gitlab_project_id");
    if (saved) {
      if(id("cfg-project-id")) id("cfg-project-id").value = saved;
      if(id("cfg-remember-pid")) id("cfg-remember-pid").checked = true;
    }
  })();
  loadHistory();
  loadPrompts();
});

function parseGitlabUrlParts(url) {
  try {
    const u = new URL(url);
    const m = u.pathname.match(/(.+)\/-\/(issues|work_items)\/(\d+)$/);
    if (!m) return { repoName: "unknown-repo", itemNumber: "unknown" };
    const repoParts = m[1].split("/").filter(Boolean);
    let repoName = repoParts[repoParts.length - 1] || "unknown-repo";
    if (repoName === "gitlab-profile" && repoParts.length >= 2) {
      repoName = repoParts[repoParts.length - 2];
    }
    return { repoName, itemNumber: m[3] };
  } catch {
    return { repoName: "unknown-repo", itemNumber: "unknown" };
  }
}

function sanitizeFilenamePart(value) {
  return (value || "unknown")
    .trim()
    .replace(/[\/]/g, "-")
    .replace(/[^\w.-]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^[-._]+|[-._]+$/g, "") || "unknown";
}

function buildDownloadFilename(url, modelName, ext) {
  const parts = parseGitlabUrlParts(url || "");
  const date = new Date();
  const dateStr = `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, "0")}${String(date.getDate()).padStart(2, "0")}`;
  return `${sanitizeFilenamePart(parts.repoName)}_${sanitizeFilenamePart(parts.itemNumber)}_${sanitizeFilenamePart(modelName)}_${dateStr}.${ext}`;
}

function downloadText(elId, filename) {
  const el = id(elId);
  const text = el.tagName === "TEXTAREA" ? el.value : (el.dataset.raw || el.textContent);
  const a = Object.assign(document.createElement("a"), {
    href: URL.createObjectURL(new Blob([text], { type: "text/plain;charset=utf-8" })),
    download: filename,
  });
  a.click();
}

function downloadLastResult() {
  const meta = S.lastResultMeta || {};
  const filename = buildDownloadFilename(meta.url, meta.modelName, "md");
  downloadText("last-result", filename);
}

function downloadLastExport() {
  const meta = S.lastExportMeta || S.lastResultMeta || {};
  const filename = buildDownloadFilename(meta.url, meta.modelName, "txt");
  downloadText("last-export", filename);
}

function shortUrl(url) {
  try { const u = new URL(url); return u.pathname.split("/").slice(-3).join("/"); }
  catch { return url.slice(0, 50); }
}

// ── Dashboard ─────────────────────────────────────────────────────────

// 依日期建立 Milestone 選單，並自動選取當前 Sprint
function buildMilestoneSelect(milestones) {
  const msSelect = id("dash-milestone");
  if (!msSelect) return;

  const today = new Date(); today.setHours(0, 0, 0, 0);
  const current = [], upcoming = [], past = [];
  let autoSelectTitle = null;

  milestones.forEach(m => {
    const sd = m.start_date ? new Date(m.start_date) : null;
    const ed = m.due_date   ? new Date(m.due_date)   : null;
    if (sd && ed) {
      sd.setHours(0,0,0,0); ed.setHours(23,59,59,999);
      if (today >= sd && today <= ed) current.push(m);
      else if (sd > today)            upcoming.push(m);
      else                            past.push(m);
    } else {
      past.push(m);
    }
  });

  // 預設載入的第一個選項為 "不限 Milestone"，所以不需要預先選定任何版號
  // autoSelectTitle = null; (保持為一開始宣告的 null 即可)

  // 排序
  const bySDDesc = (a, b) => (b.start_date || '') > (a.start_date || '') ? 1 : -1;
  const bySDasc  = (a, b) => (a.start_date || '') > (b.start_date || '') ? 1 : -1;
  current.sort(bySDDesc); upcoming.sort(bySDasc); past.sort(bySDDesc);

  const addOption = (parent, m) => {
    const o = document.createElement("option");
    const range = (m.start_date && m.due_date) ? ` (${m.start_date}~${m.due_date})` : '';
    o.value = m.title;
    o.textContent = m.title + range;
    parent.appendChild(o);
  };

  msSelect.innerHTML = '';
  const allOpt = document.createElement("option");
  allOpt.value = "all"; allOpt.textContent = "不限 Milestone";
  msSelect.appendChild(allOpt);

  if (current.length) {
    const g = document.createElement("optgroup");
    g.label = "⏳ 當前進行中";
    current.forEach(m => addOption(g, m));
    msSelect.appendChild(g);
  }
  if (upcoming.length) {
    const g = document.createElement("optgroup");
    g.label = "⏸️ 未來";
    upcoming.forEach(m => addOption(g, m));
    msSelect.appendChild(g);
  }
  if (past.length) {
    const g = document.createElement("optgroup");
    g.label = "───── 過去 ─────";
    past.forEach(m => addOption(g, m));
    msSelect.appendChild(g);
  }

  if (autoSelectTitle) msSelect.value = autoSelectTitle;
}

async function doLoadDashboard(isMore = false) {
  const urlEl   = id("dash-repo-url");
  const repoUrl = urlEl ? urlEl.value.trim() : "";
  if (!repoUrl && !isMore) {
    showSt("dash-status", "error", "請填寫 Repo 網址或 Project ID");
    return;
  }

  if (!isMore) {
    S.dash = { issues: [], milestones: [], projectId: null, pageOffset: 1, hasMore: false, repoUrl, loading: false };
  }
  if (S.dash.loading) return;  // 防止重複並發
  S.dash.loading = true;

  const payload = {
    repo_url:      S.dash.repoUrl,
    project_id:    S.dash.projectId || S.projectId,
    private_token: S.token || (id("cfg-token") ? id("cfg-token").value.trim() : ""),
    target_count:  500,
    page_offset:   S.dash.pageOffset
  };

  const loadBtn = document.querySelector('#view-dashboard .btn-primary');
  if (!isMore && loadBtn) { loadBtn.disabled = true; loadBtn.textContent = "載入中..."; }

  if (!isMore) {
    id("dash-content").style.display = "none";
    showSt("dash-status", "info", "正在向 GitLab API 抓取資料...");
  } else {
    showSt("dash-status", "info", `背景載入中（目前 ${S.dash.issues.length} 筆）...`);
  }

  try {
    const res = await api("/api/dashboard/data", payload);
    if (res.error) throw new Error(res.error);

    S.dash.projectId = res.project_id;
    S.dash.issues    = S.dash.issues.concat(res.issues || []);

    // 合併 milestone map（後端 + issues 本身兩層）
    const msMap = {};
    S.dash.milestones.forEach(m => { if (m?.title) msMap[m.title] = m; });
    (res.milestones || []).forEach(m => { if (m?.title && !msMap[m.title]) msMap[m.title] = m; });
    S.dash.issues.forEach(i => {
      const ms = i.milestone;
      if (ms?.title && !msMap[ms.title]) msMap[ms.title] = ms;
    });
    S.dash.milestones = Object.values(msMap).sort((a, b) => (b.id || 0) - (a.id || 0));

    S.dash.hasMore   = res.has_more;
    S.dash.pageOffset = res.next_page_offset;

    id("dash-content").style.display = "flex";
    id("dash-status").className = "status hidden";

    // 重建 milestone 選單（保留目前選擇）
    const prevMs = id("dash-milestone").value;
    buildMilestoneSelect(S.dash.milestones);
    if (isMore && prevMs && [...id("dash-milestone").options].some(o => o.value === prevMs)) {
      id("dash-milestone").value = prevMs;
    }

    renderDashboardStats();

    // 自動背景連載：若本次回傳滿 500 筆則繼續
    if (res.has_more && res.next_page_offset > 0) {
      id("dash-footer-status").textContent = `已載入 ${S.dash.issues.length} 筆，背景繼續載入...`;
      id("btn-dash-load-more").style.display = "none";
      S.dash.loading = false;
      setTimeout(() => doLoadDashboard(true), 300);
      return;
    }

    id("dash-footer-status").textContent = `全部載入完成，共 ${S.dash.issues.length} 筆`;
    id("btn-dash-load-more").style.display = "none";

  } catch(e) {
    showSt("dash-status", "error", `載入${isMore ? '更多' : ''}失敗：${e.message}`);
  } finally {
    S.dash.loading = false;
    if (!isMore && loadBtn) { loadBtn.disabled = false; loadBtn.textContent = "載入資料"; }
  }
}

function loadDashboard() { doLoadDashboard(false); }
function loadMoreDashboard() { doLoadDashboard(true); }


// Chart.js instance
let _dashChart = null;

function renderDashboardStats() {
  const msSel = id("dash-milestone");
  const milestone = msSel ? msSel.value : "all";

  let validIssues = S.dash.issues || [];

  // Milestone 篩選（最優先）
  if (milestone !== "all") {
    validIssues = validIssues.filter(i => {
      const ms = i.milestone;
      const title = ms && typeof ms === 'object' ? ms.title : ms;
      return title === milestone;
    });
  }

  // ─ 總數
  const total  = validIssues.length;
  const opened = validIssues.filter(i => i.state === "opened").length;
  const closed = validIssues.filter(i => i.state === "closed").length;

  // ─ 動態判定本週期 (依據 Milestone)
  let msStart = null, msEnd = null;
  const dsCardTitle = document.getElementById("dash-val-week-label");
  if (milestone !== "all" && S.dash.milestones) {
    const msObj = S.dash.milestones.find(m => (typeof m === 'object' ? m.title : m) === milestone);
    if (msObj && typeof msObj === 'object') {
      if (msObj.start_date) msStart = new Date(msObj.start_date);
    }
  }

  let weekNew = 0, weekClosed = 0;
  // 如果有選擇 Milestone 且有 startDate，統計區間為該版本起迄；否則預設為最近 7 天
  const now = new Date();
  const weekAgo = msStart || new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
  
  if (dsCardTitle) {
      dsCardTitle.textContent = msStart ? "版版本期動態" : "本週動態 (最近 7 天)";
  }

  validIssues.forEach(i => {
    if (i.created_at && new Date(i.created_at) >= weekAgo) weekNew++;
    if (i.closed_at  && new Date(i.closed_at)  >= weekAgo) weekClosed++;
  });

  const setEl = (elId, v) => { const el = id(elId); if (el) el.textContent = v; };
  setEl("dash-val-total",       total);
  setEl("dash-val-opened",      opened);
  setEl("dash-val-closed",      closed);
  setEl("dash-val-week-new",    weekNew);
  setEl("dash-val-week-closed", weekClosed);

  const bMore = id("btn-dash-load-more");
  if (bMore) bMore.style.display = S.dash.hasMore ? "inline-block" : "none";
  setEl("dash-footer-status", `目前已載入 ${S.dash.issues.length} 筆資料`);

  // ─ 折線圖
  renderSprintChart(validIssues, milestone);
}


function renderSprintChart(issues, milestoneTitle) {
  const chartWrap = id("dash-chart-wrap");
  const canvas    = id("dash-chart");
  if (!chartWrap || !canvas || typeof Chart === "undefined") return;

  // ── 取得 Milestone 日期與判斷 X 軸週期 ──────────────────────────────────
  let startDate = null, endDate = null, chartLabel = "Issue 14日趨勢";
  // useWeekly: true=週 / false=日
  let useWeekly = false;

  if (milestoneTitle !== "all" && S.dash.milestones) {
    const msObj = S.dash.milestones.find(m =>
      (typeof m === 'object' ? m.title : m) === milestoneTitle
    );
    if (msObj && typeof msObj === 'object') {
      if (msObj.start_date) startDate = new Date(msObj.start_date);
      if (msObj.due_date)   endDate   = new Date(msObj.due_date);
      chartLabel = `趨勢 [${milestoneTitle}]`;
    }
    // 判斷週期：Sprint 開頭=日，版本號（含 AISVision、v數字 或其他非Sprint）=週
    useWeekly = !/^APT Sprint/i.test(milestoneTitle);
  }

  // 未選 milestone → 最近 14 日 / 日週期
  if (!startDate) {
    endDate   = new Date();
    startDate = new Date(endDate.getTime() - 13 * 24 * 60 * 60 * 1000);
    chartLabel = "Issue 14日趨勢";
    useWeekly = false;
  }
  if (!endDate) endDate = new Date();

  // ── 建立 X 軸刻度 ─────────────────────────────────────────────────────
  // 日模式：每天一個點；週模式：每週一個點（週一）
  const labels = [], buckets = [];  // buckets: [{start, end, label}]

  if (!useWeekly) {
    // 日模式
    const cur = new Date(startDate);
    while (cur <= endDate) {
      const key = cur.toISOString().slice(0, 10);
      labels.push(key.slice(5));   // MM-DD
      buckets.push({ key, start: key, end: key });
      cur.setDate(cur.getDate() + 1);
    }
  } else {
    // 週模式：每7天一個刻度，以 start_date 為基準
    const cur = new Date(startDate);
    while (cur <= endDate) {
      const weekStart = cur.toISOString().slice(0, 10);
      const next = new Date(cur);
      next.setDate(next.getDate() + 6);
      const weekEnd = (next <= endDate ? next : endDate).toISOString().slice(0, 10);
      labels.push(`W:${weekStart.slice(5)}`);
      buckets.push({ key: weekStart, start: weekStart, end: weekEnd });
      cur.setDate(cur.getDate() + 7);
    }
  }

  if (labels.length === 0) { chartWrap.style.display = "none"; return; }

  // ── 計算每個刻度的 opened / closed 筆數 ────────────────────────────────
  const openData  = new Array(buckets.length).fill(0);
  const closeData = new Array(buckets.length).fill(0);

  issues.forEach(i => {
    const created  = i.created_at ? i.created_at.slice(0, 10) : null;
    const closed_d = i.closed_at  ? i.closed_at.slice(0, 10)  : null;
    buckets.forEach((b, idx) => {
      if (created  && created  >= b.start && created  <= b.end) openData[idx]++;
      if (closed_d && closed_d >= b.start && closed_d <= b.end) closeData[idx]++;
    });
  });

  // ── 主題色 ─────────────────────────────────────────────────────────────
  const isDark    = document.documentElement.dataset.theme !== "light";
  const gridColor = isDark ? "rgba(255,255,255,0.07)" : "rgba(0,0,0,0.06)";
  const textColor = isDark ? "rgba(255,255,255,0.5)"  : "rgba(0,0,0,0.5)";

  // ── 重建 Chart（折線圖）────────────────────────────────────────────────
  if (_dashChart) { _dashChart.destroy(); _dashChart = null; }
  _dashChart = new Chart(canvas, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "新建立",
          data: openData,
          borderColor: "rgba(91,182,255,0.9)",
          backgroundColor: "rgba(91,182,255,0.15)",
          pointBackgroundColor: "rgba(91,182,255,1)",
          borderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
          tension: 0.35,
          fill: true,
        },
        {
          label: "已關閉",
          data: closeData,
          borderColor: "rgba(61,214,140,0.9)",
          backgroundColor: "rgba(61,214,140,0.1)",
          pointBackgroundColor: "rgba(61,214,140,1)",
          borderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
          tension: 0.35,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { labels: { color: textColor, font: { family: "IBM Plex Mono", size: 11 } } },
        tooltip: { mode: "index" },
      },
      scales: {
        x: {
          ticks: { color: textColor, font: { family: "IBM Plex Mono", size: 10 }, maxRotation: 45 },
          grid:  { color: gridColor },
        },
        y: {
          beginAtZero: true,
          ticks: { color: textColor, font: { family: "IBM Plex Mono", size: 10 }, precision: 0 },
          grid:  { color: gridColor },
        },
      },
    },
  });

  id("dash-chart-label").textContent = `${chartLabel}（X軸：${useWeekly ? '週' : '日'}）`;
  id("dash-chart-range").textContent = `${startDate.toISOString().slice(0,10)} → ${endDate.toISOString().slice(0,10)}`;
  chartWrap.style.display = "flex";
}

