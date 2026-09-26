document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");
    const alertBox = document.getElementById("authAlert");
    const submitBtn = document.getElementById("loginSubmitBtn");

    function showAuthMessage(message, type = "error") {
        if (alertBox) {
            alertBox.className = `auth-alert ${type}`;
            alertBox.textContent = message;
        } else {
            alert(message);
        }
    }

    if (!loginForm) return;

    loginForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value;

        if (!username || !password) {
            showAuthMessage("Please enter both your username and password.", "error");
            return;
        }

        const originalBtnHTML = submitBtn ? submitBtn.innerHTML : "";
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = "<span>Signing in...</span>";
        }
        if (alertBox) {
            alertBox.className = "auth-alert";
            alertBox.textContent = "";
        }

        try {
            const apiBase = (window.location.protocol.startsWith('http') && !['5500', '3000', '5173'].includes(window.location.port))
                ? window.location.origin
                : 'http://localhost:8080';

            const response = await fetch(`${apiBase}/api/auth/login/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    username,
                    password,
                }),
            });

            const data = await response.json();

            if (response.ok) {
                if (data.token) {
                    localStorage.setItem("token", data.token);
                }
                if (data.user) {
                    localStorage.setItem("user", JSON.stringify(data.user));
                }
                showAuthMessage("Signed in successfully! Redirecting...", "success");
                setTimeout(() => {
                    window.location.href = "index.html";
                }, 500);
            } else {
                const errMsg =
                    data.detail ||
                    data.error ||
                    (typeof data === "object" ? Object.values(data).flat().join(" ") : "Invalid credentials.");
                showAuthMessage(errMsg || "Login failed. Please check your credentials.", "error");
            }
        } catch (error) {
            console.error("Error:", error);
            showAuthMessage("Unable to reach the server. Make sure the backend is running (e.g. on port 8080).", "error");
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnHTML;
            }
        }
    });
});