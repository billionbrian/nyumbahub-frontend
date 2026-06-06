document.addEventListener("DOMContentLoaded", () => {
    const signupForm = document.getElementById("signupForm");

    if (signupForm) {
        signupForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const username = document.getElementById("username").value;
            const name = document.getElementById("name").value;
            const email = document.getElementById("email").value;
            const phone = document.getElementById("phone").value;
            const role = document.getElementById("role").value;
            const password = document.getElementById("password").value;
            const confirmPassword = document.getElementById("confirmPassword").value;

            if (password !== confirmPassword) {
                alert("Passwords do not match!");
                return;
            }

            console.log("Sending signup data:", { username, name, email, phone, role });

            try {
                console.log("Attempting to connect to: http://localhost:8000/api/auth/signup/");
                const response = await fetch("http://localhost:8000/api/auth/signup/", {
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

                console.log("Response status:", response.status);
                
                // Check if response is JSON or HTML
                const contentType = response.headers.get("content-type");
                console.log("Content-Type:", contentType);
                
                if (contentType && contentType.includes("application/json")) {
                    const data = await response.json();
                    console.log("Signup response:", data);

                    if (response.ok) {
                        alert("Signup successful!");
                        window.location.href = "login.html";
                    } else {
                        alert(`Signup failed: ${JSON.stringify(data)}`);
                    }
                } else {
                    // Handle HTML error response
                    const text = await response.text();
                    console.error("Server returned HTML instead of JSON:", text.substring(0, 200));
                    alert(`Server error (Status ${response.status}). Check Django server logs for details.`);
                }
            } catch (error) {
                console.error("Error:", error);
                alert(`Signup failed: ${error.message}\n\nMake sure Django server is running on http://localhost:8000`);
            }
        });
    } else {
        console.error("Signup form not found in the HTML.");
    }
});
    

















