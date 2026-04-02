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

  const { Auth, Concerts, Halls, Sales, Watchlist, Admin, getToken } = TicketshopApi;

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
    let err = "";
    try {
      const pageSize = 50;
      let offset = 0;
      while (paintGen === routeGeneration) {
        const page = await Concerts.list(pageSize, offset);
        if (!Array.isArray(page) || page.length === 0) break;
        concerts.push(...page);
        if (page.length < pageSize) break;
        offset += pageSize;
      }
    } catch (e) {
      err = e.message || String(e);
    }

    if (paintGen !== routeGeneration) return;

    const wrap = el(`<div class="hero"></div>`);
    // На некоторых случаях (кэш/другая разметка) querySelector может вернуть null.
    // Тогда используем сам корневой элемент.
    const hero = wrap.querySelector(".hero") || wrap;
    hero.innerHTML = `<h1>Мероприятия</h1>
    <p class="muted">Выберите концерт и купите билет онлайн.</p>`;
    if (err) wrap.appendChild(el(`<div class="error-box">${escapeHtml(err)}</div>`));
    const grid = el('<div class="grid cols-2"></div>');
    if (!concerts.length && !err) {
      grid.appendChild(el('<p class="empty">Пока нет опубликованных мероприятий.</p>'));
    }
    concerts.forEach((c) => {
      const paused = c.sales_paused ? '<span class="badge warn">Продажи приостановлены</span>' : "";
      const card = el(`<article class="card clickable">
      <div class="card-title">${escapeHtml(c.name)}</div>
      <div class="muted">${formatDate(c.date)}</div>
      <div style="margin-top:0.5rem">${paused}</div>
    </article>`);
      card.addEventListener("click", () => navigate("#/concert/" + c.id_concert));
      grid.appendChild(card);
    });
    wrap.appendChild(grid);
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

    const desc = c.description
      ? `<p>${escapeHtml(c.description).replace(/\n/g, "<br>")}</p>`
      : '<p class="muted">Описание пока не указано.</p>';
    const paused = c.sales_paused
      ? '<p><span class="badge warn">Продажи билетов остановлены администратором</span></p>'
      : "";
    wrap.innerHTML = `
    <h1>${escapeHtml(c.name)}</h1>
    <p class="muted">${formatDate(c.date)}</p>
    ${paused}
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

  async function renderBuy(concertId, paintGen) {
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
        `<div class="error-box">Продажи на это мероприятие приостановлены.</div><p><a href="#/concert/${concertId}">← Назад</a></p>`,
        paintGen
      );
      return;
    }
    const wrap = el("<div></div>");
    wrap.innerHTML = `
    <h1>Покупка билета</h1>
    <p class="muted">${escapeHtml(c.name)} · ${formatDate(c.date)}</p>
    <form id="buy-form">
      <div class="form-row">
        <label>Тип билета / зона</label>
        <select name="ticket_type" required></select>
      </div>
      <div class="form-row">
        <label>Количество</label>
        <input name="count" type="number" min="1" value="1" required>
      </div>
      <button type="submit" class="btn btn-primary">Оплатить (оформить заказ)</button>
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
        opt.dataset.remains = String(o.remains);
        sel.appendChild(opt);
      });
    }
    wrap.querySelector("#buy-form").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(ev.target);
      const idType = parseInt(fd.get("ticket_type"), 10);
      const count = parseInt(fd.get("count"), 10);
      if (!idType) return;
      try {
        await Sales.buy({
          id_concert: parseInt(concertId, 10),
          id_ticket_type: idType,
          count,
        });
        alert("Покупка оформлена!");
        navigate("#/profile");
      } catch (e) {
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
    const user = await loadUser();
    if (paintGen !== routeGeneration) return;

    if (!user || !user.is_admin) {
      renderLayout('<div class="error-box">Нужны права администратора.</div>', paintGen);
      return;
    }
    renderLayout(
      `
    <h1>Админ-панель</h1>
    <p class="muted">Управление концертами и просмотр продаж.</p>
    <ul>
      <li><a href="#/admin/concerts">Концерты — добавить, редактировать, остановить продажи</a></li>
      <li><a href="#/admin/sales">Недавние покупки</a></li>
    </ul>
    <p><a href="#/">← На сайт</a></p>
  `,
      paintGen
    );
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

    const hallOpts = halls.map((h) => `<option value="${h.id_hall}">${escapeHtml(h.name)}</option>`).join("");
    const rows = concerts
      .map(
        (c) => `
    <tr data-id="${c.id_concert}">
      <td>${escapeHtml(c.name)}</td>
      <td>${formatDate(c.date)}</td>
      <td>${c.sales_paused ? '<span class="badge warn">Стоп</span>' : '<span class="badge ok">Ок</span>'}</td>
      <td>
        <button type="button" class="btn btn-ghost btn-edit" data-id="${c.id_concert}">Изменить</button>
        <button type="button" class="btn btn-danger btn-del" data-id="${c.id_concert}">Удалить</button>
      </td>
    </tr>`
      )
      .join("");

    const wrap = el("<div></div>");
    wrap.innerHTML = `
    <h1>Концерты (админ)</h1>
    <h2>Новый концерт</h2>
    <form id="new-concert" class="card" style="margin-bottom:2rem">
      <div class="form-row"><label>Название</label><input name="name" required></div>
      <div class="form-row"><label>Дата и время</label><input name="date" type="datetime-local" required></div>
      <div class="form-row"><label>Зал</label><select name="id_hall" required>${hallOpts}</select></div>
      <div class="form-row"><label>Описание</label><textarea name="description"></textarea></div>
      <div class="form-row"><label><input type="checkbox" name="sales_paused"> Продажи остановлены</label></div>
      <button type="submit" class="btn btn-primary">Создать</button>
    </form>
    <div class="table-wrap">
      <table><thead><tr><th>Название</th><th>Дата</th><th>Продажи</th><th></th></tr></thead>
      <tbody id="admin-concerts-body">${rows}</tbody></table>
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
        <div class="form-row"><label><input type="checkbox" name="sales_paused"> Продажи остановлены</label></div>
        <div class="actions">
          <button type="submit" class="btn btn-primary">Сохранить</button>
          <button type="button" class="btn btn-ghost" id="edit-cancel">Отмена</button>
        </div>
      </form>
    </dialog>
  `;

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

    wrap.querySelectorAll(".btn-edit").forEach((btn) => {
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

    wrap.querySelectorAll(".btn-del").forEach((btn) => {
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

    renderLayout(wrap, paintGen);
  }

  async function renderAdminSales(paintGen) {
    const user = await loadUser();
    if (paintGen !== routeGeneration) return;

    if (!user || !user.is_admin) {
      renderLayout('<div class="error-box">Нужны права администратора.</div>', paintGen);
      return;
    }
    let sales = [];
    try {
      sales = await Admin.recentSales(80);
    } catch (e) {
      renderLayout(`<div class="error-box">${escapeHtml(e.message)}</div>`, paintGen);
      return;
    }
    if (paintGen !== routeGeneration) return;

    const rows = sales
      .map(
        (s) => `
    <tr>
      <td>${formatDate(s.sale_date)}</td>
      <td>${escapeHtml(s.user_email)}</td>
      <td>${escapeHtml(s.concert_name || "—")}</td>
      <td>${s.count}</td>
      <td>${s.total_price} ₽</td>
    </tr>`
      )
      .join("");
    renderLayout(
      `
    <h1>Недавние покупки</h1>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Дата</th><th>Пользователь</th><th>Концерт</th><th>Билетов</th><th>Сумма</th></tr></thead>
        <tbody>${rows || '<tr><td colspan="5" class="muted">Нет данных</td></tr>'}</tbody>
      </table>
    </div>
    <p><a href="#/admin">← Админ</a></p>
  `,
      paintGen
    );
  }

  async function route() {
    const paintGen = ++routeGeneration;
    const r = parseRoute();
    const [a, b] = [r.name, r.args[0]];
    try {
      if (a === "home" || a === "") {
        await renderHome(paintGen);
      } else if (a === "login") {
        renderLogin(paintGen);
      } else if (a === "register") {
        renderRegister(paintGen);
      } else if (a === "concert" && b) {
        await renderConcertDetail(b, paintGen);
      } else if (a === "watchlist") {
        await renderWatchlist(paintGen);
      } else if (a === "profile") {
        await renderProfile(paintGen);
      } else if (a === "buy" && b) {
        await renderBuy(b, paintGen);
      } else if (a === "admin") {
        if (!b) await renderAdminHome(paintGen);
        else if (b === "concerts") await renderAdminConcerts(paintGen);
        else if (b === "sales") await renderAdminSales(paintGen);
        else await renderAdminHome(paintGen);
      } else {
        await renderHome(paintGen);
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
        Auth.logout();
        cachedUser = null;
        navigate("#/");
      };
    } else {
      elUser.textContent = "Войти";
      elUser.href = "#/login";
      elUser.onclick = null;
    }
    if (elAdmin) {
      elAdmin.style.display = user && user.is_admin ? "inline" : "none";
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
