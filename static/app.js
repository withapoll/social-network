// Минимальный фронтенд для заготовки соцсети.
// Токен авторизации держим в памяти страницы (без localStorage).
let authToken = null;

function showTab(name) {
    ["register", "login", "profile"].forEach((t) => {
        document.getElementById("card-" + t).classList.toggle("hidden", t !== name);
        document.getElementById("tab-" + t).classList.toggle("active", t === name);
    });
}

function setMsg(id, text, ok) {
    const el = document.getElementById(id);
    el.className = "msg " + (ok ? "ok" : "err");
    el.textContent = text;
}

async function register() {
    const body = {
        first_name: document.getElementById("reg-first").value.trim(),
        second_name: document.getElementById("reg-second").value.trim(),
        birthdate: document.getElementById("reg-birth").value,
        gender: document.getElementById("reg-gender").value || null,
        interests: document.getElementById("reg-interests").value.trim() || null,
        city: document.getElementById("reg-city").value.trim() || null,
        password: document.getElementById("reg-password").value,
    };
    try {
        const resp = await fetch("/user/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
        const data = await resp.json();
        if (resp.ok) {
            setMsg("reg-msg", "Готово! Ваш ID: " + data.user_id + ". Используйте его для входа.", true);
        } else {
            setMsg("reg-msg", "Ошибка: " + JSON.stringify(data.detail), false);
        }
    } catch (e) {
        setMsg("reg-msg", "Сетевая ошибка: " + e.message, false);
    }
}

async function login() {
    const body = {
        id: parseInt(document.getElementById("login-id").value, 10),
        password: document.getElementById("login-password").value,
    };
    try {
        const resp = await fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
        const data = await resp.json();
        if (resp.ok) {
            authToken = data.token;
            setMsg("login-msg", "Вход выполнен. Токен сохранён для просмотра анкет.", true);
            document.getElementById("login-token").textContent = "token: " + data.token;
        } else {
            setMsg("login-msg", "Ошибка: " + JSON.stringify(data.detail), false);
        }
    } catch (e) {
        setMsg("login-msg", "Сетевая ошибка: " + e.message, false);
    }
}

const FIELD_LABELS = {
    id: "ID",
    first_name: "Имя",
    second_name: "Фамилия",
    birthdate: "Дата рождения",
    gender: "Пол",
    interests: "Интересы",
    city: "Город",
};

async function loadProfile() {
    const dataEl = document.getElementById("profile-data");
    dataEl.innerHTML = "";
    if (!authToken) {
        setMsg("profile-msg", "Сначала войдите во вкладке «Вход».", false);
        return;
    }
    const id = document.getElementById("profile-id").value;
    try {
        const resp = await fetch("/user/get/" + id, {
            headers: { Authorization: "Bearer " + authToken },
        });
        const data = await resp.json();
        if (resp.ok) {
            setMsg("profile-msg", "", true);
            document.getElementById("profile-msg").textContent = "";
            for (const [key, label] of Object.entries(FIELD_LABELS)) {
                const row = document.createElement("div");
                row.className = "profile-row";
                row.innerHTML = "<span>" + label + "</span><span>" +
                    (data[key] ?? "—") + "</span>";
                dataEl.appendChild(row);
            }
        } else {
            setMsg("profile-msg", "Ошибка: " + JSON.stringify(data.detail), false);
        }
    } catch (e) {
        setMsg("profile-msg", "Сетевая ошибка: " + e.message, false);
    }
}
