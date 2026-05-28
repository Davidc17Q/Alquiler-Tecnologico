/**
 * TechRent — Panel del cliente
 * Sesión Django + API REST (credentials: include).
 */

const API = {
  v1: "/api/v1",
  pagos: "/api/v2/pagos/",
  equiposFlask: "/api/equipos/disponibles",
};

const state = {
  user: null,
  resumen: null,
  equipos: [],
  misAlquileres: [],
  alquilerFilter: "activos",
  section: "dashboard",
};

function refreshIcons() {
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
}

// ─── HTTP con sesión ────────────────────────────────────────────────────────

async function apiFetch(url, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  return fetch(url, {
    ...options,
    headers,
    credentials: "include",
  });
}

async function parseJsonSafe(res) {
  const contentType = res.headers.get("Content-Type") || "";
  if (contentType.includes("application/json")) {
    try {
      return await res.json();
    } catch {
      return { detail: "Respuesta JSON inválida." };
    }
  }
  const text = await res.text();
  if (text.includes("Page not found") || text.includes("<!DOCTYPE html>")) {
    return { detail: "Ruta no encontrada en el servidor." };
  }
  return { detail: text.slice(0, 200) || "Respuesta no JSON." };
}

// ─── Utilidades ───────────────────────────────────────────────────────────

function toast(message, type = "success") {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = message;
  container.appendChild(el);
  setTimeout(() => {
    el.style.opacity = "0";
    el.style.transform = "translateX(100%)";
    setTimeout(() => el.remove(), 300);
  }, 4000);
}

function avatarInitials(name) {
  return (name || "?")
    .split(" ")
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

function statusBadge(estado) {
  const map = {
    DISPONIBLE: "badge-online",
    PENDIENTE: "badge-pending",
    PAGADO: "badge-online",
    FINALIZADO: "badge-offline",
    NO_DISPONIBLE: "badge-offline",
  };
  const cls = map[estado] || "badge-pending";
  return `<span class="badge ${cls}">${estado}</span>`;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function apiErrorMessage(data, fallback) {
  if (!data) return fallback;
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail)) return data.detail.join(" ");
  if (typeof data === "object") {
    for (const value of Object.values(data)) {
      if (Array.isArray(value) && value[0]) return String(value[0]);
      if (typeof value === "string") return value;
    }
  }
  return fallback;
}

function setAuthError(formId, message) {
  const el = document.getElementById(formId === "form-login" ? "auth-login-error" : "auth-register-error");
  if (!el) return;
  if (message) {
    el.textContent = message;
    el.classList.add("visible");
  } else {
    el.textContent = "";
    el.classList.remove("visible");
  }
}

function formatMoney(value) {
  const n = Number(value);
  if (Number.isNaN(n)) return `$${value}`;
  return `$${n.toLocaleString("es-CO")}`;
}

function formatDate(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso + "T12:00:00").toLocaleDateString("es-CO", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  } catch {
    return iso;
  }
}

// ─── Autenticación ────────────────────────────────────────────────────────

function isStaffUser(user) {
  return user && (user.rol === "VENDOR" || user.rol === "ADMIN");
}

async function routeAfterAuth(user) {
  if (isStaffUser(user) && window.TechRentAdmin) {
    window.TechRentAdmin.boot(user);
    return;
  }
  await onSessionReady();
}

function showAuthGate() {
  document.getElementById("auth-gate")?.classList.remove("hidden");
  document.getElementById("app-shell")?.classList.add("hidden");
  document.getElementById("admin-shell")?.classList.add("hidden");
}

function showAppShell() {
  document.getElementById("auth-gate")?.classList.add("hidden");
  document.getElementById("app-shell")?.classList.remove("hidden");
  document.getElementById("admin-shell")?.classList.add("hidden");
}

function updateUserUI() {
  const u = state.user;
  if (!u) return;
  const firstName = (u.nombre || "").split(" ")[0] || u.nombre;
  const setText = (id, text) => {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  };
  setText("dashboard-user-name", firstName);
  setText("sidebar-user-name", u.nombre);
  setText("sidebar-user-email", u.email);
  setText("header-user-badge", u.email);
  setText("alquiler-session-hint", `Sesión: ${u.nombre} · #${u.id}`);
  const avatar = document.getElementById("header-avatar");
  if (avatar) avatar.textContent = avatarInitials(u.nombre);
}

function applyResumen(resumen) {
  state.resumen = resumen;
  if (!resumen) return;
  const set = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = String(val ?? 0);
  };
  set("dash-total", resumen.total_alquileres);
  set("dash-activos", resumen.activos);
  set("dash-pendientes", resumen.pendientes_pago);
  set("dash-finalizados", resumen.finalizados);
}

async function fetchMe() {
  const res = await apiFetch(`${API.v1}/auth/me/`);
  const data = await parseJsonSafe(res);
  if (!res.ok) throw new Error(data.detail || "Sin sesión");
  state.user = data.usuario;
  applyResumen(data.resumen);
  updateUserUI();
  return data;
}

function initFloatingLabels() {
  document.querySelectorAll(".field-group input, .field-group select").forEach((input) => {
    const group = input.closest(".field-group");
    const sync = () => group?.classList.toggle("has-value", Boolean(input.value?.trim()));
    input.addEventListener("input", sync);
    input.addEventListener("change", sync);
    sync();
  });
}

function initAuthTabs() {
  const tabLogin = document.getElementById("auth-tab-login");
  const tabRegister = document.getElementById("auth-tab-register");
  const formLogin = document.getElementById("form-login");
  const formRegister = document.getElementById("form-register");

  function showLogin() {
    tabLogin?.classList.add("text-cyan-300", "bg-cyan-500/10");
    tabLogin?.classList.remove("text-slate-400");
    tabRegister?.classList.remove("text-cyan-300", "bg-cyan-500/10");
    tabRegister?.classList.add("text-slate-400");
    formLogin?.classList.remove("is-hidden");
    formRegister?.classList.add("is-hidden");
    setAuthError("form-register", "");
  }

  function showRegister() {
    tabRegister?.classList.add("text-cyan-300", "bg-cyan-500/10");
    tabRegister?.classList.remove("text-slate-400");
    tabLogin?.classList.remove("text-cyan-300", "bg-cyan-500/10");
    tabLogin?.classList.add("text-slate-400");
    formRegister?.classList.remove("is-hidden");
    formLogin?.classList.add("is-hidden");
    setAuthError("form-login", "");
  }

  tabLogin?.addEventListener("click", showLogin);
  tabRegister?.addEventListener("click", showRegister);
  showLogin();
}

async function submitAuthForm(form, { url, payload, successToast, formKey }) {
  const btn = form.querySelector('button[type="submit"]');
  setAuthError(formKey, "");
  if (btn) {
    btn.disabled = true;
    btn.setAttribute("aria-busy", "true");
  }
  try {
    const res = await apiFetch(url, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    const data = await parseJsonSafe(res);
    if (!res.ok) {
      throw new Error(apiErrorMessage(data, "No se pudo completar la solicitud."));
    }
    state.user = data;
    setAuthError(formKey, "");
    await routeAfterAuth(data);
    toast(successToast(data));
    form.reset();
  } catch (err) {
    const msg = err.message || "Error de conexión. Revisa que Docker esté en marcha.";
    setAuthError(formKey, msg);
    toast(msg, "error");
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.removeAttribute("aria-busy");
    }
  }
}

function initAuthForms() {
  const formLogin = document.getElementById("form-login");
  const formRegister = document.getElementById("form-register");

  formLogin?.addEventListener("submit", (e) => {
    e.preventDefault();
    const email = document.getElementById("login-email")?.value.trim();
    const password = document.getElementById("login-password")?.value || "";
    if (!email || !password) {
      setAuthError("form-login", "Completa correo y contraseña.");
      return;
    }
    submitAuthForm(formLogin, {
      url: `${API.v1}/auth/login/`,
      payload: { email, password },
      formKey: "form-login",
      successToast: (data) => `Bienvenido, ${data.nombre}`,
    });
  });

  formRegister?.addEventListener("submit", (e) => {
    e.preventDefault();
    const nombre = document.getElementById("register-nombre")?.value.trim();
    const email = document.getElementById("register-email")?.value.trim();
    const password = document.getElementById("register-password")?.value || "";
    if (!nombre || !email || !password) {
      setAuthError("form-register", "Completa todos los campos.");
      return;
    }
    submitAuthForm(formRegister, {
      url: `${API.v1}/auth/registro/`,
      payload: { nombre, email, password },
      formKey: "form-register",
      successToast: (data) => `Cuenta creada — hola, ${data.nombre}`,
    });
  });
}

function initLogout() {
  document.getElementById("btn-logout")?.addEventListener("click", async () => {
    try {
      await apiFetch(`${API.v1}/auth/logout/`, { method: "POST" });
    } catch {
      /* ignorar */
    }
    state.user = null;
    state.resumen = null;
    state.misAlquileres = [];
    document.getElementById("admin-shell")?.classList.add("hidden");
    showAuthGate();
    toast("Sesión cerrada");
  });
}

async function onSessionReady() {
  showAppShell();
  try {
    await fetchMe();
  } catch {
    /* usuario ya en state desde login */
  }
  await loadMisAlquileres();
  refreshDashboardQuick();
  refreshIcons();
  if (typeof window.techrentNavigate === "function") {
    window.techrentNavigate(state.section || "dashboard");
  }
}

async function initAuth() {
  initAuthTabs();
  initAuthForms();
  initLogout();
  showAuthGate();
  try {
    await fetchMe();
    if (isStaffUser(state.user)) {
      await routeAfterAuth(state.user);
    } else {
      await onSessionReady();
    }
  } catch {
    showAuthGate();
  }
}

// ─── Navegación ─────────────────────────────────────────────────────────

function initNavigation() {
  const links = document.querySelectorAll("[data-section]");
  const sections = document.querySelectorAll(".page-section");
  const title = document.getElementById("page-title");

  const titles = {
    dashboard: "Inicio",
    equipos: "Catálogo",
    alquileres: "Nuevo alquiler",
    "mis-alquileres": "Mis alquileres",
    pagos: "Pagos",
  };

  function goTo(section) {
    state.section = section;
    links.forEach((l) => {
      l.classList.toggle("active", l.dataset.section === section);
    });
    sections.forEach((s) => {
      s.classList.toggle("active", s.id === `section-${section}`);
    });
    if (title) title.textContent = titles[section] || section;
    document.getElementById("sidebar")?.classList.remove("open");
    document.getElementById("sidebar-overlay")?.classList.remove("open");

    if (section === "equipos") loadEquiposTable();
    if (section === "dashboard") refreshDashboard();
    if (section === "mis-alquileres") loadMisAlquileres();
    if (section === "alquileres") updateUserUI();
    refreshIcons();
  }

  links.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      goTo(link.dataset.section);
    });
  });

  window.techrentNavigate = goTo;
}

function initSidebarMobile() {
  const toggle = document.getElementById("sidebar-toggle");
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebar-overlay");
  toggle?.addEventListener("click", () => {
    sidebar?.classList.toggle("open");
    overlay?.classList.toggle("open");
  });
  overlay?.addEventListener("click", () => {
    sidebar?.classList.remove("open");
    overlay?.classList.remove("open");
  });
}

// ─── Dashboard ────────────────────────────────────────────────────────────

async function refreshDashboard() {
  try {
    await fetchMe();
    await loadMisAlquileres();
    refreshDashboardQuick();
  } catch (err) {
    toast(err.message, "error");
  }
}

function refreshDashboardQuick() {
  const el = document.getElementById("dashboard-quick-list");
  if (!el) return;
  const recientes = [...state.misAlquileres]
    .sort((a, b) => (b.id || 0) - (a.id || 0))
    .slice(0, 4);

  if (!recientes.length) {
    el.innerHTML =
      '<p class="text-slate-500">Aún no tienes alquileres. <button type="button" class="text-cyan-400 hover:underline" onclick="techrentNavigate(\'equipos\')">Explora el catálogo</button></p>';
    return;
  }

  el.innerHTML = recientes
    .map(
      (a) => `
    <div class="flex items-center justify-between py-3 border-t border-slate-800/60 first:border-0 gap-3">
      <div class="min-w-0">
        <p class="font-medium text-slate-200 truncate">${escapeHtml(a.equipo_nombre || "Equipo")}</p>
        <p class="text-xs text-slate-500">${formatDate(a.fecha_inicio)} → ${formatDate(a.fecha_fin)}</p>
      </div>
      <div class="flex items-center gap-2 shrink-0">
        ${statusBadge(a.estado)}
        <span class="text-xs font-mono text-cyan-400">${formatMoney(a.costo_total)}</span>
      </div>
    </div>`,
    )
    .join("");
}

// ─── Mis alquileres ───────────────────────────────────────────────────────

function filterAlquileres(list, filter) {
  if (filter === "todos") return list;
  if (filter === "historial") {
    return list.filter((a) => a.estado === "FINALIZADO");
  }
  return list.filter((a) => a.estado === "PENDIENTE" || a.estado === "PAGADO");
}

function renderAlquilerCard(a) {
  const puedePagar = a.estado === "PENDIENTE";
  return `
    <article class="glass-card p-5 space-y-3 lift">
      <div class="flex justify-between items-start gap-2">
        <div>
          <p class="text-[10px] text-slate-500 font-mono">Alquiler #${a.id}</p>
          <h4 class="font-semibold text-slate-100">${escapeHtml(a.equipo_nombre || "Equipo")}</h4>
          <p class="text-xs text-slate-500">${escapeHtml(a.equipo_categoria || "")}</p>
        </div>
        ${statusBadge(a.estado)}
      </div>
      <div class="text-xs text-slate-400 space-y-1">
        <p><span class="text-slate-500">Desde:</span> ${formatDate(a.fecha_inicio)}</p>
        <p><span class="text-slate-500">Hasta:</span> ${formatDate(a.fecha_fin)}</p>
        <p class="text-base font-mono text-cyan-300 pt-1">${formatMoney(a.costo_total)}</p>
      </div>
      <div class="flex flex-wrap gap-2 pt-1">
        ${
          puedePagar
            ? `<button type="button" class="btn-primary text-xs px-3 py-1.5 rounded-lg text-slate-950" onclick="prepararPago(${a.id}, '${a.costo_total}')">Pagar ahora</button>`
            : ""
        }
        <button type="button" class="btn-ghost text-xs px-3 py-1.5 rounded-lg" onclick="document.getElementById('alquiler-equipo-id').value=${a.equipo_id}; techrentNavigate('alquileres')">Renovar</button>
      </div>
    </article>`;
}

window.prepararPago = function prepararPago(alquilerId, monto) {
  const idEl = document.getElementById("pago-alquiler-id");
  const montoEl = document.getElementById("pago-monto");
  if (idEl) idEl.value = alquilerId;
  if (montoEl) montoEl.value = monto;
  if (typeof window.techrentNavigate === "function") {
    window.techrentNavigate("pagos");
  }
  toast("Completa el pago en el formulario");
};

async function loadMisAlquileres() {
  const container = document.getElementById("mis-alquileres-list");
  if (!container) return;
  container.innerHTML =
    '<p class="text-slate-500 text-sm col-span-full py-8 text-center">Cargando…</p>';

  try {
    const res = await apiFetch(`${API.v1}/mis-alquileres/`);
    const data = await parseJsonSafe(res);
    if (!res.ok) throw new Error(data.detail || "Error al cargar alquileres");
    state.misAlquileres = Array.isArray(data) ? data : [];
    renderMisAlquileres();
    refreshDashboardQuick();
  } catch (err) {
    container.innerHTML = `<p class="text-red-400 text-sm col-span-full py-8 text-center">${escapeHtml(err.message)}</p>`;
    toast(err.message, "error");
  }
}

function renderMisAlquileres() {
  const container = document.getElementById("mis-alquileres-list");
  if (!container) return;

  const filtered = filterAlquileres(state.misAlquileres, state.alquilerFilter);

  if (!filtered.length) {
    const msg =
      state.alquilerFilter === "historial"
        ? "No tienes alquileres finalizados."
        : state.alquilerFilter === "activos"
          ? "No tienes alquileres en curso."
          : "No tienes alquileres registrados.";
    container.innerHTML = `<p class="text-slate-500 text-sm col-span-full py-12 text-center">${msg}</p>`;
    return;
  }

  container.innerHTML = filtered.map(renderAlquilerCard).join("");
  refreshIcons();
}

function initMisAlquileresFilters() {
  document.querySelectorAll("[data-alquiler-filter]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.alquilerFilter = btn.dataset.alquilerFilter;
      document.querySelectorAll("[data-alquiler-filter]").forEach((b) => {
        b.classList.toggle("active", b === btn);
      });
      renderMisAlquileres();
    });
  });
}

// ─── Equipos ────────────────────────────────────────────────────────────────

const CATEGORIA_META = {
  Laptop: { icon: "laptop", color: "cyan" },
  Tablet: { icon: "tablet", color: "blue" },
  Cámara: { icon: "camera", color: "purple" },
  Smartphone: { icon: "smartphone", color: "cyan" },
  Drone: { icon: "plane", color: "blue" },
  "VR/AR": { icon: "glasses", color: "purple" },
  Consola: { icon: "gamepad-2", color: "cyan" },
  Proyector: { icon: "presentation", color: "blue" },
  Monitor: { icon: "monitor", color: "cyan" },
  Periférico: { icon: "keyboard", color: "purple" },
  Audio: { icon: "mic", color: "purple" },
  Streaming: { icon: "radio", color: "cyan" },
  Redes: { icon: "wifi", color: "blue" },
  Almacenamiento: { icon: "hard-drive", color: "cyan" },
  Impresión: { icon: "printer", color: "blue" },
  Electrónica: { icon: "cpu", color: "purple" },
  Diseño: { icon: "pen-tool", color: "purple" },
  Desktop: { icon: "monitor-dot", color: "cyan" },
  Otros: { icon: "package", color: "blue" },
};

let equiposFiltroCategoria = "all";
let equiposBusqueda = "";

function groupEquiposByCategoria(equipos) {
  const groups = {};
  for (const e of equipos) {
    const cat = e.categoria || "Otros";
    if (!groups[cat]) groups[cat] = [];
    groups[cat].push(e);
  }
  return Object.keys(groups)
    .sort((a, b) => a.localeCompare(b, "es"))
    .map((categoria) => ({
      categoria,
      equipos: groups[categoria].sort((a, b) =>
        (a.nombre || "").localeCompare(b.nombre || "", "es"),
      ),
    }));
}

function getCategoriaMeta(categoria) {
  return CATEGORIA_META[categoria] || { icon: "box", color: "cyan" };
}

function renderEquipoRow(e) {
  const equipoId = e.id ?? e.pk;
  const idLabel = equipoId != null ? `#${equipoId}` : "—";
  const idAttr = equipoId != null ? equipoId : "";
  const rawNombre = e.nombre || "";
  const nombre = escapeHtml(rawNombre);
  const searchKey = rawNombre.toLowerCase().replace(/"/g, "");
  return `
    <tr class="equipo-row-compact border-t border-slate-800/60" data-nombre="${searchKey}">
      <td class="py-2 px-4">
        <div class="flex items-center gap-2.5 min-w-[180px]">
          <div class="h-8 w-8 rounded-lg bg-gradient-to-br from-cyan-500/15 to-purple-500/15 flex items-center justify-center text-[10px] font-bold text-cyan-300 shrink-0">${avatarInitials(e.nombre)}</div>
          <div class="min-w-0">
            <p class="font-medium text-slate-100 truncate text-sm">${nombre}</p>
            <p class="text-[10px] text-slate-500 font-mono">ID ${idLabel}</p>
          </div>
        </div>
      </td>
      <td class="py-2 px-4 font-mono text-cyan-300/90 text-sm whitespace-nowrap">$${e.precio_por_dia}</td>
      <td class="py-2 px-4 whitespace-nowrap">${statusBadge(e.estado)}</td>
      <td class="py-2 px-4 text-right whitespace-nowrap">
        <button type="button" class="btn-ghost text-[11px] px-2.5 py-1 rounded-md" ${idAttr ? `onclick="document.getElementById('alquiler-equipo-id').value=${idAttr}; techrentNavigate('alquileres')"` : "disabled"}>Alquilar</button>
      </td>
    </tr>`;
}

function renderCategoriaBlock(grupo, openByDefault) {
  const meta = getCategoriaMeta(grupo.categoria);
  const colorMap = {
    cyan: "from-cyan-500/20 to-cyan-500/5 text-cyan-400 border-cyan-500/20",
    blue: "from-blue-500/20 to-blue-500/5 text-blue-400 border-blue-500/20",
    purple: "from-purple-500/20 to-purple-500/5 text-purple-400 border-purple-500/20",
  };
  const colorCls = colorMap[meta.color] || colorMap.cyan;
  const disponibles = grupo.equipos.filter((e) => e.estado === "DISPONIBLE").length;

  return `
    <article class="category-block ${openByDefault ? "is-open" : ""}" data-categoria="${escapeHtml(grupo.categoria)}">
      <button type="button" class="category-header" aria-expanded="${openByDefault}">
        <div class="flex items-center gap-3 min-w-0">
          <div class="category-icon-wrap bg-gradient-to-br ${colorCls} border">
            <i data-lucide="${meta.icon}" class="w-4 h-4"></i>
          </div>
          <div class="text-left min-w-0">
            <h4 class="font-semibold text-slate-100">${escapeHtml(grupo.categoria)}</h4>
            <p class="text-[11px] text-slate-500">${grupo.equipos.length} equipos · ${disponibles} disponibles</p>
          </div>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <span class="text-xs text-slate-600 font-mono hidden sm:inline">▼</span>
        </div>
      </button>
      <div class="category-body">
        <div class="category-body-inner">
          <table class="data-table w-full">
            <thead class="text-[10px] text-slate-500 uppercase tracking-wider bg-slate-900/40">
              <tr>
                <th class="py-2 px-4 text-left font-medium">Equipo</th>
                <th class="py-2 px-4 text-left font-medium">Precio/día</th>
                <th class="py-2 px-4 text-left font-medium">Estado</th>
                <th class="py-2 px-4 text-right font-medium">Acción</th>
              </tr>
            </thead>
            <tbody>
              ${grupo.equipos.map(renderEquipoRow).join("")}
            </tbody>
          </table>
        </div>
      </div>
    </article>`;
}

function renderEquiposFiltros(grupos, total) {
  const container = document.getElementById("equipos-filtros");
  if (!container) return;

  const pills = [
    `<button type="button" data-categoria="all" class="category-pill ${equiposFiltroCategoria === "all" ? "active" : ""}">Todas (${total})</button>`,
  ];
  for (const g of grupos) {
    const active = equiposFiltroCategoria === g.categoria ? "active" : "";
    pills.push(
      `<button type="button" data-categoria="${escapeHtml(g.categoria)}" class="category-pill ${active}">${escapeHtml(g.categoria)} (${g.equipos.length})</button>`,
    );
  }
  container.innerHTML = pills.join("");

  container.querySelectorAll(".category-pill").forEach((btn) => {
    btn.addEventListener("click", () => {
      equiposFiltroCategoria = btn.dataset.categoria;
      applyEquiposFiltros();
      container.querySelectorAll(".category-pill").forEach((b) => {
        b.classList.toggle("active", b.dataset.categoria === equiposFiltroCategoria);
      });
    });
  });
}

function applyEquiposFiltros() {
  const blocks = document.querySelectorAll(".category-block");
  const term = equiposBusqueda.trim().toLowerCase();

  blocks.forEach((block) => {
    const cat = block.dataset.categoria;
    const matchCategoria =
      equiposFiltroCategoria === "all" || equiposFiltroCategoria === cat;

    let visibleRows = 0;
    block.querySelectorAll(".equipo-row-compact").forEach((row) => {
      const nombre = row.dataset.nombre || "";
      const matchSearch = !term || nombre.includes(term);
      row.classList.toggle("hidden", !matchSearch);
      if (matchSearch) visibleRows += 1;
    });

    const showBlock = matchCategoria && (visibleRows > 0 || !term);
    block.classList.toggle("is-filtered-out", !showBlock);
  });

  const resumen = document.getElementById("equipos-resumen");
  if (resumen && state.equipos.length) {
    const visibles = document.querySelectorAll(
      ".category-block:not(.is-filtered-out) .equipo-row-compact:not(.hidden)",
    ).length;
    resumen.textContent = `${visibles} de ${state.equipos.length} equipos visibles`;
  }
}

function bindCategoryAccordions() {
  document.querySelectorAll(".category-header").forEach((btn) => {
    btn.addEventListener("click", () => {
      const block = btn.closest(".category-block");
      block?.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", block?.classList.contains("is-open"));
    });
  });
}

async function loadEquiposTable() {
  const catalog = document.getElementById("equipos-catalog");
  if (!catalog) return;

  catalog.innerHTML = `<div class="glass-card p-8 text-center text-slate-500 text-sm">Cargando inventario…</div>`;

  try {
    let fuente = "flask-ms";
    let res = await apiFetch(API.equiposFlask);
    let data = await parseJsonSafe(res);
    if (!res.ok || !Array.isArray(data) || !data.length) {
      fuente = "django-monolito";
      res = await apiFetch(`${API.v1}/equipos/`);
      data = await parseJsonSafe(res);
      if (!res.ok) throw new Error(data.detail || "Error equipos");
    }
    state.equipos = (Array.isArray(data) ? data : []).map((e) => ({
      ...e,
      estado: e.estado || (e.disponible === false ? "NO_DISPONIBLE" : "DISPONIBLE"),
    }));

    if (!state.equipos.length) {
      catalog.innerHTML = `<div class="glass-card p-8 text-center text-slate-500 text-sm">Sin equipos en catálogo.</div>`;
      return;
    }

    const grupos = groupEquiposByCategoria(state.equipos);
    renderEquiposFiltros(grupos, state.equipos.length);
    catalog.innerHTML = grupos.map((g, i) => renderCategoriaBlock(g, i < 2)).join("");

    const resumen = document.getElementById("equipos-resumen");
    if (resumen) {
      resumen.textContent = `${state.equipos.length} equipos en ${grupos.length} categorías · ${fuente === "flask-ms" ? "Flask MS (Strangler)" : "Django"}`;
    }

    bindCategoryAccordions();
    applyEquiposFiltros();
    refreshIcons();
  } catch (err) {
    catalog.innerHTML = `<div class="glass-card p-6 text-center text-red-400 text-sm">${escapeHtml(err.message)}</div>`;
    toast(err.message, "error");
  }
}

function initEquiposUI() {
  const search = document.getElementById("equipos-buscar");
  search?.addEventListener("input", (e) => {
    equiposBusqueda = e.target.value;
    applyEquiposFiltros();
    if (equiposBusqueda) {
      document.querySelectorAll(".category-block").forEach((b) => b.classList.add("is-open"));
    }
  });

  document.getElementById("equipos-expand-all")?.addEventListener("click", () => {
    const blocks = document.querySelectorAll(".category-block");
    const anyClosed = Array.from(blocks).some((b) => !b.classList.contains("is-open"));
    blocks.forEach((b) => b.classList.toggle("is-open", anyClosed));
    document.querySelectorAll(".category-header").forEach((btn) => {
      btn.setAttribute(
        "aria-expanded",
        btn.closest(".category-block")?.classList.contains("is-open"),
      );
    });
  });
}

// ─── Formularios ──────────────────────────────────────────────────────────

function initForms() {
  document.getElementById("form-alquiler")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      equipo_id: parseInt(document.getElementById("alquiler-equipo-id").value, 10),
      fecha_inicio: document.getElementById("alquiler-fecha-inicio").value,
      fecha_fin: document.getElementById("alquiler-fecha-fin").value,
    };
    const btn = e.target.querySelector('button[type="submit"]');
    btn.disabled = true;
    try {
      const res = await apiFetch(`${API.v1}/alquileres/`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      const data = await parseJsonSafe(res);
      if (!res.ok) throw new Error(data.detail || "Error al crear alquiler");
      toast(`Alquiler #${data.id} creado — ${formatMoney(data.costo_total)}`);
      document.getElementById("pago-alquiler-id").value = data.id;
      document.getElementById("pago-monto").value = data.costo_total;
      await fetchMe();
      await loadMisAlquileres();
      window.prepararPago(data.id, data.costo_total);
    } catch (err) {
      toast(err.message, "error");
    } finally {
      btn.disabled = false;
    }
  });

  document.getElementById("form-pago")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      alquiler_id: parseInt(document.getElementById("pago-alquiler-id").value, 10),
      monto: document.getElementById("pago-monto").value,
      metodo: document.getElementById("pago-metodo").value,
    };
    const btn = e.target.querySelector('button[type="submit"]');
    btn.disabled = true;
    try {
      const res = await apiFetch(API.pagos, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      const data = await parseJsonSafe(res);
      if (!res.ok) throw new Error(data.detail || "Error al procesar pago");
      toast(`Pago #${data.id} confirmado`);
      await apiFetch(`${API.v1}/notificar-pago/`, {
        method: "POST",
        body: JSON.stringify({
          alquiler_id: payload.alquiler_id,
          monto: payload.monto,
        }),
      });
      await fetchMe();
      await loadMisAlquileres();
      e.target.reset();
    } catch (err) {
      toast(err.message, "error");
    } finally {
      btn.disabled = false;
    }
  });
}

// ─── Init ─────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  const lang = document.documentElement.getAttribute("lang") || "es";
  if (window.TechRentI18n) window.TechRentI18n.apply(lang);
  initFloatingLabels();
  initNavigation();
  initSidebarMobile();
  initForms();
  initEquiposUI();
  initMisAlquileresFilters();
  initAuth();
  refreshIcons();
});
