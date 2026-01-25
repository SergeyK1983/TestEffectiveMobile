document.addEventListener("DOMContentLoaded", () => {
    const loginBtn = document.getElementById("login-button");
    const overlay = document.getElementById("login-overlay");
    const form = document.getElementById("login-form");
    const submitBtn = document.getElementById("login-submit");
    const errorBox = document.getElementById("login-error");

    loginBtn.addEventListener("click", () => {
        overlay.classList.remove("hidden");
        errorBox.classList.add("hidden");
    });

    // закрытие по клику вне формы
    overlay.addEventListener("click", () => {
        overlay.classList.add("hidden");
    });

    // чтобы клик по форме не закрывал окно
    form.addEventListener("click", (e) => {
        e.stopPropagation();
    });

    submitBtn.addEventListener("click", async () => {
        errorBox.classList.add("hidden");

        const payload = {
            username: document.getElementById("username").value || null,
            email: document.getElementById("email").value || null,
            password: document.getElementById("password").value
        };

        try {
            const response = await fetch("/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) {
                const data = await response.json();
                showError(parseBackendError(data));
                return;
            }
            const accessToken = response.headers.get("access_token");
            const refreshToken = response.headers.get("refresh_token");

            if (!accessToken || !refreshToken) {
                showError("Токены не получены от сервера");
                return;
            }

            saveTokens(accessToken, refreshToken);

            console.log("Успешный вход", data);
            overlay.classList.add("hidden");

        } catch (err) {
            showError("Ошибка соединения с сервером");
        }
    });

    function showError(message) {
        errorBox.textContent = message;
        errorBox.classList.remove("hidden");
    }

    function parseBackendError(data) {
        // FastAPI validation error (422)
        if (data.detail) {
            if (Array.isArray(data.detail)) {
                return data.detail.map(e => e.msg).join(", ");
            }
            return data.detail;
        }
        return "Ошибка авторизации";
    }

    function saveTokens(accessToken, refreshToken) {
        localStorage.setItem("access_token", accessToken);
        localStorage.setItem("refresh_token", refreshToken);
    }
});
