const chatbotLog = document.getElementById("chatbot-log");
const agentLog = document.getElementById("agent-log");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const providerSel = document.getElementById("provider");
const resetBtn = document.getElementById("reset-btn");
const refreshStateBtn = document.getElementById("refresh-state-btn");
const stateView = document.getElementById("state-view");

function esc(s) {
  return String(s ?? "").replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
}

function appendMsg(pane, role, html) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.innerHTML = `<div class="role">${role}</div>${html}`;
  pane.appendChild(div);
  pane.scrollTop = pane.scrollHeight;
  return div;
}

function pendingMsg(pane, role) {
  return appendMsg(pane, role, `<span class="spinner"></span>thinking…`);
}

function renderTrace(trace) {
  if (!Array.isArray(trace) || trace.length === 0) return "";
  return trace.map(s => {
    if (s.final_answer !== undefined) {
      return `<div class="step final">
        ${s.thought ? `<div class="label">Thought</div><pre>${esc(s.thought)}</pre>` : ""}
        <div class="label">Final Answer</div><pre>${esc(s.final_answer)}</pre>
      </div>`;
    }
    const actionStr = s.action ? JSON.stringify(s.action) : "(parse error)";
    return `<div class="step">
      ${s.thought ? `<div class="label">Thought</div><pre>${esc(s.thought)}</pre>` : ""}
      <div class="label action">Action</div><pre>${esc(actionStr)}</pre>
      <div class="label obs">Observation</div><pre>${esc(s.observation || "")}</pre>
    </div>`;
  }).join("");
}

function metricsChips(m) {
  if (!m) return "";
  const statusCls = m.status === "success" ? "ok" : "fail";
  return `
    <div style="margin-bottom:0.4rem">
      <span class="metrics-chip ${statusCls}">${m.status}</span>
      <span class="metrics-chip">steps: ${m.steps}</span>
      <span class="metrics-chip">tokens: ${m.total_tokens ?? 0}</span>
    </div>`;
}

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  return res.json();
}

async function refreshState() {
  const s = await fetch("/api/state").then(r => r.json());
  stateView.textContent = JSON.stringify(s, null, 2);
}

async function send() {
  const message = userInput.value.trim();
  if (!message) return;
  userInput.value = "";
  sendBtn.disabled = true;

  appendMsg(chatbotLog, "user", `<pre>${esc(message)}</pre>`);
  appendMsg(agentLog, "user", `<pre>${esc(message)}</pre>`);

  const chatPending = pendingMsg(chatbotLog, "bot");
  const agentPending = pendingMsg(agentLog, "agent");

  const [chatRes, agentRes] = await Promise.all([
    postJSON("/api/chat", { message }).catch(e => ({ error: String(e) })),
    postJSON("/api/agent", { message }).catch(e => ({ error: String(e) })),
  ]);

  chatPending.innerHTML = `<div class="role">bot</div><pre>${esc(chatRes.response ?? chatRes.error)}</pre>`;
  agentPending.innerHTML = `<div class="role">agent</div>
    ${metricsChips(agentRes.metrics)}
    ${renderTrace(agentRes.trace)}
    <pre><strong>Answer:</strong> ${esc(agentRes.response ?? agentRes.error)}</pre>`;

  sendBtn.disabled = false;
  refreshState();
}

sendBtn.addEventListener("click", send);
userInput.addEventListener("keydown", e => {
  if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) send();
});

providerSel.addEventListener("change", async () => {
  const res = await postJSON("/api/provider", { provider: providerSel.value });
  if (res.error) {
    alert("Provider switch failed: " + res.error);
    providerSel.value = "mock";
  }
});

resetBtn.addEventListener("click", async () => {
  await postJSON("/api/reset");
  chatbotLog.innerHTML = "";
  agentLog.innerHTML = "";
  refreshState();
});

refreshStateBtn.addEventListener("click", refreshState);

refreshState();
