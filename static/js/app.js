(() => {
  "use strict";

  const TicketshopApi = window.TicketshopApi;
  if (!TicketshopApi) {
    document.addEventListener("DOMContentLoaded", () => {
      const main = document.getElementById("app-main");
      if (main) {
        main.innerHTML =
          '<div class="error-box">Не загружен JavaScript API (<code>/static/js/api.js</code>). ' +
          "Откройте сайт через сервер FastAPI: <code>http://127.0.0.1:8000/</code>, обновите страницу (Ctrl+F5).</div>";
      }
    });
    return;
  }

  const { Auth, Concerts, Halls, Groups, Sales, Watchlist, Admin, getToken } = TicketshopApi;

  /** Увеличивается при каждом переходе; устаревшие async-отрисовки не затирают экран. */
  let routeGeneration = 0;

  function el(html) {
    const t = document.createElement("template");
    t.innerHTML = html.trim();
    return t.content.firstChild;
  }

  function formatDate(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    return d.toLocaleString("ru-RU", {
      dateStyle: "long",
      timeStyle: "short",
    });
  }

  function parseRoute() {
    const raw = location.hash.replace(/^#\/?/, "").trim();
    const segs = raw ? raw.split("/").filter(Boolean) : [];
    if (segs.length === 0) return { name: "home", args: [] };
    return { name: segs[0], args: segs.slice(1) };
  }

  function navigate(to) {
    location.hash = to.startsWith("#") ? to : "#" + to;
  }

  let cachedUser = null;

  async function loadUser() {
    if (!getToken()) {
      cachedUser = null;
      return null;
    }
    try {
      cachedUser = await Auth.me();
      return cachedUser;
    } catch {
      cachedUser = null;
      TicketshopApi.setToken(null);
      return null;
    }
  }

  function setActiveNav() {
    const r = parseRoute();
    const path = r.name + (r.args[0] ? "/" + r.args[0] : "");
    document.querySelectorAll(".nav a[data-route]").forEach((a) => {
      const target = a.getAttribute("data-route");
      a.classList.toggle("active", path === target || (target && path.startsWith(target)));
    });
  }

  function renderLayout(innerHtml, paintGen) {
    if (paintGen !== routeGeneration) return;
    const main = document.getElementById("app-main");
    if (!main) return;
    main.innerHTML = "";
    main.appendChild(typeof innerHtml === "string" ? el(innerHtml) : innerHtml);
    setActiveNav();
  }

  async function renderHome(paintGen) {
    renderLayout(
      el(`<div class="hero">
        <h1>Мероприятия</h1>
        <p class="muted">Загрузка списка с сервера…</p>
      </div><div class="grid cols-2"><p class="empty muted">Подождите</p></div>`),
      paintGen
    );

    let concerts = [];
    let halls = [];
    let allGroups = [];
    let err = "";
    try {
      const [concertsRes, hallsRes, groupsRes] = await Promise.all([
        (async () => {
          const all = [];
          const pageSize = 50;
          let offset = 0;
          while (paintGen === routeGeneration) {
            const page = await Concerts.list(pageSize, offset);
            if (!Array.isArray(page) || page.length === 0) break;
            all.push(...page);
            if (page.length < pageSize) break;
            offset += pageSize;
          }
          return all;
        })(),
        Halls.list(),
        Groups.list(),
      ]);
      concerts = concertsRes;
      halls = hallsRes;
      allGroups = groupsRes;
    } catch (e) {
      err = e.message || String(e);
    }

    if (paintGen !== routeGeneration) return;

    // Загружаем группы для всех концертов параллельно
    const groupsMap = {};
    if (concerts.length) {
      const groupResults = await Promise.allSettled(
        concerts.map((c) => Concerts.groups(c.id_concert))
      );
      concerts.forEach((c, i) => {
        groupsMap[c.id_concert] =
          groupResults[i].status === "fulfilled" ? groupResults[i].value : [];
      });
    }

    if (paintGen !== routeGeneration) return;

    // Карта залов для фильтрации
    const hallMap = {};
    halls.forEach((h) => { hallMap[h.id_hall] = h.name; });

    // Уникальные группы из реально привязанных
    const usedGroupIds = new Set();
    Object.values(groupsMap).forEach((gs) => gs.forEach((g) => usedGroupIds.add(g.id_group)));
    const filterGroups = allGroups.filter((g) => usedGroupIds.has(g.id_group));

    // --- Построение интерфейса ---
    const wrap = el("<div></div>");
    wrap.innerHTML = `
      <div class="hero">
        <h1>Мероприятия</h1>
        <p class="muted">Выберите концерт и купите билет онлайн.</p>
      </div>
      <div class="filter-panel">
        <div class="filter-row">
          <input type="text" id="f-search" class="filter-input" placeholder="Поиск по названию или артисту…">
        </div>
        <div class="filter-row filter-selects">
          <select id="f-group"><option value="">Все артисты</option></select>
          <select id="f-hall"><option value="">Все залы</option></select>
          <input type="date" id="f-date-from" class="filter-input" title="Дата от">
          <input type="date" id="f-date-to" class="filter-input" title="Дата до">
          <button type="button" id="f-reset" class="btn btn-ghost btn-sm">Сбросить</button>
        </div>
      </div>
    `;
    if (err) wrap.appendChild(el(`<div class="error-box">${escapeHtml(err)}</div>`));
    const grid = el('<div class="grid cols-2" id="concerts-grid"></div>');
    wrap.appendChild(grid);

    // Заполняем <select>
    const selGroup = wrap.querySelector("#f-group");
    filterGroups
      .sort((a, b) => a.name.localeCompare(b.name))
      .forEach((g) => {
        const o = document.createElement("option");
        o.value = String(g.id_group);
        o.textContent = g.name;
        selGroup.appendChild(o);
      });

    const selHall = wrap.querySelector("#f-hall");
    halls
      .sort((a, b) => a.name.localeCompare(b.name))
      .forEach((h) => {
        const o = document.createElement("option");
        o.value = String(h.id_hall);
        o.textContent = h.name;
        selHall.appendChild(o);
      });

    // --- Функция отрисовки карточек ---
    function renderCards() {
      const search = wrap.querySelector("#f-search").value.trim().toLowerCase();
      const groupId = wrap.querySelector("#f-group").value;
      const hallId = wrap.querySelector("#f-hall").value;
      const dateFrom = wrap.querySelector("#f-date-from").value;
      const dateTo = wrap.querySelector("#f-date-to").value;

      grid.innerHTML = "";

      const filtered = concerts.filter((c) => {
        const groups = groupsMap[c.id_concert] || [];

        // Текстовый поиск — по названию концерта и именам групп
        if (search) {
          const inName = c.name.toLowerCase().includes(search);
          const inGroups = groups.some((g) => g.name.toLowerCase().includes(search));
          if (!inName && !inGroups) return false;
        }
        // Фильтр по артисту
        if (groupId && !groups.some((g) => String(g.id_group) === groupId)) return false;
        // Фильтр по залу
        if (hallId && String(c.id_hall) !== hallId) return false;
        // Фильтр по дате
        const cd = new Date(c.date);
        if (dateFrom && cd < new Date(dateFrom)) return false;
        if (dateTo) {
          const to = new Date(dateTo);
          to.setHours(23, 59, 59, 999);
          if (cd > to) return false;
        }
        return true;
      });

      if (!filtered.length) {
        grid.appendChild(el('<p class="empty">Ничего не найдено.</p>'));
        return;
      }

      filtered.forEach((c) => {
        const paused = c.sales_paused ? '<span class="badge warn">Продажи приостановлены</span>' : "";
        const groups = groupsMap[c.id_concert] || [];
        const groupsHtml = groups.length
          ? `<div class="concert-groups"><span class="groups-label">Группы:</span> ${groups
              .map((g) => `<span class="group-tag">${escapeHtml(g.name)}</span>`)
              .join("")}</div>`
          : "";
        const hallName = hallMap[c.id_hall];
        const hallHtml = hallName ? `<div class="muted" style="font-size:0.82rem">${escapeHtml(hallName)}</div>` : "";
        const card = el(`<article class="card clickable">
          <div class="card-title">${escapeHtml(c.name)}</div>
          <div class="muted">${formatDate(c.date)}</div>
          ${hallHtml}
          ${groupsHtml}
          <div style="margin-top:0.5rem">${paused}</div>
        </article>`);
        card.addEventListener("click", () => navigate("#/concert/" + c.id_concert));
        grid.appendChild(card);
      });
    }

    // Вешаем обработчики
    wrap.querySelector("#f-search").addEventListener("input", renderCards);
    wrap.querySelector("#f-group").addEventListener("change", renderCards);
    wrap.querySelector("#f-hall").addEventListener("change", renderCards);
    wrap.querySelector("#f-date-from").addEventListener("change", renderCards);
    wrap.querySelector("#f-date-to").addEventListener("change", renderCards);
    wrap.querySelector("#f-reset").addEventListener("click", () => {
      wrap.querySelector("#f-search").value = "";
      wrap.querySelector("#f-group").value = "";
      wrap.querySelector("#f-hall").value = "";
      wrap.querySelector("#f-date-from").value = "";
      wrap.querySelector("#f-date-to").value = "";
      renderCards();
    });

    renderCards();
    renderLayout(wrap, paintGen);
  }

  function escapeHtml(s) {
    if (s == null) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  async function renderConcertDetail(id, paintGen) {
    const wrap = el("<div></div>");
    let c;
    try {
      c = await Concerts.get(id);
    } catch (e) {
      renderLayout(`<div class="error-box">${escapeHtml(e.message)}</div>`, paintGen);
      return;
    }
    if (paintGen !== routeGeneration) return;

    let concertGroups = [];
    try {
      concertGroups = await Concerts.groups(id);
    } catch { /* не блокируем отрисовку */ }
    if (paintGen !== routeGeneration) return;

    const desc = c.description
      ? `<p>${escapeHtml(c.description).replace(/\n/g, "<br>")}</p>`
      : '<p class="muted">Описание пока не указано.</p>';
    const paused = c.sales_paused
      ? '<p><span class="badge warn">Продажи билетов остановлены администратором</span></p>'
      : "";
    const groupsHtml = concertGroups.length
      ? `<div class="concert-groups detail">
           <span class="groups-label">Выступают:</span>
           ${concertGroups.map((g) => `<span class="group-tag">${escapeHtml(g.name)}</span>`).join("")}
         </div>`
      : "";
    wrap.innerHTML = `
    <h1>${escapeHtml(c.name)}</h1>
    <p class="muted">${formatDate(c.date)}</p>
    ${paused}
    ${groupsHtml}
    ${desc}
    <div class="actions" id="concert-actions"></div>
    <p style="margin-top:1rem"><a href="#/">← На главную</a></p>
  `;
    const actions = wrap.querySelector("#concert-actions");
    const user = await loadUser();
    if (paintGen !== routeGeneration) return;

    if (!user) {
      actions.appendChild(el('<span class="muted">Войдите, чтобы отслеживать и покупать билеты.</span>'));
      actions.appendChild(el('<a class="btn btn-primary" href="#/login">Войти</a>'));
    } else {
      let watching = false;
      try {
        const st = await Watchlist.status(id);
        watching = st.watching;
      } catch {
        /* ignore */
      }
      if (paintGen !== routeGeneration) return;

      const btnWatch = el(
        `<button type="button" class="btn btn-ghost">${watching ? "Убрать из отслеживаемых" : "Отслеживать"}</button>`
      );
      btnWatch.addEventListener("click", async () => {
        btnWatch.disabled = true;
        try {
          if (watching) {
            await Watchlist.remove(id);
            watching = false;
          } else {
            await Watchlist.add(id);
            watching = true;
          }
          btnWatch.textContent = watching ? "Убрать из отслеживаемых" : "Отслеживать";
        } catch (e) {
          alert(e.message);
        }
        btnWatch.disabled = false;
      });
      actions.appendChild(btnWatch);
      const btnBuy = el('<button type="button" class="btn btn-primary">Купить билет</button>');
      btnBuy.disabled = !!c.sales_paused;
      btnBuy.addEventListener("click", () => navigate("#/buy/" + id));
      actions.appendChild(btnBuy);
    }
    renderLayout(wrap, paintGen);
  }

  async function renderWatchlist(paintGen) {
    const user = await loadUser();
    if (paintGen !== routeGeneration) return;

    if (!user) {
      navigate("#/login");
      return;
    }
    let list = [];
    try {
      list = await Watchlist.list();
    } catch (e) {
      renderLayout(`<div class="error-box">${escapeHtml(e.message)}</div>`, paintGen);
      return;
    }
    if (paintGen !== routeGeneration) return;

    const wrap = el("<div></div>");
    wrap.innerHTML = `<h1>Отслеживаемое</h1>`;
    if (!list.length) {
      wrap.appendChild(
        el('<p class="empty">Вы пока не добавили мероприятия. Откройте концерт и нажмите «Отслеживать».</p>')
      );
    } else {
      const grid = el('<div class="grid cols-2"></div>');
      list.forEach((c) => {
        const card = el(`<article class="card clickable">
        <div class="card-title">${escapeHtml(c.name)}</div>
        <div class="muted">${formatDate(c.date)}</div>
      </article>`);
        card.addEventListener("click", () => navigate("#/concert/" + c.id_concert));
        grid.appendChild(card);
      });
      wrap.appendChild(grid);
    }
    wrap.appendChild(el('<p><a href="#/">← На главную</a></p>'));
    renderLayout(wrap, paintGen);
  }

  async function renderProfile(paintGen) {
    const user = await loadUser();
    if (paintGen !== routeGeneration) return;

    if (!user) {
      navigate("#/login");
      return;
    }
    const wrap = el("<div></div>");
    wrap.innerHTML = `
    <h1>Профиль</h1>
    <form id="profile-form">
      <div class="form-row"><label>Email</label><input name="email" value="${escapeHtml(user.email)}" disabled></div>
      <div class="form-row"><label>Имя</label><input name="name" value="${escapeHtml(user.name || "")}"></div>
      <div class="form-row"><label>Фамилия</label><input name="surname" value="${escapeHtml(user.surname || "")}"></div>
      <div class="form-row"><label>Возраст</label><input name="age" type="number" min="1" max="100" value="${user.age ?? ""}"></div>
      <div class="form-row"><label>Новый пароль (оставьте пустым, если не меняете)</label><input name="password" type="password" autocomplete="new-password"></div>
      <button type="submit" class="btn btn-primary">Сохранить</button>
    </form>
    <p style="margin-top:1.5rem"><a href="#/">← На главную</a></p>
  `;
    wrap.querySelector("#profile-form").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      const payload = {};
      const name = fd.get("name");
      const surname = fd.get("surname");
      const age = fd.get("age");
      const password = fd.get("password");
      if (name) payload.name = name;
      if (surname) payload.surname = surname;
      if (age !== "" && age != null) payload.age = parseInt(age, 10);
      if (password) payload.password = password;
      try {
        await Auth.patchMe(payload);
        await loadUser();
        alert("Сохранено");
      } catch (e) {
        alert(e.message);
      }
    });
    renderLayout(wrap, paintGen);
  }

  // ── Модальные окна ──────────────────────────────────────────────────────────

  function showConfirmModal(title, text, onYes) {
    const existing = document.getElementById("_confirm-modal");
    if (existing) existing.remove();

    const modal = el(`
      <div id="_confirm-modal" class="modal-overlay">
        <div class="modal-box">
          <h2 class="modal-title">${escapeHtml(title)}</h2>
          <p class="modal-text">${escapeHtml(text)}</p>
          <div class="modal-actions">
            <button type="button" class="btn btn-ghost" id="_confirm-no">Отмена</button>
            <button type="button" class="btn btn-primary" id="_confirm-yes">Да</button>
          </div>
        </div>
      </div>
    `);
    document.body.appendChild(modal);
    modal.querySelector("#_confirm-yes").addEventListener("click", () => {
      modal.remove();
      onYes();
    });
    modal.querySelector("#_confirm-no").addEventListener("click", () => modal.remove());
    modal.addEventListener("click", (e) => { if (e.target === modal) modal.remove(); });
  }

  function showSuccessModal(title, text, onClose) {
    const existing = document.getElementById("_success-modal");
    if (existing) existing.remove();

    const modal = el(`
      <div id="_success-modal" class="modal-overlay">
        <div class="modal-box">
          <div class="modal-icon">🎉</div>
          <h2 class="modal-title">${escapeHtml(title)}</h2>
          <p class="modal-text">${text}</p>
          <div class="modal-actions">
            <button type="button" class="btn btn-primary" id="_success-ok">Отлично!</button>
          </div>
        </div>
      </div>
    `);
    document.body.appendChild(modal);
    const close = () => { modal.remove(); if (onClose) onClose(); };
    modal.querySelector("#_success-ok").addEventListener("click", close);
    modal.addEventListener("click", (e) => { if (e.target === modal) close(); });
  }

  // ── Страница бронирования (шаг 1 — выбор билета) — устарело ────────────────
  async function _unused_renderBuy(concertId, paintGen) {
    const user = await loadUser();
    if (paintGen !== routeGeneration) return;

    if (!user) {
      navigate("#/login");
      return;
    }
    let c;
    let options = [];
    try {
      c = await Concerts.get(concertId);
      options = await Concerts.purchaseOptions(concertId);
    } catch (e) {
      renderLayout(`<div class="error-box">${escapeHtml(e.message)}</div>`, paintGen);
      return;
    }
    if (paintGen !== routeGeneration) return;

    if (c.sales_paused) {
      renderLayout(
        `<div class="error-box">Продажи на это мероприятие приостановлены.</div>
         <p><a href="#/concert/${concertId}">← Назад</a></p>`,
        paintGen
      );
      return;
    }

    const wrap = el("<div></div>");
    const prefillName      = escapeHtml(user.name    || "");
    const prefillSurname   = escapeHtml(user.surname || "");
    const prefillBirthDate = "";
    wrap.innerHTML = `
      <h1>Оформление билета</h1>
      <p class="muted">${escapeHtml(c.name)} · ${formatDate(c.date)}</p>
      <form id="buy-form" style="max-width:480px;margin-top:1.5rem">

        <div class="card" style="margin-bottom:1.25rem">
          <h2 style="margin-top:0;font-size:1.05rem">Данные покупателя</h2>
          <div class="form-row">
            <label>Имя <span style="color:var(--danger)">*</span></label>
            <input name="name" value="${prefillName}" required placeholder="Введите имя">
          </div>
          <div class="form-row">
            <label>Фамилия <span style="color:var(--danger)">*</span></label>
            <input name="surname" value="${prefillSurname}" required placeholder="Введите фамилию">
          </div>
          <div class="form-row">
            <label>Дата рождения <span style="color:var(--danger)">*</span></label>
            <input name="birth_date" type="date" value="${prefillBirthDate}" required>
          </div>
        </div>

        <div class="card">
          <h2 style="margin-top:0;font-size:1.05rem">Билет</h2>
          <div class="form-row">
            <label>Тип билета / зона</label>
            <select name="ticket_type" required></select>
          </div>
          <div class="form-row">
            <label>Количество</label>
            <input name="count" type="number" min="1" value="1" required>
          </div>
        </div>

        <div class="actions" style="margin-top:1.25rem">
          <button type="submit" class="btn btn-primary">Перейти к оплате →</button>
        </div>
      </form>
      <p style="margin-top:1rem"><a href="#/concert/${concertId}">← К мероприятию</a></p>
    `;

    const sel = wrap.querySelector('select[name="ticket_type"]');
    if (!options.length) {
      sel.innerHTML = '<option value="">Нет доступных билетов</option>';
      sel.disabled = true;
    } else {
      options.forEach((o) => {
        const opt = document.createElement("option");
        opt.value = String(o.id_ticket_type);
        opt.textContent = `${o.ticket_type_name} — ${o.price} ₽ (осталось: ${o.remains})`;
        opt.dataset.price = String(o.price);
        sel.appendChild(opt);
      });
    }

    wrap.querySelector("#buy-form").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      const name      = fd.get("name")?.trim() || "";
      const surname   = fd.get("surname")?.trim() || "";
      const birthDate = fd.get("birth_date") || "";
      const idType    = parseInt(fd.get("ticket_type"), 10);
      const count     = parseInt(fd.get("count"), 10);
      if (!idType) return;
      const selectedOpt = sel.options[sel.selectedIndex];
      const price = parseInt(selectedOpt?.dataset.price || "0", 10);

      // Вычисляем возраст из даты рождения и обновляем профиль
      const profilePatch = {};
      if (name)    profilePatch.name    = name;
      if (surname) profilePatch.surname = surname;
      if (birthDate) {
        const born = new Date(birthDate);
        const age  = Math.floor((Date.now() - born.getTime()) / (365.25 * 24 * 60 * 60 * 1000));
        if (age > 0 && age <= 100) profilePatch.age = age;
      }
      if (Object.keys(profilePatch).length) {
        try { await Auth.patchMe(profilePatch); } catch (_) {}
      }

      // Сохраняем бронь и переходим на выбор мест
      const booking = {
        concertId: parseInt(concertId, 10),
        concertName: c.name,
        concertDate: c.date,
        idType,
        ticketTypeName: selectedOpt?.text.split(" —")[0] || "",
        count,
        price,
        seats: [],
        expiresAt: Date.now() + 15 * 60 * 1000, // 15 минут
      };
      sessionStorage.setItem("ticketBooking", JSON.stringify(booking));
      navigate("#/seats/" + concertId);
    });

    renderLayout(wrap, paintGen);
  }

  // ── Страница выбора мест (шаг 2 — карта зала) ──────────────────────────────

  async function renderSeats(concertId, paintGen) {
    const user = await loadUser();
    if (paintGen !== routeGeneration) return;
    if (!user) { navigate("#/login"); return; }

    let c, layout;
    try {
      c = await Concerts.get(concertId);
      layout = await Concerts.hallLayout(concertId);
    } catch (e) {
      renderLayout(`<div class="error-box">${escapeHtml(e.message)}</div>`, paintGen);
      return;
    }
    if (paintGen !== routeGeneration) return;

    if (c.sales_paused) {
      renderLayout(
        `<div class="error-box">Продажи на это мероприятие приостановлены.</div>
         <p><a href="#/concert/${concertId}">← Назад</a></p>`,
        paintGen
      );
      return;
    }

    const occupiedSet = new Set(layout.occupied.map(([r, s]) => `${r}:${s}`));

    // Selection state: either seated seats from ONE zone OR a dance-count from ONE zone.
    // selection = { zone, kind: "seated", seats: Set<"row:seat"> } or
    //             { zone, kind: "dance", count: N } or null
    let selection = null;

    const wrap = el("<div></div>");
    wrap.innerHTML = `
      <h1>Выбор мест</h1>
      <p class="muted">${escapeHtml(c.name)} · ${formatDate(c.date)}</p>

      <div class="seatmap-info">
        <div>Выбранная зона: <strong id="sel-zone">—</strong></div>
        <div>Выбрано: <strong id="sel-count">0</strong></div>
        <div>Итого: <strong id="sel-total">0 ₽</strong></div>
      </div>

      <div class="seatmap-legend">
        ${layout.zones.map(z => `
          <span class="legend-item">
            <span class="legend-swatch" style="background:${z.color}"></span>
            ${escapeHtml(z.name)} · ${z.price} ₽
          </span>
        `).join("")}
        <span class="legend-item">
          <span class="legend-swatch" style="background:#3b3f4d"></span>Занято
        </span>
        <span class="legend-item">
          <span class="legend-swatch" style="background:#ffffff;border:2px solid #7c6cf0"></span>Выбрано
        </span>
      </div>

      <div class="seatmap">
        <div class="seatmap-stage">СЦЕНА</div>
        <div id="seatmap-body"></div>
      </div>

      <div class="actions" style="margin-top:1.25rem">
        <button type="button" class="btn btn-primary" id="btn-to-pay" disabled>Перейти к оформлению →</button>
        <button type="button" class="btn btn-ghost" id="btn-back-seats">← К мероприятию</button>
      </div>
    `;

    const body = wrap.querySelector("#seatmap-body");
    const zoneByKey = new Map(); // "row:seat" -> zone (seated only)
    const seatedKeyToBtn = new Map();

    for (const z of layout.zones) {
      const block = document.createElement("div");
      block.className = "seatmap-zone seatmap-zone-" + z.role;
      const header = document.createElement("div");
      header.className = "seatmap-zone-title";
      header.textContent = `${z.name} — ${z.price} ₽ · осталось ${z.remains}`;
      block.appendChild(header);

      if (z.role === "dance") {
        // Single big clickable circle for dance floor
        const holder = document.createElement("div");
        holder.className = "seatmap-dance-holder";
        const circle = document.createElement("button");
        circle.type = "button";
        circle.className = "dance-circle";
        circle.style.background = z.color;
        circle.dataset.zoneId = z.id_hall_zone;
        circle.innerHTML = `<span class="dance-circle-label">${escapeHtml(z.name)}</span>
                            <span class="dance-circle-sub">нажмите, чтобы выбрать</span>`;
        if (z.remains <= 0) {
          circle.disabled = true;
          circle.classList.add("dance-circle-sold");
          circle.querySelector(".dance-circle-sub").textContent = "распродано";
        }
        circle.addEventListener("click", () => openDanceModal(z));
        holder.appendChild(circle);
        block.appendChild(holder);
      } else {
        const rowMap = new Map();
        for (const p of z.seats) {
          if (!rowMap.has(p.row)) rowMap.set(p.row, []);
          rowMap.get(p.row).push(p);
        }
        const sortedRows = [...rowMap.keys()].sort((a, b) => a - b);
        for (const r of sortedRows) {
          const rowEl = document.createElement("div");
          rowEl.className = "seatmap-row";
          const label = document.createElement("span");
          label.className = "seatmap-row-label";
          label.textContent = "Ряд " + r;
          rowEl.appendChild(label);
          const seats = rowMap.get(r).sort((a, b) => a.seat - b.seat);
          for (const p of seats) {
            const key = `${p.row}:${p.seat}`;
            zoneByKey.set(key, z);
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "seat seat-" + z.role;
            btn.dataset.key = key;
            btn.style.background = z.color;
            btn.title = `Ряд ${p.row}, место ${p.seat} — ${z.price} ₽`;
            btn.textContent = p.seat;
            if (occupiedSet.has(key)) {
              btn.classList.add("seat-occupied");
              btn.disabled = true;
            }
            rowEl.appendChild(btn);
            seatedKeyToBtn.set(key, btn);
          }
          block.appendChild(rowEl);
        }
      }
      body.appendChild(block);
    }

    function refreshSummary() {
      const zoneEl  = wrap.querySelector("#sel-zone");
      const cntEl   = wrap.querySelector("#sel-count");
      const totEl   = wrap.querySelector("#sel-total");
      const btnPay  = wrap.querySelector("#btn-to-pay");
      if (!selection) {
        zoneEl.textContent = "—";
        cntEl.textContent = "0";
        totEl.textContent = "0 ₽";
        btnPay.disabled = true;
        return;
      }
      zoneEl.textContent = selection.zone.name;
      const count = selection.kind === "dance" ? selection.count : selection.seats.size;
      cntEl.textContent = String(count);
      totEl.textContent = (count * selection.zone.price) + " ₽";
      btnPay.disabled = count <= 0;
    }

    function clearSeatedSelectionVisual() {
      for (const btn of seatedKeyToBtn.values()) btn.classList.remove("seat-selected");
    }

    function startSeatedSelection(zone) {
      selection = { zone, kind: "seated", seats: new Set() };
    }

    async function maybeSwitchZone(newZone, newKind) {
      if (!selection) return true;
      const sameZone = selection.zone.id_hall_zone === newZone.id_hall_zone && selection.kind === newKind;
      if (sameZone) return true;
      if (!confirm("Вы уже выбирали места в другой зоне. Сбросить выбор и переключиться на «" + newZone.name + "»?")) {
        return false;
      }
      clearSeatedSelectionVisual();
      selection = null;
      return true;
    }

    body.addEventListener("click", async (ev) => {
      const btn = ev.target.closest(".seat");
      if (!btn || btn.disabled) return;
      const key = btn.dataset.key;
      const zone = zoneByKey.get(key);
      if (!zone) return;
      const ok = await maybeSwitchZone(zone, "seated");
      if (!ok) return;
      if (!selection) startSeatedSelection(zone);
      if (selection.seats.has(key)) {
        selection.seats.delete(key);
        btn.classList.remove("seat-selected");
      } else {
        selection.seats.add(key);
        btn.classList.add("seat-selected");
      }
      if (selection.kind === "seated" && selection.seats.size === 0) selection = null;
      refreshSummary();
    });

    function openDanceModal(zone) {
      // Confirm zone switch if needed
      maybeSwitchZone(zone, "dance").then((ok) => {
        if (!ok) return;
        const startCount = (selection && selection.kind === "dance" && selection.zone.id_hall_zone === zone.id_hall_zone)
          ? selection.count : 1;
        const maxCount = Math.max(1, zone.remains);
        const modal = el(`
          <div class="modal-overlay" id="_dance-modal">
            <div class="modal-card" style="max-width:380px">
              <h3 style="margin-top:0">${escapeHtml(zone.name)}</h3>
              <p class="muted" style="margin:0 0 1rem">Цена за 1 билет: <strong>${zone.price} ₽</strong></p>
              <div class="dance-counter">
                <button type="button" class="btn btn-ghost" id="_dc-minus">−</button>
                <input type="number" id="_dc-count" min="1" max="${maxCount}" value="${startCount}" />
                <button type="button" class="btn btn-ghost" id="_dc-plus">+</button>
              </div>
              <p class="muted" style="margin:0.75rem 0">Доступно: ${zone.remains}</p>
              <p style="font-size:1.1rem;margin:0 0 1rem">Итого: <strong id="_dc-total">${zone.price * startCount} ₽</strong></p>
              <div class="actions">
                <button type="button" class="btn btn-primary" id="_dc-ok">Выбрать</button>
                <button type="button" class="btn btn-ghost" id="_dc-cancel">Отмена</button>
              </div>
            </div>
          </div>
        `);
        document.body.appendChild(modal);
        const input = modal.querySelector("#_dc-count");
        const totalEl = modal.querySelector("#_dc-total");
        const clamp = () => {
          let v = parseInt(input.value, 10);
          if (isNaN(v) || v < 1) v = 1;
          if (v > maxCount) v = maxCount;
          input.value = String(v);
          totalEl.textContent = (v * zone.price) + " ₽";
        };
        modal.querySelector("#_dc-minus").addEventListener("click", () => { input.value = String(parseInt(input.value, 10) - 1); clamp(); });
        modal.querySelector("#_dc-plus").addEventListener("click",  () => { input.value = String(parseInt(input.value, 10) + 1); clamp(); });
        input.addEventListener("input", clamp);
        const close = () => modal.remove();
        modal.querySelector("#_dc-cancel").addEventListener("click", close);
        modal.addEventListener("click", (e) => { if (e.target === modal) close(); });
        modal.querySelector("#_dc-ok").addEventListener("click", () => {
          clamp();
          const v = parseInt(input.value, 10);
          clearSeatedSelectionVisual();
          selection = { zone, kind: "dance", count: v };
          refreshSummary();
          close();
        });
      });
    }

    wrap.querySelector("#btn-back-seats").addEventListener("click", () => {
      navigate("#/concert/" + concertId);
    });

    wrap.querySelector("#btn-to-pay").addEventListener("click", () => {
      if (!selection) return;
      const zone = selection.zone;
      const count = selection.kind === "dance" ? selection.count : selection.seats.size;
      if (count <= 0) return;
      const seatsArr = selection.kind === "seated"
        ? [...selection.seats].map((k) => k.split(":").map(Number))
        : [];
      const booking = {
        concertId: parseInt(concertId, 10),
        concertName: c.name,
        concertDate: c.date,
        idType: zone.id_ticket_type,
        ticketTypeName: zone.name,
        zoneRole: zone.role,
        count,
        price: zone.price,
        seats: seatsArr,
        expiresAt: Date.now() + 15 * 60 * 1000,
      };
      sessionStorage.setItem("ticketBooking", JSON.stringify(booking));
      navigate("#/checkout");
    });

    refreshSummary();
    renderLayout(wrap, paintGen);
  }

  // ── Страница оплаты (шаг 3 — таймер + подтверждение) ────────────────────────

  async function renderCheckout(paintGen) {
    const user = await loadUser();
    if (paintGen !== routeGeneration) return;
    if (!user) { navigate("#/login"); return; }

    const bookingRaw = sessionStorage.getItem("ticketBooking");
    if (!bookingRaw) {
      renderLayout('<div class="error-box">Бронь не найдена. Выберите билет снова.</div><p><a href="#/">← На главную</a></p>', paintGen);
      return;
    }
    const booking = JSON.parse(bookingRaw);

    // Проверяем не истекла ли бронь ещё до рендера
    if (Date.now() > booking.expiresAt) {
      sessionStorage.removeItem("ticketBooking");
      renderLayout(
        `<div class="error-box">Время бронирования истекло. Пожалуйста, начните оформление заново.</div>
         <p><a href="#/concert/${booking.concertId}">← К мероприятию</a></p>`,
        paintGen
      );
      return;
    }

    const total = booking.price * booking.count;

    const prefillName    = escapeHtml(user.name    || "");
    const prefillSurname = escapeHtml(user.surname || "");

    const wrap = el("<div></div>");
    wrap.innerHTML = `
      <h1>Оформление билета</h1>
      <div class="checkout-timer-wrap">
        <span class="checkout-timer-label">Бронь действует:</span>
        <span id="checkout-timer" class="checkout-timer">15:00</span>
      </div>
      <form id="checkout-form" style="max-width:520px;margin-top:1.5rem">
        <div class="card" style="margin-bottom:1.25rem">
          <h2 style="margin-top:0;font-size:1.05rem">Данные покупателя</h2>
          <div class="form-row">
            <label>Имя <span style="color:var(--danger)">*</span></label>
            <input name="name" value="${prefillName}" required placeholder="Введите имя">
          </div>
          <div class="form-row">
            <label>Фамилия <span style="color:var(--danger)">*</span></label>
            <input name="surname" value="${prefillSurname}" required placeholder="Введите фамилию">
          </div>
          <div class="form-row">
            <label>Дата рождения <span style="color:var(--danger)">*</span></label>
            <input name="birth_date" type="date" required>
          </div>
        </div>

        <div class="card" style="margin-bottom:1.25rem">
          <h2 style="margin-top:0;font-size:1.05rem">Ваш заказ</h2>
          <table class="checkout-summary">
            <tr><td class="muted">Концерт</td><td><strong>${escapeHtml(booking.concertName)}</strong></td></tr>
            <tr><td class="muted">Дата</td><td>${formatDate(booking.concertDate)}</td></tr>
            <tr><td class="muted">Тип билета</td><td>${escapeHtml(booking.ticketTypeName)}</td></tr>
            <tr><td class="muted">Количество</td><td>${booking.count} шт.</td></tr>
            ${(booking.seats && booking.seats.length) ? `<tr><td class="muted">Места</td><td>${booking.seats.map(([r, s]) => `Р${r}-М${s}`).join(", ")}</td></tr>` : ""}
            <tr class="checkout-total"><td>Итого</td><td><strong>${total} ₽</strong></td></tr>
          </table>
        </div>

        <div class="actions">
          <button type="submit" class="btn btn-primary" id="btn-pay">Оплатить ${total} ₽</button>
          <button type="button" class="btn btn-ghost" id="btn-back-booking">← К выбору мест</button>
        </div>
      </form>
    `;

    // Таймер обратного отсчёта
    const timerEl = wrap.querySelector("#checkout-timer");
    let timerInterval = null;

    function updateTimer() {
      const left = booking.expiresAt - Date.now();
      if (left <= 0) {
        clearInterval(timerInterval);
        sessionStorage.removeItem("ticketBooking");
        renderLayout(
          `<div class="error-box">Время бронирования истекло. Пожалуйста, начните оформление заново.</div>
           <p><a href="#/concert/${booking.concertId}">← К мероприятию</a></p>`,
          paintGen
        );
        return;
      }
      const m = Math.floor(left / 60000);
      const s = Math.floor((left % 60000) / 1000);
      timerEl.textContent = `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
      timerEl.classList.toggle("checkout-timer-urgent", left < 60000);
    }

    updateTimer();
    timerInterval = setInterval(updateTimer, 1000);

    // Останавливаем таймер при уходе со страницы
    const stopTimer = () => clearInterval(timerInterval);
    window.addEventListener("hashchange", stopTimer, { once: true });

    // Кнопка «Назад» — сохраняем бронь, возвращаем на схему зала
    wrap.querySelector("#btn-back-booking").addEventListener("click", () => {
      stopTimer();
      navigate("#/buy/" + booking.concertId);
    });

    // Отправка формы оформления → оплата
    wrap.querySelector("#checkout-form").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      if (Date.now() > booking.expiresAt) {
        stopTimer();
        sessionStorage.removeItem("ticketBooking");
        renderLayout(
          `<div class="error-box">Время бронирования истекло.</div>
           <p><a href="#/concert/${booking.concertId}">← К мероприятию</a></p>`,
          paintGen
        );
        return;
      }
      const fd = new FormData(ev.target);
      const name      = (fd.get("name") || "").toString().trim();
      const surname   = (fd.get("surname") || "").toString().trim();
      const birthDate = (fd.get("birth_date") || "").toString();

      // Обновляем профиль покупателя (имя/фамилия/возраст)
      const profilePatch = {};
      if (name)    profilePatch.name    = name;
      if (surname) profilePatch.surname = surname;
      if (birthDate) {
        const born = new Date(birthDate);
        const age  = Math.floor((Date.now() - born.getTime()) / (365.25 * 24 * 60 * 60 * 1000));
        if (age > 0 && age <= 100) profilePatch.age = age;
      }
      if (Object.keys(profilePatch).length) {
        try { await Auth.patchMe(profilePatch); } catch (_) {}
      }

      const payBtn = wrap.querySelector("#btn-pay");
      payBtn.disabled = true;
      try {
        await Sales.buy({
          id_concert: booking.concertId,
          id_ticket_type: booking.idType,
          count: booking.count,
          seats: booking.seats && booking.seats.length ? booking.seats : null,
        });
        stopTimer();
        sessionStorage.removeItem("ticketBooking");
        showSuccessModal(
          "Поздравляем с покупкой!",
          `Вы приобрели билеты на концерт <strong>${escapeHtml(booking.concertName)}</strong>.<br><br>
           Ваши билеты отправлены вам на почту.`,
          () => navigate("#/profile")
        );
      } catch (e) {
        payBtn.disabled = false;
        alert(e.message);
      }
    });

    renderLayout(wrap, paintGen);
  }

  function renderLogin(paintGen) {
    const wrap = el("<div></div>");
    wrap.innerHTML = `
    <h1>Вход</h1>
    <form id="login-form">
      <div class="form-row"><label>Email</label><input name="email" type="email" required autocomplete="username"></div>
      <div class="form-row"><label>Пароль</label><input name="password" type="password" required autocomplete="current-password"></div>
      <button type="submit" class="btn btn-primary">Войти</button>
    </form>
    <p class="muted" style="margin-top:1rem">Нет аккаунта? <a href="#/register">Регистрация</a></p>
  `;
    wrap.querySelector("#login-form").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      try {
        await Auth.login(fd.get("email"), fd.get("password"));
        await loadUser();
        navigate("#/");
      } catch (e) {
        alert(e.message);
      }
    });
    renderLayout(wrap, paintGen);
  }

  function renderRegister(paintGen) {
    const wrap = el("<div></div>");
    wrap.innerHTML = `
    <h1>Регистрация</h1>
    <form id="reg-form">
      <div class="form-row"><label>Email</label><input name="email" type="email" required></div>
      <div class="form-row"><label>Пароль</label><input name="password" type="password" required minlength="3"></div>
      <button type="submit" class="btn btn-primary">Создать аккаунт</button>
    </form>
    <p class="muted" style="margin-top:1rem">Уже есть аккаунт? <a href="#/login">Войти</a></p>
  `;
    wrap.querySelector("#reg-form").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      try {
        await Auth.register(fd.get("email"), fd.get("password"));
        await Auth.login(fd.get("email"), fd.get("password"));
        await loadUser();
        navigate("#/");
      } catch (e) {
        alert(e.message);
      }
    });
    renderLayout(wrap, paintGen);
  }

  async function renderAdminHome(paintGen) {
  const main = document.getElementById("app-main");

  // Отрисовываем только админ-интерфейс
  main.innerHTML = `
    <div class="admin-home-container">
      <h1 class="admin-title">Панель управления Ticketmuse</h1>
      <p class="admin-subtitle">Добро пожаловать в систему администрирования</p>

      <div class="admin-dashboard-grid">
        <a href="#/admin/concerts" class="admin-card">
          <span class="icon">🎸</span>
          <span>Все концерты</span>
        </a>
        <a href="#/admin/halls" class="admin-card">
          <span class="icon">🏛</span>
          <span>Все концертные залы</span>
        </a>
        <a href="#/admin/groups" class="admin-card">
          <span class="icon">🎤</span>
          <span>Музыкальные группы</span>
        </a>
        <a href="#/admin/sales" class="admin-card">
          <span class="icon">💰</span>
          <span>Последние продажи</span>
        </a>
        <a href="#/admin/add" class="admin-card add-new">
          <span class="icon">➕</span>
          <span>Добавить объект</span>
        </a>
      </div>
    </div>
  `;
}

  async function renderAdminConcerts(paintGen) {
    const user = await loadUser();
    if (paintGen !== routeGeneration) return;

    if (!user || !user.is_admin) {
      renderLayout('<div class="error-box">Нужны права администратора.</div>', paintGen);
      return;
    }
    let concerts = [];
    let halls = [];
    try {
      concerts = await Concerts.list(200, 0);
      halls = await Halls.list();
    } catch (e) {
      renderLayout(`<div class="error-box">${escapeHtml(e.message)}</div>`, paintGen);
      return;
    }
    if (paintGen !== routeGeneration) return;

    const hallById = new Map(halls.map((h) => [h.id_hall, h]));
    const hallOpts = halls.map((h) => `<option value="${h.id_hall}">${escapeHtml(h.name)}</option>`).join("");
    const hallFilterOpts = '<option value="">Все залы</option>' + hallOpts;

    const wrap = el("<div></div>");
    wrap.innerHTML = `
    <h1>Концерты (админ)</h1>
    <h2>Новый концерт</h2>
    <form id="new-concert" class="card" style="margin-bottom:2rem">
      <div class="form-row"><label>Название</label><input name="name" required></div>
      <div class="form-row"><label>Дата и время</label><input name="date" type="datetime-local" required></div>
      <div class="form-row"><label>Зал</label><select name="id_hall" required>${hallOpts}</select></div>
      <div class="form-row"><label>Описание</label><textarea name="description"></textarea></div>
      <div class="form-row form-row-check">
        <label class="check-label"><input type="checkbox" name="sales_paused"> Продажи остановлены</label>
      </div>
      <button type="submit" class="btn btn-primary">Создать</button>
    </form>

    <div class="admin-filters">
      <input type="search" id="flt-q" placeholder="Поиск по названию или описанию…" />
      <select id="flt-hall">${hallFilterOpts}</select>
      <select id="flt-status">
        <option value="">Все статусы</option>
        <option value="ok">Продажи идут</option>
        <option value="paused">Остановлены</option>
      </select>
      <button type="button" class="btn btn-ghost" id="flt-reset">Сбросить</button>
    </div>

    <div class="table-wrap">
      <table class="admin-table"><thead><tr><th>Название</th><th>Дата</th><th>Зал</th><th>Продажи</th><th></th></tr></thead>
      <tbody id="admin-concerts-body"></tbody></table>
    </div>
    <p style="margin-top:1rem"><a href="#/admin">← Админ</a></p>
    <dialog id="edit-dlg" style="border:none;border-radius:12px;padding:0;max-width:480px;width:90%">
      <form method="dialog" id="edit-form" class="card" style="margin:0">
        <h2 style="margin-top:0">Редактировать</h2>
        <input type="hidden" name="cid">
        <div class="form-row"><label>Название</label><input name="name" required></div>
        <div class="form-row"><label>Дата</label><input name="date" type="datetime-local" required></div>
        <div class="form-row"><label>Зал</label><select name="id_hall">${hallOpts}</select></div>
        <div class="form-row"><label>Описание</label><textarea name="description"></textarea></div>
        <div class="form-row form-row-check">
          <label class="check-label"><input type="checkbox" name="sales_paused"> Продажи остановлены</label>
        </div>
        <div class="actions">
          <button type="submit" class="btn btn-primary">Сохранить</button>
          <button type="button" class="btn btn-ghost" id="edit-cancel">Отмена</button>
        </div>
      </form>
    </dialog>
  `;

    const tbody = wrap.querySelector("#admin-concerts-body");
    function rowHtml(c) {
      const hall = hallById.get(c.id_hall);
      return `
        <tr data-id="${c.id_concert}">
          <td><strong>${escapeHtml(c.name)}</strong></td>
          <td>${formatDate(c.date)}</td>
          <td>${escapeHtml(hall ? hall.name : "—")}</td>
          <td>${c.sales_paused ? '<span class="badge warn">Стоп</span>' : '<span class="badge ok">Ок</span>'}</td>
          <td>
            <button type="button" class="btn btn-ghost btn-edit" data-id="${c.id_concert}">Изменить</button>
            <button type="button" class="btn btn-danger btn-del" data-id="${c.id_concert}">Удалить</button>
          </td>
        </tr>`;
    }
    function applyFilters() {
      const q = (wrap.querySelector("#flt-q").value || "").trim().toLowerCase();
      const hallFlt = wrap.querySelector("#flt-hall").value;
      const statusFlt = wrap.querySelector("#flt-status").value;
      const filtered = concerts.filter((c) => {
        if (q && !((c.name || "").toLowerCase().includes(q) || (c.description || "").toLowerCase().includes(q))) return false;
        if (hallFlt && String(c.id_hall) !== hallFlt) return false;
        if (statusFlt === "ok" && c.sales_paused) return false;
        if (statusFlt === "paused" && !c.sales_paused) return false;
        return true;
      });
      tbody.innerHTML = filtered.length
        ? filtered.map(rowHtml).join("")
        : '<tr><td colspan="5" class="muted" style="text-align:center">Ничего не найдено</td></tr>';
      attachRowHandlers();
    }
    wrap.querySelector("#flt-q").addEventListener("input", applyFilters);
    wrap.querySelector("#flt-hall").addEventListener("change", applyFilters);
    wrap.querySelector("#flt-status").addEventListener("change", applyFilters);
    wrap.querySelector("#flt-reset").addEventListener("click", () => {
      wrap.querySelector("#flt-q").value = "";
      wrap.querySelector("#flt-hall").value = "";
      wrap.querySelector("#flt-status").value = "";
      applyFilters();
    });

    function toLocalInput(iso) {
      const d = new Date(iso);
      const pad = (n) => String(n).padStart(2, "0");
      return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
    }
    function fromLocalInput(s) {
      return new Date(s).toISOString();
    }

    wrap.querySelector("#new-concert").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      const payload = {
        name: fd.get("name"),
        date: fromLocalInput(fd.get("date")),
        id_hall: parseInt(fd.get("id_hall"), 10),
        description: fd.get("description") || null,
        sales_paused: fd.get("sales_paused") === "on",
      };
      try {
        await Concerts.create(payload);
        location.reload();
      } catch (e) {
        alert(e.message);
      }
    });

    const dlg = wrap.querySelector("#edit-dlg");
    const editForm = wrap.querySelector("#edit-form");

    wrap.querySelector("#edit-cancel").addEventListener("click", () => dlg.close());

    function attachRowHandlers() {
      tbody.querySelectorAll(".btn-edit").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const id = parseInt(btn.dataset.id, 10);
          const c = await Concerts.get(id);
          editForm.querySelector('input[name="cid"]').value = String(c.id_concert);
          editForm.name.value = c.name;
          editForm.date.value = toLocalInput(c.date);
          editForm.id_hall.value = String(c.id_hall);
          editForm.description.value = c.description || "";
          editForm.sales_paused.checked = !!c.sales_paused;
          dlg.showModal();
        });
      });
      tbody.querySelectorAll(".btn-del").forEach((btn) => {
        btn.addEventListener("click", async () => {
          if (!confirm("Удалить концерт?")) return;
          try {
            await Concerts.delete(parseInt(btn.dataset.id, 10));
            location.reload();
          } catch (e) {
            alert(e.message);
          }
        });
      });
    }

    editForm.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(editForm);
      const id = parseInt(fd.get("cid"), 10);
      const payload = {
        name: fd.get("name"),
        date: fromLocalInput(fd.get("date")),
        id_hall: parseInt(fd.get("id_hall"), 10),
        description: fd.get("description") || null,
        sales_paused: fd.get("sales_paused") === "on",
      };
      try {
        await Concerts.update(id, payload);
        dlg.close();
        location.reload();
      } catch (e) {
        alert(e.message);
      }
    });

    applyFilters();
    renderLayout(wrap, paintGen);
  }


let salesLimit = 10;

async function renderAdminSales(paintGen) {
  const user = await loadUser();
  if (paintGen !== routeGeneration) return;

  if (!user || !user.is_admin) {
    renderLayout('<div class="error-box">Нужны права администратора.</div>', paintGen);
    return;
  }

  let sales = [];
  try {
    sales = await Admin.recentSales(salesLimit);
  } catch (e) {
    renderLayout(`<div class="error-box">${escapeHtml(e.message)}</div>`, paintGen);
    return;
  }
  if (paintGen !== routeGeneration) return;

  const wrap = el("<div></div>");
  wrap.innerHTML = `
    <div class="admin-container">
      <h1>Недавние покупки билетов</h1>

      <div class="admin-filters">
        <input type="search" id="flt-q" placeholder="Поиск по e-mail или концерту…" />
        <select id="flt-sum">
          <option value="">Любая сумма</option>
          <option value="lt1000">До 1 000 ₽</option>
          <option value="1000-5000">1 000 – 5 000 ₽</option>
          <option value="gt5000">Больше 5 000 ₽</option>
        </select>
        <select id="flt-period">
          <option value="">Всё время</option>
          <option value="today">Сегодня</option>
          <option value="week">За 7 дней</option>
          <option value="month">За 30 дней</option>
        </select>
        <button type="button" class="btn btn-ghost" id="flt-reset">Сбросить</button>
      </div>

      <div class="table-wrap">
        <table class="admin-table">
          <thead>
            <tr><th>Дата</th><th>Пользователь</th><th>Концерт</th><th>Билетов</th><th>Сумма</th></tr>
          </thead>
          <tbody id="admin-sales-body"></tbody>
        </table>
      </div>

      <div style="text-align:center;margin-top:1.25rem">
        <button id="load-more-sales" class="btn btn-ghost" style="${sales.length < salesLimit ? 'display:none' : ''}">
          Показать ещё
        </button>
      </div>

      <p style="margin-top:1rem"><a href="#/admin">← Админ</a></p>
    </div>
  `;

  const tbody = wrap.querySelector("#admin-sales-body");
  function rowHtml(s) {
    const dt = s.created_at || s.sale_date;
    return `
      <tr>
        <td>${dt ? formatDate(dt) : "—"}</td>
        <td>${escapeHtml(s.user_email || (s.user && s.user.email) || "—")}</td>
        <td>${escapeHtml(s.concert_name || (s.concert && s.concert.title) || "—")}</td>
        <td>${s.count || 1}</td>
        <td><strong>${s.total_price || 0} ₽</strong></td>
      </tr>
    `;
  }
  function applyFilters() {
    const q = (wrap.querySelector("#flt-q").value || "").trim().toLowerCase();
    const sumF = wrap.querySelector("#flt-sum").value;
    const per = wrap.querySelector("#flt-period").value;
    const now = Date.now();
    const filtered = sales.filter((s) => {
      const email = (s.user_email || (s.user && s.user.email) || "").toLowerCase();
      const cname = (s.concert_name || (s.concert && s.concert.title) || "").toLowerCase();
      if (q && !email.includes(q) && !cname.includes(q)) return false;
      const sum = s.total_price || 0;
      if (sumF === "lt1000"     && !(sum < 1000))                   return false;
      if (sumF === "1000-5000"  && !(sum >= 1000 && sum <= 5000))   return false;
      if (sumF === "gt5000"     && !(sum > 5000))                   return false;
      if (per) {
        const d = new Date(s.created_at || s.sale_date).getTime();
        if (isNaN(d)) return false;
        const diff = now - d;
        if (per === "today" && diff > 24 * 3600 * 1000)        return false;
        if (per === "week"  && diff > 7 * 24 * 3600 * 1000)    return false;
        if (per === "month" && diff > 30 * 24 * 3600 * 1000)   return false;
      }
      return true;
    });
    tbody.innerHTML = filtered.length
      ? filtered.map(rowHtml).join("")
      : '<tr><td colspan="5" class="muted" style="text-align:center">Ничего не найдено</td></tr>';
  }
  wrap.querySelector("#flt-q").addEventListener("input", applyFilters);
  wrap.querySelector("#flt-sum").addEventListener("change", applyFilters);
  wrap.querySelector("#flt-period").addEventListener("change", applyFilters);
  wrap.querySelector("#flt-reset").addEventListener("click", () => {
    wrap.querySelector("#flt-q").value = "";
    wrap.querySelector("#flt-sum").value = "";
    wrap.querySelector("#flt-period").value = "";
    applyFilters();
  });

  const loadMore = wrap.querySelector("#load-more-sales");
  if (loadMore) {
    loadMore.addEventListener("click", async () => {
      salesLimit += 10;
      await renderAdminSales(paintGen);
    });
  }

  applyFilters();
  renderLayout(wrap, paintGen);
}
async function renderAdminHalls(paintGen) {
  const user = await loadUser();
  if (paintGen !== routeGeneration) return;

  if (!user || !user.is_admin) {
    renderLayout('<div class="error-box">Доступ запрещен.</div>', paintGen);
    return;
  }

  let halls = [];
  try {
    halls = await Halls.list();
  } catch (e) {
    renderLayout(`<div class="error-box">${escapeHtml(e.message)}</div>`, paintGen);
    return;
  }

  const wrap = el("<div></div>");
  wrap.innerHTML = `
    <div class="admin-container">
      <h1>Управление залами</h1>

      <div class="admin-filters">
        <input type="search" id="flt-q" placeholder="Поиск по названию или адресу…" />
        <select id="flt-cap">
          <option value="">Любая вместимость</option>
          <option value="small">Маленькие (до 500)</option>
          <option value="medium">Средние (500–2000)</option>
          <option value="large">Большие (от 2000)</option>
        </select>
        <button type="button" class="btn btn-ghost" id="flt-reset">Сбросить</button>
      </div>

      <div class="table-wrap">
        <table class="admin-table">
          <thead>
            <tr><th>ID</th><th>Название</th><th>Адрес</th><th>Телефон</th><th>Вместимость</th><th>Схема</th><th>Действия</th></tr>
          </thead>
          <tbody id="admin-halls-body"></tbody>
        </table>
      </div>
      <p style="margin-top:1rem"><a href="#/admin">← Админ</a></p>
    </div>
  `;

  const tbody = wrap.querySelector("#admin-halls-body");
  function rowHtml(h) {
    const cap = h.seatsAmount != null ? `${h.seatsAmount} чел.` : "—";
    const scheme = `${h.scheme || "classic"} · ${h.rows_count || "?"}×${h.seats_per_row || "?"}`;
    return `
      <tr>
        <td class="muted">#${h.id_hall}</td>
        <td><strong>${escapeHtml(h.name)}</strong></td>
        <td>${escapeHtml(h.address || "—")}</td>
        <td>${escapeHtml(h.phone || "—")}</td>
        <td>${cap}</td>
        <td class="muted">${escapeHtml(scheme)}</td>
        <td>
          <button type="button" class="btn btn-danger btn-del" data-id="${h.id_hall}">Удалить</button>
        </td>
      </tr>
    `;
  }
  function applyFilters() {
    const q = (wrap.querySelector("#flt-q").value || "").trim().toLowerCase();
    const cap = wrap.querySelector("#flt-cap").value;
    const filtered = halls.filter((h) => {
      if (q) {
        const hay = `${h.name || ""} ${h.address || ""}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      const s = h.seatsAmount || 0;
      if (cap === "small"  && !(s > 0   && s < 500))   return false;
      if (cap === "medium" && !(s >= 500 && s <= 2000)) return false;
      if (cap === "large"  && !(s > 2000))               return false;
      return true;
    });
    tbody.innerHTML = filtered.length
      ? filtered.map(rowHtml).join("")
      : '<tr><td colspan="7" class="muted" style="text-align:center">Ничего не найдено</td></tr>';
    tbody.querySelectorAll(".btn-del").forEach((btn) => {
      btn.addEventListener("click", async () => {
        if (!confirm("Удалить этот зал?")) return;
        try {
          await Halls.delete(parseInt(btn.dataset.id, 10));
          await renderAdminHalls(paintGen);
        } catch (e) {
          alert("Ошибка при удалении: " + e.message);
        }
      });
    });
  }
  wrap.querySelector("#flt-q").addEventListener("input", applyFilters);
  wrap.querySelector("#flt-cap").addEventListener("change", applyFilters);
  wrap.querySelector("#flt-reset").addEventListener("click", () => {
    wrap.querySelector("#flt-q").value = "";
    wrap.querySelector("#flt-cap").value = "";
    applyFilters();
  });
  applyFilters();
  renderLayout(wrap, paintGen);
}


// Вспомогательная функция удаления зала
window.deleteHall = async (id, gen) => {
  if (!confirm("Удалить этот зал?")) return;
  try {
    await Halls.delete(id);
    await renderAdminHalls(gen); // Перерисовываем список
  } catch (e) {
    alert("Ошибка при удалении: " + e.message);
  }
};

async function renderAdminGroups(paintGen) {
  const user = await loadUser();
  if (paintGen !== routeGeneration) return;

  let groups = [];
  try {
    groups = await Groups.list();
  } catch (e) {
    renderLayout(`<div class="error-box">${escapeHtml(e.message)}</div>`, paintGen);
    return;
  }

  // Unique genre ids for filter dropdown
  const genreIds = [...new Set(groups.map((g) => g.id_genre).filter((x) => x != null))].sort((a, b) => a - b);

  const wrap = el("<div></div>");
  wrap.innerHTML = `
    <div class="admin-container">
      <h1>Музыкальные группы</h1>

      <div class="admin-filters">
        <input type="search" id="flt-q" placeholder="Поиск по названию или сайту…" />
        <select id="flt-genre">
          <option value="">Все жанры</option>
          ${genreIds.map((gid) => `<option value="${gid}">Жанр #${gid}</option>`).join("")}
        </select>
        <select id="flt-albums">
          <option value="">Любое число альбомов</option>
          <option value="0">Без альбомов</option>
          <option value="1-3">1–3</option>
          <option value="4-9">4–9</option>
          <option value="10">10 и больше</option>
        </select>
        <button type="button" class="btn btn-ghost" id="flt-reset">Сбросить</button>
      </div>

      <div class="table-wrap">
        <table class="admin-table">
          <thead>
            <tr><th>ID</th><th>Название</th><th>Альбомов</th><th>Сайт</th><th>Жанр</th><th>Действия</th></tr>
          </thead>
          <tbody id="admin-groups-body"></tbody>
        </table>
      </div>
      <p style="margin-top:1rem"><a href="#/admin">← Админ</a></p>
    </div>
  `;

  const tbody = wrap.querySelector("#admin-groups-body");
  function rowHtml(g) {
    const site = g.site
      ? `<a href="${escapeHtml(g.site)}" target="_blank" rel="noopener">${escapeHtml(g.site)}</a>`
      : '<span class="muted">—</span>';
    return `
      <tr>
        <td class="muted">#${g.id_group}</td>
        <td><strong>${escapeHtml(g.name)}</strong></td>
        <td>${g.albumCount ?? 0}</td>
        <td>${site}</td>
        <td class="muted">#${g.id_genre ?? "—"}</td>
        <td>
          <button type="button" class="btn btn-danger btn-del" data-id="${g.id_group}">Удалить</button>
        </td>
      </tr>
    `;
  }
  function applyFilters() {
    const q = (wrap.querySelector("#flt-q").value || "").trim().toLowerCase();
    const genre = wrap.querySelector("#flt-genre").value;
    const albums = wrap.querySelector("#flt-albums").value;
    const filtered = groups.filter((g) => {
      if (q) {
        const hay = `${g.name || ""} ${g.site || ""}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      if (genre && String(g.id_genre) !== genre) return false;
      const a = g.albumCount || 0;
      if (albums === "0"    && a !== 0)        return false;
      if (albums === "1-3"  && !(a >= 1 && a <= 3))  return false;
      if (albums === "4-9"  && !(a >= 4 && a <= 9))  return false;
      if (albums === "10"   && !(a >= 10))           return false;
      return true;
    });
    tbody.innerHTML = filtered.length
      ? filtered.map(rowHtml).join("")
      : '<tr><td colspan="6" class="muted" style="text-align:center">Ничего не найдено</td></tr>';
    tbody.querySelectorAll(".btn-del").forEach((btn) => {
      btn.addEventListener("click", async () => {
        if (!confirm("Удалить группу? Это может затронуть связанные концерты.")) return;
        try {
          await Groups.delete(parseInt(btn.dataset.id, 10));
          await renderAdminGroups(paintGen);
        } catch (e) {
          alert("Ошибка: " + e.message);
        }
      });
    });
  }
  wrap.querySelector("#flt-q").addEventListener("input", applyFilters);
  wrap.querySelector("#flt-genre").addEventListener("change", applyFilters);
  wrap.querySelector("#flt-albums").addEventListener("change", applyFilters);
  wrap.querySelector("#flt-reset").addEventListener("click", () => {
    wrap.querySelector("#flt-q").value = "";
    wrap.querySelector("#flt-genre").value = "";
    wrap.querySelector("#flt-albums").value = "";
    applyFilters();
  });
  applyFilters();
  renderLayout(wrap, paintGen);
}

// Вспомогательная функция удаления группы
window.deleteGroup = async (id, gen) => {
  if (!confirm("Удалить группу? Это может затронуть связанные концерты.")) return;
  try {
    await Groups.delete(id);
    await renderAdminGroups(gen);
  } catch (e) {
    alert("Ошибка: " + e.message);
  }
};

  async function route() {
  const paintGen = ++routeGeneration;
  const r = parseRoute();
  const [a, b] = [r.name, r.args[0]];

  // 1. Сначала получаем данные пользователя, чтобы знать его роль
  const user = await loadUser();

  try {
    // 2. Логика для главной страницы (#/ или пустой хэш)
    if (a === "home" || a === "") {
      if (user && user.is_admin) {
        // Если зашел админ — показываем панель управления с 5 кнопками
        await renderAdminHome(paintGen);
      } else {
        // Если гость или обычный юзер — показываем витрину концертов
        await renderHome(paintGen);
      }
    }
    else if (a === "login") {
      renderLogin(paintGen);
    }
    else if (a === "register") {
      renderRegister(paintGen);
    }
    else if (a === "concert" && b) {
      await renderConcertDetail(b, paintGen);
    }
    else if (a === "watchlist") {
      await renderWatchlist(paintGen);
    }
    else if (a === "profile") {
      await renderProfile(paintGen);
    }
    else if ((a === "buy" || a === "seats") && b) {
      await renderSeats(b, paintGen);
    }
    else if (a === "checkout") {
      await renderCheckout(paintGen);
    }
    // 3. Обработка админских подстраниц (ссылки из кнопок панели)
    else if (a === "admin") {
      // Защита: если не админ пытается зайти по прямой ссылке — кидаем на главную
      if (!user || !user.is_admin) {
        navigate("#/");
        return;
      }

      if (b === "concerts") {
        await renderAdminConcerts(paintGen);
      } else if (b === "halls") {
        await renderAdminHalls(paintGen); // Добавьте функцию для залов
      } else if (b === "groups") {
        await renderAdminGroups(paintGen); // Добавьте функцию для групп
      } else if (b === "sales") {
        salesLimit = 10; // Сбрасываем лимит при входе на страницу
        await renderAdminSales(paintGen);
      } else if (b === "add") {
        await renderAdminAdd(paintGen); // Страница добавления/редактирования
      } else {
        await renderAdminHome(paintGen);
      }
    }
    else {
      // Если маршрут не найден — на главную (которая сама выберет роль)
      navigate("#/");
    }
  } catch (e) {
    console.error(e);
    renderLayout(`<div class="error-box">${escapeHtml(e.message)}</div>`, paintGen);
  } finally {
    if (paintGen === routeGeneration) {
      await updateHeaderAuth();
    }
  }
}

  async function updateHeaderAuth() {
    const user = await loadUser();
    const elUser = document.getElementById("nav-user");
    const elAdmin = document.getElementById("nav-admin");
    if (!elUser) return;
    if (user) {
      elUser.textContent = "Выйти";
      elUser.href = "#";
      elUser.onclick = (ev) => {
        ev.preventDefault();
        showConfirmModal(
          "Выход из аккаунта",
          "Вы уверены, что хотите выйти?",
          () => {
            Auth.logout();
            cachedUser = null;
            navigate("#/");
          }
        );
      };
    } else {
      elUser.textContent = "Войти";
      elUser.href = "#/login";
      elUser.onclick = null;
    }
    if (elAdmin) {
      elAdmin.style.display = "none";
    }
  }

  /** Если клик по тому же hash, hashchange не сработает — принудительно перерисуем. */
  document.addEventListener("click", (ev) => {
    const a = ev.target.closest("a[href^='#/']");
    if (!a) return;
    const href = a.getAttribute("href");
    if (!href || href.indexOf("#/") !== 0) return;
    if (location.hash === href) {
      ev.preventDefault();
      route();
    }
  });

  window.addEventListener("hashchange", route);
  document.addEventListener("DOMContentLoaded", () => {
    route();
  });
})();
