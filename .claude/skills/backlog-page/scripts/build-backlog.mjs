// Gera <pasta deste script>/backlog.html a partir de docs/TASKS.md.
// O TASKS.md é a fonte da verdade; esta página é só uma visualização.
// Uso (na raiz do projeto): node backlog-page/build-backlog.mjs [--name "Nome"] [--source docs/TASKS.md] [--out backlog-page/backlog.html]
// Sem argumentos: lê ../docs/TASKS.md relativo ao script e usa o nome da pasta do projeto.

import { readFileSync, writeFileSync } from "node:fs";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(here, "..");

const arg = (flag) => {
  const i = process.argv.indexOf(flag);
  return i > -1 ? process.argv[i + 1] : undefined;
};

const sourcePath = arg("--source") ? resolve(arg("--source")) : join(projectRoot, "docs", "TASKS.md");
const outputPath = arg("--out") ? resolve(arg("--out")) : join(here, "backlog.html");
const projectName =
  arg("--name") ??
  basename(resolve(projectRoot))
    .split(/[-_\s]+/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");

const STATUS = {
  "⬜": { key: "todo", label: "Não iniciada" },
  "🔄": { key: "doing", label: "Em andamento" },
  "✅": { key: "done", label: "Concluída" },
};

const escapeHtml = (text) =>
  text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

const inline = (text) =>
  escapeHtml(text)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, href) =>
      /^https?:/.test(href) ? `<a href="${href}">${label}</a>` : `<span class="ref">${label}</span>`);

function parse(markdown) {
  const doc = { title: "", intro: [], sections: [] };
  let section = null;

  for (const raw of markdown.split(/\r?\n/)) {
    const line = raw.trimEnd();
    if (!line.trim()) continue;

    if (line.startsWith("# ")) { doc.title = line.slice(2).trim(); continue; }

    if (line.startsWith("## ")) {
      let heading = line.slice(3).trim();
      const emoji = Object.keys(STATUS).find((e) => heading.startsWith(e));
      if (emoji) heading = heading.slice(emoji.length).trim();
      section = { heading, status: emoji ? STATUS[emoji] : null, tasks: [], bullets: [], notes: [] };
      doc.sections.push(section);
      continue;
    }

    const task = line.match(/^\s*- \[( |x|X)\] (.*)$/);
    if (task && section) { section.tasks.push({ done: task[1] !== " ", text: task[2] }); continue; }

    const bullet = line.match(/^\s*- (.*)$/);
    if (bullet && section) { section.bullets.push(bullet[1]); continue; }

    (section ? section.notes : doc.intro).push(line.trim());
  }
  return doc;
}

function renderTaskList(tasks) {
  return `<ul class="tasks">${tasks
    .map((t) => `<li class="${t.done ? "is-done" : ""}"><span class="box" aria-hidden="true">${t.done ? "✓" : ""}</span><span>${inline(t.text)}</span><span class="sr">${t.done ? "(concluída)" : "(pendente)"}</span></li>`)
    .join("")}</ul>`;
}

function renderNotes(notes) {
  return notes.map((n) => `<p class="${n.startsWith("**Aceite:**") ? "accept" : "note"}">${inline(n)}</p>`).join("");
}

function renderPhase(section) {
  const total = section.tasks.length;
  const done = section.tasks.filter((t) => t.done).length;
  const pct = total ? Math.round((done / total) * 100) : 0;
  const status = section.status;
  return `
  <article class="phase st-${status.key}">
    <header>
      <h3>${inline(section.heading)}</h3>
      <span class="pill pill-${status.key}">${status.label}</span>
    </header>
    <div class="progress" role="img" aria-label="${done} de ${total} tarefas concluídas">
      <div class="bar"><span style="width:${pct}%"></span></div>
      <span class="count">${done}/${total}</span>
    </div>
    ${total ? renderTaskList(section.tasks) : ""}
    ${section.bullets.length ? `<ul class="plain">${section.bullets.map((b) => `<li>${inline(b)}</li>`).join("")}</ul>` : ""}
    ${renderNotes(section.notes)}
  </article>`;
}

function renderSideSection(section, cls) {
  return `
  <section class="side ${cls}">
    <h2>${inline(section.heading)}</h2>
    ${section.tasks.length ? renderTaskList(section.tasks) : ""}
    ${section.bullets.length ? `<ul class="plain">${section.bullets.map((b) => `<li>${inline(b)}</li>`).join("")}</ul>` : ""}
    ${renderNotes(section.notes)}
  </section>`;
}

function render(doc) {
  const phases = doc.sections.filter((s) => s.status);
  const others = doc.sections.filter((s) => !s.status);
  const doneSection = others.find((s) => /conclu/i.test(s.heading));
  const decisions = others.find((s) => /decis/i.test(s.heading));
  const stateSection = others.find((s) => /estado atual/i.test(s.heading));
  const rest = others.filter((s) => s !== doneSection && s !== decisions && s !== stateSection);

  const allTasks = phases.flatMap((p) => p.tasks);
  const doneTasks = allTasks.filter((t) => t.done).length;
  const phasesDone = phases.filter((p) => p.status.key === "done").length;
  const current = phases.find((p) => p.status.key === "doing") ?? phases.find((p) => p.status.key === "todo");
  const openDecisions = decisions ? decisions.tasks.filter((t) => !t.done).length : 0;
  const generatedAt = new Date().toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });

  return `<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Backlog ${escapeHtml(projectName)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..100,500..800&family=Public+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* Layout: painel de backlog — resumo no topo, coluna lateral com estado atual, decisões e concluídos, fases em lista à direita. */
:root {
  --bg: #f6f7f8; --surface: #ffffff; --fg: #16202a; --muted: #586572; --line: #d9dee3;
  --accent: #0d6b6e; --accent-soft: #e2f0f0; --warn: #8a6d00; --warn-soft: #fbf5dc;
  --ok: #1f7a3a; --ok-soft: #e4f3e8; --code-bg: #eef1f4;
  --font-display: "Archivo", "Arial Narrow", system-ui, sans-serif;
  --font-body: "Public Sans", system-ui, "Segoe UI", sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, Consolas, monospace;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0f1418; --surface: #161d23; --fg: #e3e8ec; --muted: #98a5b1; --line: #2a343d;
    --accent: #4fc1c3; --accent-soft: #143032; --warn: #e6c24a; --warn-soft: #332b10;
    --ok: #6fd18c; --ok-soft: #15301e; --code-bg: #1d262e;
    color-scheme: dark;
  }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--fg); font-family: var(--font-body); font-size: 15px; line-height: 1.55; }
.wrap { max-width: 1180px; margin: 0 auto; padding: 36px max(16px, env(safe-area-inset-left, 0px)) 64px; }
.eyebrow { font-family: var(--font-display); font-weight: 700; text-transform: uppercase; letter-spacing: .1em; font-size: 12px; color: var(--accent); margin: 0 0 6px; }
h1 { font-family: var(--font-display); font-stretch: 85%; font-weight: 800; font-size: clamp(28px, 4.5vw, 42px); line-height: 1.05; margin: 0 0 8px; }
.sub { color: var(--muted); margin: 0; font-size: 13.5px; }
code { font-family: var(--font-mono); font-size: .85em; background: var(--code-bg); padding: 1px 5px; border-radius: 4px; overflow-wrap: anywhere; }
.ref { color: var(--accent); font-weight: 600; }
a { color: var(--accent); }

.summary { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: 24px 0 28px; }
@media (max-width: 760px) { .summary { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.stat { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 14px 16px; }
.stat b { display: block; font-family: var(--font-display); font-size: 26px; font-weight: 800; line-height: 1.1; font-variant-numeric: tabular-nums; }
.stat span { font-size: 13px; color: var(--muted); }
.stat.warn b { color: var(--warn); }

.grid { display: grid; grid-template-columns: 320px minmax(0, 1fr); gap: 28px; align-items: start; }
@media (max-width: 900px) { .grid { grid-template-columns: minmax(0, 1fr); } }
aside { display: grid; gap: 16px; }
.side { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 16px; }
.side.decisions { border: 1px dashed var(--warn); background: var(--warn-soft); }
.side.state { border-left: 4px solid var(--accent); background: var(--accent-soft); }
.side h2 { font-family: var(--font-display); font-size: 16px; font-weight: 800; margin: 0 0 8px; }
.phases { display: grid; gap: 12px; min-width: 0; }
.phases > h2 { font-family: var(--font-display); font-size: 16px; font-weight: 800; margin: 0; }

.phase { background: var(--surface); border: 1px solid var(--line); border-left: 4px solid var(--line); border-radius: 8px; padding: 14px 16px; }
.phase.st-doing { border-left-color: var(--accent); }
.phase.st-done { border-left-color: var(--ok); }
.phase header { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; justify-content: space-between; }
.phase h3 { margin: 0; font-family: var(--font-display); font-size: 17px; font-weight: 700; }
.pill { font-size: 11.5px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; padding: 2px 9px; border-radius: 999px; white-space: nowrap; }
.pill-todo { background: var(--code-bg); color: var(--muted); }
.pill-doing { background: var(--accent-soft); color: var(--accent); }
.pill-done { background: var(--ok-soft); color: var(--ok); }
.progress { display: flex; align-items: center; gap: 10px; margin: 10px 0 6px; }
.bar { flex: 1; height: 6px; border-radius: 999px; background: var(--code-bg); overflow: hidden; }
.bar span { display: block; height: 100%; background: var(--accent); }
.st-done .bar span { background: var(--ok); }
.count { font-family: var(--font-mono); font-size: 12px; color: var(--muted); font-variant-numeric: tabular-nums; }

ul.tasks, ul.plain { margin: 6px 0; padding: 0; list-style: none; display: grid; gap: 5px; }
ul.plain { list-style: disc; padding-left: 20px; }
ul.tasks li { display: flex; gap: 9px; align-items: flex-start; font-size: 14.5px; }
.box { flex: none; width: 16px; height: 16px; margin-top: 3px; border: 1.5px solid var(--muted); border-radius: 4px; display: grid; place-items: center; font-size: 11px; font-weight: 700; color: var(--surface); }
li.is-done .box { background: var(--ok); border-color: var(--ok); }
li.is-done > span:nth-child(2) { color: var(--muted); text-decoration: line-through; text-decoration-color: var(--line); }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
p.accept { margin: 10px 0 0; padding: 8px 12px; border-radius: 6px; background: var(--accent-soft); font-size: 13.5px; }
p.note { margin: 6px 0; font-size: 14px; color: var(--muted); }
footer { margin-top: 36px; font-size: 12.5px; color: var(--muted); }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <p class="eyebrow">${escapeHtml(projectName)} · acompanhamento</p>
    <h1>${inline(doc.title || "Tarefas")}</h1>
    <p class="sub">Gerado a partir de <code>docs/TASKS.md</code> em ${generatedAt}. Para atualizar, edite o TASKS.md e rode <code>node backlog-page/build-backlog.mjs</code>.</p>
  </header>

  <div class="summary">
    <div class="stat"><b>${doneTasks}/${allTasks.length}</b><span>tarefas das fases concluídas</span></div>
    <div class="stat"><b>${phasesDone}/${phases.length}</b><span>fases concluídas</span></div>
    <div class="stat"><b>${current ? inline(current.heading.split(":")[0]) : "—"}</b><span>${current ? inline(current.heading.split(":").slice(1).join(":").trim() || "próxima fase") : "todas concluídas"}</span></div>
    <div class="stat ${openDecisions ? "warn" : ""}"><b>${openDecisions}</b><span>decisões pendentes</span></div>
  </div>

  <div class="grid">
    <aside>
      ${stateSection ? renderSideSection(stateSection, "state") : ""}
      ${decisions ? renderSideSection(decisions, "decisions") : ""}
      ${doneSection ? renderSideSection(doneSection, "done") : ""}
      ${rest.map((s) => renderSideSection(s, "")).join("")}
    </aside>
    <main class="phases">
      <h2>Fases</h2>
      ${phases.map(renderPhase).join("")}
    </main>
  </div>

  <footer>${doc.intro.map(inline).join(" ")}</footer>
</div>
</body>
</html>
`;
}

writeFileSync(outputPath, render(parse(readFileSync(sourcePath, "utf8"))), "utf8");
console.log(`Backlog gerado em ${outputPath}`);
