const $ = (id) => document.getElementById(id);
const chatbotLog = $("chatbot-log");
const agentLog = $("agent-log");
const userInput = $("user-input");
const sendBtn = $("send-btn");
const providerSel = $("provider");
const userSel = $("current-user");
const userTag = $("user-tag");
const userTagName = $("user-tag-name");
const resetBtn = $("reset-btn");
const ordersTbody = $("orders-tbody");
const ordersTotal = $("orders-total");
const toolResult = $("tool-result");

function esc(s) {
  return String(s ?? "").replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
}

function fmtPrice(n) {
  return (n || 0).toLocaleString("vi-VN") + "đ";
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
  return `<div>
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

function currentUserPrefix() {
  const u = userSel.value.trim();
  return u ? `[Người dùng: ${u}] ` : "";
}

function refreshUserTag() {
  const u = userSel.value.trim();
  if (u) {
    userTagName.textContent = u;
    userTag.classList.remove("hidden");
  } else {
    userTag.classList.add("hidden");
  }
}

async function refreshState() {
  const s = await fetch("/api/state").then(r => r.json());
  renderOrdersTable(s);
}

function renderOrdersTable(state) {
  const summary = state.summary || { orders: [], total: 0, count: 0 };
  const items = summary.orders || [];
  ordersTotal.textContent = `${items.length} món · ${fmtPrice(summary.total)}`;
  if (items.length === 0) {
    ordersTbody.innerHTML = `<tr class="empty"><td colspan="5">Chưa có đơn nào</td></tr>`;
    return;
  }
  ordersTbody.innerHTML = items.map(o => `
    <tr>
      <td><strong>${esc(o.user)}</strong></td>
      <td>${esc(o.item_name)}${o.note ? `<br><small style="color:var(--text-dim)">${esc(o.note)}</small>` : ""}</td>
      <td class="price">${fmtPrice(o.price)}</td>
      <td class="${o.paid ? "paid-yes" : "paid-no"}">${o.paid ? "✓" : "—"}</td>
      <td>${o.paid ? "" : `<button class="btn pay-btn" data-pay="${esc(o.user)}">Đã trả</button>`}</td>
    </tr>
  `).join("");
}

async function callTool(name, args, opts = {}) {
  if (opts.confirm && !confirm(opts.confirm)) return;
  toolResult.classList.remove("hidden");
  toolResult.innerHTML = `<span class="tool-name">${esc(name)}</span><br><span class="spinner"></span>running…`;
  const res = await postJSON(`/api/tool/${name}`, args || {});
  if (res.error) {
    toolResult.innerHTML = `<span class="tool-name">${esc(name)}</span><br><span style="color:var(--danger)">${esc(res.error)}</span>`;
  } else {
    toolResult.innerHTML = `<span class="tool-name">${esc(name)}</span>\n${esc(JSON.stringify(res.result, null, 2))}`;
  }
  refreshState();
}

async function send() {
  const raw = userInput.value.trim();
  if (!raw) return;
  const message = currentUserPrefix() + raw;
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
    <div class="answer-block"><strong>Answer:</strong> ${esc(agentRes.response ?? agentRes.error)}</div>`;

  sendBtn.disabled = false;
  refreshState();
}

/* ---------- Event wiring ---------- */
sendBtn.addEventListener("click", send);
userInput.addEventListener("keydown", e => {
  if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
    e.preventDefault();
    send();
  }
});

userSel.addEventListener("change", refreshUserTag);

providerSel.addEventListener("change", async () => {
  const res = await postJSON("/api/provider", { provider: providerSel.value });
  if (res.error) {
    alert("Provider switch failed: " + res.error);
    providerSel.value = "mock";
  }
});

resetBtn.addEventListener("click", async () => {
  if (!confirm("Reset toàn bộ đơn và lịch sử chat?")) return;
  await postJSON("/api/reset");
  chatbotLog.innerHTML = "";
  agentLog.innerHTML = "";
  toolResult.classList.add("hidden");
  refreshState();
});

// Quick-action buttons
document.querySelectorAll(".btn.quick").forEach(btn => {
  btn.addEventListener("click", () => {
    const tool = btn.dataset.tool;
    const confirmMsg = btn.dataset.confirm;
    callTool(tool, {}, { confirm: confirmMsg });
  });
});

// Mark-paid buttons (delegated)
ordersTbody.addEventListener("click", e => {
  const btn = e.target.closest("[data-pay]");
  if (!btn) return;
  callTool("mark_paid", { user: btn.dataset.pay });
});

// Collapsible sections
document.querySelectorAll("[data-toggle]").forEach(head => {
  head.addEventListener("click", () => {
    head.closest(".collapsible").classList.toggle("collapsed");
  });
});

refreshUserTag();
refreshState();
