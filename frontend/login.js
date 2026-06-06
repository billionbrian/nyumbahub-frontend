document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("loginForm").addEventListener("submit", async function(e) {
        e.preventDefault();

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        console.log("Login attempt for username:", username);

        try {
            const response = await fetch("http://localhost:8000/api/auth/login/", {
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
            console.log("Login response:", data);
            console.log("Response status:", response.status);

            if (response.ok) {
                alert("Login successful!");
                if (data.token) {
                    localStorage.setItem("token", data.token);
                    console.log("Token stored in localStorage");
                } else {
                    console.error("No token in response data");
                }
                if (data.user) {
                    localStorage.setItem("user", JSON.stringify(data.user));
                    console.log("User data stored in localStorage");
                }
                console.log("Login successful:", data);
                console.log("Token in localStorage after login:", localStorage.getItem("token"));
                window.location.href = "index.html";
            } else {
                alert(`Login failed: ${JSON.stringify(data)}`);
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Login failed due to a network error.");
        }
    });
});


            