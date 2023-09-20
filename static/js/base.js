document.addEventListener("DOMContentLoaded", function () {
    const closeModal = document.getElementById("close-modal");
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const showRegister = document.getElementById("show-register");
    const showLogin = document.getElementById("show-login");
    const loginError = document.getElementById("login-error");
    const registerError = document.getElementById("register-error");

    const modal = document.getElementById("modal");
    const openLoginBtn = document.getElementById("open-login");

    if (localStorage.getItem("token")) {
        openLoginBtn.textContent = "登出系統";
    } else {
        openLoginBtn.textContent = "登入/註冊";
    }

    openLoginBtn.addEventListener("click", function () {
        if (localStorage.getItem("token")) {
            localStorage.removeItem("token");
            openLoginBtn.textContent = "登入/註冊";
        } else {
            modal.style.display = "flex";
        }
    });

    closeModal.addEventListener("click", function () {
        modal.style.display = "none";
    });

    showRegister.addEventListener("click", function () {
        loginForm.style.display = "none";
        registerForm.style.display = "flex";
    });

    showLogin.addEventListener("click", function () {
        loginForm.style.display = "flex";
        registerForm.style.display = "none";
    });

    loginForm.addEventListener("submit", function (event) {
        event.preventDefault();
        //  Ajax?
        const email = document.querySelector(
            "#login-form input[type='text']"
        ).value;
        const password = document.querySelector(
            "#login-form input[type='password']"
        ).value;

        // 發送 API 請求
        fetch("/api/user/auth", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ email, password }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.token) {
                    // 將 token 存到 localStorage
                    localStorage.setItem("token", data.token);

                    // modal.style.display = "none";
                    // openLoginBtn.textContent = "登出";

                    loginError.textContent = ""; // 清空錯誤訊息
                    location.reload(); // 重新載入頁面
                } else {
                    // console.log(data.message);
                    loginError.textContent = data.message || "登入失敗";
                }
            });
    });

    registerForm.addEventListener("submit", function (event) {
        event.preventDefault();
        //  Ajax
        const name = document.querySelector("#register-name").value;
        const email = document.querySelector("#register-email").value;
        const password = document.querySelector("#register-password").value;

        fetch("/api/user", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ name, email, password }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.ok) {
                    registerError.textContent = "註冊成功";
                } else {
                    // console.log(data.message);
                    registerError.textContent = data.message || "註冊失敗";
                }
            });
    });

    checkLoginStatus();

    function checkLoginStatus() {
        console.log("checking");

        fetch("/api/user/auth", {
            method: "GET",
            headers: {
                Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
        })
            .then((response) => response.json())
            .then((data) => {
                console.log(data);

                if (data && data.data) {
                    openLoginBtn.textContent = "登出系統";
                } else {
                    openLoginBtn.textContent = "登入/註冊";
                }
            })
            .catch((error) => {
                // console.error("Error:", error);
                openLoginBtn.textContent = "登入/註冊";
            });
    }
});
