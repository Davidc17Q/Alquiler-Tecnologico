/**
 * TechRent — Panel administrativo / vendedores
 */
const TechRentAdmin = (function () {
  const API = { v1: "/api/v1" };
  const state = {
    user: null,
    metrics: null,
    analytics: null,
    clientes: [],
    equipos: [],
    alquileres: [],
    alquilerFilter: "activos",
    charts: {},
  };

  const METRIC_DEFS = [
    { key: "total_usuarios", label: "Total usuarios", icon: "users", color: "cyan" },
    { key: "clientes_activos", label: "Clientes activos", icon: "user-check", color: "blue" },
    { key: "equipos_registrados", label: "Equipos registrados", icon: "laptop", color: "purple" },
    { key: "equipos_alquilados", label: "Equipos alquilados", icon: "package-check", color: "cyan" },
    { key: "ingresos_mensuales", label: "Ingresos mensuales", icon: "banknote", color: "emerald", money: true },
    { key: "alquileres_activos", label: "Alquileres activos", icon: "calendar-check", color: "purple" },
    { key: "pagos_pendientes", label: "Pagos pendientes", icon: "credit-card", color: "amber" },
    { key: "uso_sistema", label: "Uso del sistema", icon: "activity", color: "rose", suffix: "%" },
  ];

  function apiFetch(url, opts = {}) {
    return fetch(url, {
      ...opts,
      headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
      credentials: "include",
    });
  }

  async function parseJson(res) {
    try {
      return await res.json();
    } catch {
      return { detail: "Error de respuesta" };
    }
  }

  function toast(msg, type = "success") {
    if (typeof window.toast === "function") window.toast(msg, type);
  }

  function escapeHtml(t) {
    const d = document.createElement("div");
    d.textContent = t;
    return d.innerHTML;
  }

  function formatMoney(v) {
    return `$${Number(v || 0).toLocaleString("es-CO")}`;
  }

  function isStaff(user) {
    return user && (user.rol === "VENDOR" || user.rol === "ADMIN");
  }

  function drawSparkline(canvas, data, color = "#22d3ee") {
    if (!canvas || !data?.length) return;
    const ctx = canvas.getContext("2d");
    const w = canvas.width = canvas.offsetWidth * 2;
    const h = canvas.height = 72;
    ctx.clearRect(0, 0, w, h);
    const max = Math.max(...data, 1);
    const step = w / (data.length - 1 || 1);
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    data.forEach((v, i) => {
      const x = i * step;
      const y = h - (v / max) * (h - 8) - 4;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
    const g = ctx.createLinearGradient(0, 0, 0, h);
    g.addColorStop(0, color.replace(")", ", 0.25)").replace("rgb", "rgba").replace("#22d3ee", "rgba(34,211,238,0.25)"));
    g.addColorStop(1, "transparent");
  }

  function growthHtml(key, metrics) {
    if (key === "ingresos_mensuales" && metrics.ingresos_crecimiento != null) {
      const g = metrics.ingresos_crecimiento;
      const cls = g >= 0 ? "admin-growth-up" : "admin-growth-down";
      const sign = g >= 0 ? "+" : "";
      return `<span class="text-xs ${cls}">${sign}${g}%</span>`;
    }
    const spark = metrics.sparklines?.[key] || [];
    if (spark.length < 2) return `<span class="text-xs text-slate-500">—</span>`;
    const g = spark[spark.length - 1] - spark[0];
    const cls = g >= 0 ? "admin-growth-up" : "admin-growth-down";
    return `<span class="text-xs ${cls}">${g >= 0 ? "+" : ""}${g}</span>`;
  }

  function renderMetricCards(metrics) {
    const grid = document.getElementById("admin-metrics-grid");
    if (!grid) return;
    grid.innerHTML = METRIC_DEFS.map((def, i) => {
      let val = metrics[def.key] ?? 0;
      if (def.money) val = formatMoney(val);
      else if (def.suffix === "%") val = `${val}%`;
      else if (def.suffix) val = `${val}${def.suffix}`;
      else val = Number(val).toLocaleString("es-CO");

      return `
      <article class="admin-metric-card" style="animation-delay:${i * 40}ms">
        <div class="flex justify-between items-start mb-2">
          <div class="h-9 w-9 rounded-lg bg-${def.color}-500/15 flex items-center justify-center">
            <i data-lucide="${def.icon}" class="w-4 h-4 text-${def.color}-400"></i>
          </div>
          ${growthHtml(def.key, metrics)}
        </div>
        <p class="admin-metric-value text-white">${val}</p>
        <p class="text-xs text-slate-500 mt-1">${def.label}</p>
        <canvas class="admin-sparkline" data-spark="${def.key}" height="36"></canvas>
      </article>`;
    }).join("");

    grid.querySelectorAll("[data-spark]").forEach((c) => {
      const key = c.dataset.spark;
      drawSparkline(c, metrics.sparklines?.[key] || [0, 0, 0, 0, 0, 0, 0]);
    });
    if (typeof lucide !== "undefined") lucide.createIcons();
  }

  async function loadDashboard() {
    const grid = document.getElementById("admin-metrics-grid");
    if (grid) grid.innerHTML = '<div class="skeleton-admin h-32 col-span-full"></div>'.repeat(4);
    const res = await apiFetch(`${API.v1}/admin/dashboard/`);
    const data = await parseJson(res);
    if (!res.ok) {
      toast(data.detail || "Sin acceso admin", "error");
      return;
    }
    state.metrics = data;
    renderMetricCards(data);
  }

  function destroyCharts() {
    Object.values(state.charts).forEach((c) => c?.destroy?.());
    state.charts = {};
  }

  async function loadAnalytics() {
    const res = await apiFetch(`${API.v1}/admin/analytics/`);
    const data = await parseJson(res);
    if (!res.ok) return;
    state.analytics = data;
    if (typeof Chart === "undefined") return;
    destroyCharts();

    const gridColor = "rgba(148,163,184,0.15)";
    const fontColor = "#94a3b8";

    const ing = data.ingresos_por_mes || [];
    state.charts.ingresos = new Chart(document.getElementById("chart-ingresos"), {
      type: "line",
      data: {
        labels: ing.map((x) => x.mes),
        datasets: [{
          label: "Ingresos",
          data: ing.map((x) => x.total),
          borderColor: "#22d3ee",
          backgroundColor: "rgba(34,211,238,0.1)",
          fill: true,
          tension: 0.4,
        }],
      },
      options: { plugins: { legend: { display: false } }, scales: { x: { grid: { color: gridColor }, ticks: { color: fontColor } }, y: { grid: { color: gridColor }, ticks: { color: fontColor } } } },
    });

    const cats = data.alquileres_por_categoria || [];
    state.charts.cats = new Chart(document.getElementById("chart-categorias"), {
      type: "bar",
      data: {
        labels: cats.map((c) => c.categoria),
        datasets: [{ data: cats.map((c) => c.total), backgroundColor: "rgba(167,139,250,0.7)", borderRadius: 6 }],
      },
      options: { plugins: { legend: { display: false } }, scales: { x: { ticks: { color: fontColor, maxRotation: 45 } }, y: { ticks: { color: fontColor } } } },
    });

    const top = data.equipos_mas_alquilados || [];
    state.charts.top = new Chart(document.getElementById("chart-top-equipos"), {
      type: "bar",
      data: {
        labels: top.map((e) => e.nombre?.slice(0, 18)),
        datasets: [{ data: top.map((e) => e.total), backgroundColor: "rgba(52,211,153,0.65)", borderRadius: 6 }],
      },
      options: { indexAxis: "y", plugins: { legend: { display: false } } },
    });

    const act = data.actividad_usuarios || [];
    state.charts.act = new Chart(document.getElementById("chart-actividad"), {
      type: "line",
      data: {
        labels: act.map((x) => x.mes),
        datasets: [{ data: act.map((x) => x.usuarios), borderColor: "#a78bfa", tension: 0.35 }],
      },
      options: { plugins: { legend: { display: false } } },
    });

    const est = data.estados_sistema || {};
    state.charts.est = new Chart(document.getElementById("chart-estados"), {
      type: "doughnut",
      data: {
        labels: Object.keys(est),
        datasets: [{ data: Object.values(est), backgroundColor: ["#fbbf24", "#34d399", "#64748b"] }],
      },
    });
  }

  async function loadClientes() {
    const q = document.getElementById("admin-clientes-buscar")?.value || "";
    const list = document.getElementById("admin-clientes-list");
    if (list) list.innerHTML = '<div class="skeleton-admin h-16"></div>'.repeat(3);
    const res = await apiFetch(`${API.v1}/admin/clientes/?q=${encodeURIComponent(q)}`);
    const data = await parseJson(res);
    if (!res.ok) {
      const msg = data.detail || "No se pudo cargar la lista de clientes.";
      if (list) list.innerHTML = `<p class="text-red-400 text-sm">${escapeHtml(msg)}</p>`;
      toast(msg, "error");
      return;
    }
    if (!Array.isArray(data)) {
      if (list) list.innerHTML = '<p class="text-red-400 text-sm">Respuesta inválida del servidor.</p>';
      return;
    }
    state.clientes = data;
    if (!list) return;
    if (!data.length) {
      list.innerHTML = '<p class="text-slate-500 text-sm">Sin clientes.</p>';
      return;
    }
    list.innerHTML = data.map((c) => {
      const ini = (c.nombre || "?").split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase();
      const badge = c.activo
        ? '<span class="badge badge-online">Activo</span>'
        : '<span class="badge badge-offline">Bloqueado</span>';
      return `
      <div class="admin-client-row">
        <div class="h-11 w-11 rounded-full bg-gradient-to-br from-cyan-500/30 to-purple-600/40 flex items-center justify-center text-sm font-bold">${ini}</div>
        <div class="min-w-0">
          <p class="font-medium truncate">${escapeHtml(c.nombre)}</p>
          <p class="text-xs text-slate-500 truncate">${escapeHtml(c.email)}</p>
          <p class="text-[10px] text-slate-600 mt-0.5">${c.total_alquileres || 0} alquileres · último: ${c.ultimo_alquiler || "—"}</p>
        </div>
        ${badge}
        <div class="flex flex-wrap gap-1 justify-end">
          <button type="button" class="btn-ghost text-[10px] px-2 py-1" onclick="TechRentAdmin.toggleCliente(${c.id}, ${!c.activo})">${c.activo ? "Bloquear" : "Activar"}</button>
          <button type="button" class="btn-ghost text-[10px] px-2 py-1" onclick="TechRentAdmin.verDetalleCliente(${c.id})">Detalle</button>
        </div>
      </div>`;
    }).join("");
  }

  async function toggleCliente(id, activo) {
    const res = await apiFetch(`${API.v1}/admin/clientes/${id}/`, {
      method: "PATCH",
      body: JSON.stringify({ activo }),
    });
    if (res.ok) {
      toast(activo ? "Cliente activado" : "Cliente bloqueado");
      loadClientes();
    }
  }

  async function verDetalleCliente(id) {
    const res = await apiFetch(`${API.v1}/admin/clientes/${id}/`);
    const data = await parseJson(res);
    if (!res.ok) return;
    alert(
      `Alquileres: ${data.alquileres?.length || 0}\nPagos: ${data.pagos?.length || 0}\n(Revisa consola para JSON)`,
    );
    console.log("Cliente detalle", data);
  }

  async function loadEquipos() {
    const grid = document.getElementById("admin-equipos-grid");
    if (grid) grid.innerHTML = '<div class="skeleton-admin h-40"></div>'.repeat(4);
    const res = await apiFetch(`${API.v1}/admin/equipos/`);
    const data = await parseJson(res);
    if (!res.ok) return;
    state.equipos = data;
    const cats = [...new Set(data.map((e) => e.categoria))].sort();
    const filtros = document.getElementById("admin-equipos-filtros");
    if (filtros) {
      filtros.innerHTML = `<button type="button" class="category-pill active" data-eq-cat="all">Todos</button>${cats.map((c) => `<button type="button" class="category-pill" data-eq-cat="${escapeHtml(c)}">${escapeHtml(c)}</button>`).join("")}`;
      filtros.querySelectorAll("[data-eq-cat]").forEach((btn) => {
        btn.addEventListener("click", () => {
          filtros.querySelectorAll("[data-eq-cat]").forEach((b) => b.classList.toggle("active", b === btn));
          renderEquiposGrid(btn.dataset.eqCat);
        });
      });
    }
    renderEquiposGrid("all");
  }

  function renderEquiposGrid(cat) {
    const grid = document.getElementById("admin-equipos-grid");
    if (!grid) return;
    const items = cat === "all" ? state.equipos : state.equipos.filter((e) => e.categoria === cat);
    grid.innerHTML = items.map((e) => `
      <article class="admin-equipo-card" data-id="${e.id}">
        <div class="admin-equipo-thumb"><i data-lucide="laptop" class="w-8 h-8 text-cyan-400/60"></i></div>
        <div class="p-4 space-y-2">
          <div class="flex justify-between gap-2">
            <h4 class="font-semibold text-sm truncate">${escapeHtml(e.nombre)}</h4>
            <span class="badge ${e.estado === "DISPONIBLE" ? "badge-online" : "badge-pending"}">${e.estado}</span>
          </div>
          <p class="text-xs text-slate-500">${escapeHtml(e.categoria)} · ID #${e.id}</p>
          <p class="font-mono text-cyan-300">${formatMoney(e.precio_por_dia)}/día</p>
          <div class="flex flex-wrap gap-1 pt-2">
            <button type="button" class="btn-ghost text-[10px] px-2" onclick="TechRentAdmin.patchEquipo(${e.id},{estado:'DISPONIBLE'})">Disponible</button>
            <button type="button" class="btn-ghost text-[10px] px-2" onclick="TechRentAdmin.patchEquipo(${e.id},{estado:'MANTENIMIENTO'})">Mantenimiento</button>
            <button type="button" class="btn-ghost text-[10px] px-2 text-red-400" onclick="TechRentAdmin.deleteEquipo(${e.id})">Eliminar</button>
          </div>
        </div>
      </article>`).join("");
    if (typeof lucide !== "undefined") lucide.createIcons();
  }

  async function patchEquipo(id, body) {
    const res = await apiFetch(`${API.v1}/admin/equipos/${id}/`, { method: "PATCH", body: JSON.stringify(body) });
    if (res.ok) {
      toast("Equipo actualizado");
      loadEquipos();
    }
  }

  async function deleteEquipo(id) {
    if (!confirm("¿Eliminar equipo?")) return;
    const res = await apiFetch(`${API.v1}/admin/equipos/${id}/`, { method: "DELETE" });
    if (res.ok || res.status === 204) {
      toast("Equipo eliminado");
      loadEquipos();
    }
  }

  async function loadAlquileres() {
    const list = document.getElementById("admin-alquileres-list");
    if (list) list.innerHTML = '<div class="skeleton-admin h-24"></div>';
    const res = await apiFetch(`${API.v1}/admin/alquileres/`);
    const data = await parseJson(res);
    if (!res.ok) return;
    state.alquileres = data;
    renderAlquileres();
  }

  function renderAlquileres() {
    const list = document.getElementById("admin-alquileres-list");
    if (!list) return;
    const today = new Date().toISOString().slice(0, 10);
    let items = state.alquileres;
    if (state.alquilerFilter === "activos") {
      items = items.filter((a) => a.estado === "PAGADO" || (a.estado === "PENDIENTE" && a.fecha_fin >= today));
    } else if (state.alquilerFilter === "pendientes") {
      items = items.filter((a) => a.estado === "PENDIENTE");
    } else if (state.alquilerFilter === "vencidos") {
      items = items.filter((a) => a.fecha_fin < today && a.estado !== "FINALIZADO");
    } else if (state.alquilerFilter === "finalizados") {
      items = items.filter((a) => a.estado === "FINALIZADO");
    }

    list.innerHTML = `<div class="admin-timeline">${items.slice(0, 40).map((a) => `
      <div class="admin-timeline-item glass-card p-4">
        <div class="flex flex-wrap justify-between gap-2">
          <div>
            <p class="font-mono text-[10px] text-slate-500">#${a.id}</p>
            <p class="font-semibold">${escapeHtml(a.equipo_nombre)}</p>
            <p class="text-xs text-slate-500">${escapeHtml(a.usuario_nombre)} · ${a.fecha_inicio} → ${a.fecha_fin}</p>
          </div>
          <span class="badge badge-pending">${a.estado}</span>
        </div>
        <p class="text-cyan-300 font-mono text-sm mt-2">${formatMoney(a.costo_total)}</p>
      </div>`).join("")}</div>`;
  }

  async function loadInfra() {
    const grid = document.getElementById("admin-infra-grid");
    const res = await apiFetch(`${API.v1}/admin/infra/`);
    const data = await parseJson(res);
    if (!res.ok || !grid) return;
    grid.innerHTML = (data.servicios || []).map((s) => `
      <div class="infra-node ${s.estado === "ONLINE" ? "online infra-pulse" : "offline"}">
        <div class="flex justify-between items-start mb-3">
          <h4 class="font-semibold text-sm">${escapeHtml(s.nombre)}</h4>
          <span class="badge ${s.estado === "ONLINE" ? "badge-online" : "badge-offline"}">${s.estado}</span>
        </div>
        <p class="text-xs font-mono text-cyan-400">${s.latencia_ms}ms</p>
        <div class="mt-3 space-y-1 text-[10px] text-slate-500">
          <div class="flex justify-between"><span>CPU</span><span>${s.cpu_mock}%</span></div>
          ${s.metricas_simuladas ? '<p class="text-[9px] text-amber-400/80">CPU/RAM simuladas</p>' : ""}
          <div class="h-1.5 rounded-full bg-slate-800"><div class="h-full rounded-full bg-cyan-500/60" style="width:${s.cpu_pct || 0}%"></div></div>
          <div class="flex justify-between"><span>RAM</span><span>${s.memoria_pct || 0}%</span></div>
          <div class="h-1.5 rounded-full bg-slate-800"><div class="h-full rounded-full bg-purple-500/60" style="width:${s.memoria_pct || 0}%"></div></div>
        </div>
        <pre class="worker-log mt-3 text-[9px]">${(s.logs || []).join("\n")}</pre>
      </div>`).join("");
  }

  function navigate(section) {
    document.querySelectorAll("[data-admin-section]").forEach((l) => {
      l.classList.toggle("active", l.dataset.adminSection === section);
    });
    document.querySelectorAll(".admin-section").forEach((s) => {
      s.classList.toggle("active", s.id === `admin-section-${section.replace("admin-", "")}`);
    });
    const titles = {
      "admin-dashboard": "Dashboard",
      "admin-analytics": "Analytics",
      "admin-clientes": "Clientes",
      "admin-equipos": "Equipos",
      "admin-alquileres": "Alquileres",
      "admin-infra": "Microservicios",
    };
    const t = document.getElementById("admin-page-title");
    if (t) t.textContent = titles[section] || section;

    if (section === "admin-dashboard") loadDashboard();
    if (section === "admin-analytics") loadAnalytics();
    if (section === "admin-clientes") loadClientes();
    if (section === "admin-equipos") loadEquipos();
    if (section === "admin-alquileres") loadAlquileres();
    if (section === "admin-infra") loadInfra();

    document.getElementById("admin-sidebar")?.classList.remove("open");
    if (typeof lucide !== "undefined") lucide.createIcons();
  }

  function bindUI() {
    document.querySelectorAll("[data-admin-section]").forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        navigate(link.dataset.adminSection);
      });
    });

    document.getElementById("admin-clientes-buscar")?.addEventListener("input", () => {
      clearTimeout(bindUI._searchT);
      bindUI._searchT = setTimeout(loadClientes, 300);
    });

    document.querySelectorAll("[data-alq-filter]").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.alquilerFilter = btn.dataset.alqFilter;
        document.querySelectorAll("[data-alq-filter]").forEach((b) => b.classList.toggle("active", b === btn));
        renderAlquileres();
      });
    });

    document.getElementById("admin-btn-logout")?.addEventListener("click", async () => {
      await apiFetch(`${API.v1}/auth/logout/`, { method: "POST" });
      document.getElementById("admin-shell")?.classList.add("hidden");
      document.getElementById("auth-gate")?.classList.remove("hidden");
      toast("Sesión cerrada");
    });

    document.getElementById("admin-sidebar-collapse")?.addEventListener("click", () => {
      document.getElementById("admin-shell")?.classList.toggle("sidebar-collapsed");
    });

    document.getElementById("admin-mobile-menu")?.addEventListener("click", () => {
      document.getElementById("admin-sidebar")?.classList.toggle("open");
    });
  }

  function showAdminShell() {
    document.getElementById("auth-gate")?.classList.add("hidden");
    document.getElementById("app-shell")?.classList.add("hidden");
    document.getElementById("admin-shell")?.classList.remove("hidden");
  }

  function boot(user) {
    state.user = user;
    const name = document.getElementById("admin-user-name");
    const role = document.getElementById("admin-user-role");
    if (name) name.textContent = user.nombre;
    if (role) role.textContent = user.rol;
    showAdminShell();
    bindUI();
    navigate("admin-dashboard");
  }

  return {
    boot,
    isStaff,
    loadClientes,
    toggleCliente,
    verDetalleCliente,
    patchEquipo,
    deleteEquipo,
  };
})();

window.TechRentAdmin = TechRentAdmin;
