document.addEventListener("DOMContentLoaded", () => {
    const signupForm = document.getElementById("signupForm");
    const alertBox = document.getElementById("authAlert");
    const submitBtn = document.getElementById("signupSubmitBtn");

    function showAuthMessage(message, type = "error") {
        if (alertBox) {
            alertBox.className = `auth-alert ${type}`;
            alertBox.textContent = message;
            alertBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
        } else {
            alert(message);
        }
    }

    if (!signupForm) return;

    signupForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const username = document.getElementById("username").value.trim();
        const name = document.getElementById("name").value.trim();
        const email = document.getElementById("email").value.trim();
        const phone = document.getElementById("phone").value.trim();
        const role = document.getElementById("role").value;
        const password = document.getElementById("password").value;
        const confirmPassword = document.getElementById("confirmPassword").value;

        if (!username || !name || !email || !phone || !role || !password) {
            showAuthMessage("Please fill in all required fields.", "error");
            return;
        }

        if (password !== confirmPassword) {
            showAuthMessage("Passwords do not match. Please double-check your password.", "error");
            return;
        }

        const originalBtnHTML = submitBtn ? submitBtn.innerHTML : "";
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = "<span>Creating your account...</span>";
        }
        if (alertBox) {
            alertBox.className = "auth-alert";
            alertBox.textContent = "";
        }

        try {
            const apiBase = (window.location.protocol.startsWith('http') && !['5500', '3000', '5173'].includes(window.location.port))
                ? window.location.origin
                : 'http://localhost:8080';

            const response = await fetch(`${apiBase}/api/auth/signup/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    username,
                    name,
                    email,
                    phone,
                    role,
                    password,
                }),
            });

            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                const data = await response.json();

                if (response.ok) {
                    showAuthMessage("Account created successfully! Redirecting to Sign In...", "success");
                    setTimeout(() => {
                        window.location.href = "login.html";
                    }, 700);
                } else {
                    const errMsg =
                        data.detail ||
                        data.error ||
                        (typeof data === "object" ? Object.values(data).flat().join(" ") : "Registration failed.");
                    showAuthMessage(errMsg || "Could not create account. Please check your details.", "error");
                }
            } else {
                showAuthMessage(`Server error (Status ${response.status}). Check Django server logs for details.`, "error");
            }
        } catch (error) {
            console.error("Error:", error);
            showAuthMessage("Unable to connect to the server. Make sure the backend is running (e.g. on port 8080).", "error");
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnHTML;
            }
        }
    });
});
