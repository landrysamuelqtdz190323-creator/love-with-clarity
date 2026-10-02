"use strict";

const search = document.querySelector("#scenario-search");
const scenes = [...document.querySelectorAll(".scene")];
const filterButtons = [...document.querySelectorAll(".filter")];
let selectedCategory = "全部";

function applyFilters() {
  const words = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  let count = 0;
  for (const scene of scenes) {
    const categoryMatches = selectedCategory === "全部" || scene.dataset.category === selectedCategory;
    const wordsMatch = words.every(word => scene.dataset.search.toLocaleLowerCase().includes(word));
    scene.hidden = !(categoryMatches && wordsMatch);
    if (!scene.hidden) count++;
  }
  document.querySelector("#result-count").textContent = `找到 ${count} 个场景`;
  document.querySelector("#empty-results").hidden = count > 0;
  for (const button of filterButtons) button.setAttribute("aria-pressed", String(button.dataset.category === selectedCategory));
}

if (search) {
  search.addEventListener("input", applyFilters);
  for (const button of filterButtons) button.addEventListener("click", () => {
    selectedCategory = button.dataset.category;
    applyFilters();
  });
  document.querySelector("#reset-filters").addEventListener("click", () => {
    search.value = "";
    selectedCategory = "全部";
    applyFilters();
  });
  function revealLinkedScene() {
    const id = window.location.hash.slice(1);
    const target = document.getElementById(id);
    if (target && target.classList.contains("scene")) {
      search.value = "";
      selectedCategory = "全部";
      applyFilters();
      target.open = true;
      target.scrollIntoView({block: "start"});
    }
  }
  window.addEventListener("hashchange", revealLinkedScene);
  applyFilters();
  revealLinkedScene();
}

const tabs = [...document.querySelectorAll(".tab")];
const panels = [...document.querySelectorAll(".practice-panel")];
function selectExercise(id, focus = false) {
  for (const tab of tabs) {
    const selected = tab.dataset.panel === id;
    tab.setAttribute("aria-selected", String(selected));
    tab.tabIndex = selected ? 0 : -1;
    if (selected && focus) tab.focus();
  }
  for (const panel of panels) panel.hidden = panel.id !== id;
}
for (const [index, tab] of tabs.entries()) {
  tab.addEventListener("click", () => selectExercise(tab.dataset.panel));
  tab.addEventListener("keydown", event => {
    if (!["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const next = event.key === "Home" ? 0 : event.key === "End" ? tabs.length - 1 : (index + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
    selectExercise(tabs[next].dataset.panel, true);
  });
}

function openExerciseFromHash() {
  const target = window.location.hash.slice(1);
  if (panels.some(panel => panel.id === target)) selectExercise(target);
}
window.addEventListener("hashchange", openExerciseFromHash);
openExerciseFromHash();

function buildReport(form) {
  const fields = [...form.querySelectorAll("textarea[data-label]")];
  if (!fields.some(field => field.value.trim())) return "";
  const parts = fields.map(field => `## ${field.dataset.label}\n\n${field.value.trim() || "（尚未填写）"}`);
  return `# ${form.dataset.title}\n\n${parts.join("\n\n")}\n\n---\n由填写者自行整理，未经过 AI 分析。包含个人资料时请谨慎分享。\n练习来自《看清关系，也照顾自己》v1.0.0，CC BY 4.0。\n`;
}

for (const form of document.querySelectorAll("form[data-exercise]")) {
  form.addEventListener("submit", event => event.preventDefault());
  const panel = form.closest(".practice-panel");
  const status = panel.querySelector(".status");
  const preview = panel.querySelector(".preview");
  const output = preview.querySelector("textarea");
  function getReport() {
    const report = buildReport(form);
    if (!report) {
      status.textContent = "先填写至少一项，再生成整理稿。";
      return "";
    }
    output.value = report;
    preview.hidden = false;
    return report;
  }
  form.querySelector("[data-action=preview]").addEventListener("click", () => {
    if (getReport()) status.textContent = "整理稿已显示在下方；你可以继续修改填写。";
  });
  form.querySelector("[data-action=copy]").addEventListener("click", async () => {
    const report = getReport();
    if (!report) return;
    try {
      await navigator.clipboard.writeText(report);
      status.textContent = "已复制。请留意剪贴板与接收位置的隐私。";
    } catch (_) {
      output.focus();
      output.select();
      status.textContent = "浏览器未允许自动复制；整理稿已选中，可手动复制或下载。";
    }
  });
  form.querySelector("[data-action=download]").addEventListener("click", () => {
    const report = getReport();
    if (!report) return;
    const url = URL.createObjectURL(new Blob([report], {type: "text/markdown;charset=utf-8"}));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `love-with-clarity-${form.dataset.exercise}.md`;
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    status.textContent = "已发起下载；若浏览器没有保存，请使用复制。";
  });
  form.querySelector("[data-action=clear]").addEventListener("click", () => {
    form.reset();
    output.value = "";
    preview.hidden = true;
    status.textContent = "已清空这份练习。已导出文件与剪贴板需另行管理。";
  });
}
document.querySelector("#clear-all")?.addEventListener("click", () => {
  for (const form of document.querySelectorAll("form[data-exercise]")) form.reset();
  for (const panel of panels) {
    panel.querySelector(".preview textarea").value = "";
    panel.querySelector(".preview").hidden = true;
    panel.querySelector(".status").textContent = "已清空页面中的全部练习。";
  }
});
