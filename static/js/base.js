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

    showRegister.addEventListener("click", function () {
        loginForm.style.display = "none";
        registerForm.style.display = "flex";
        loginError.textContent = "";
    });

    showLogin.addEventListener("click", function () {
        loginForm.style.display = "flex";
        registerForm.style.display = "none";
        registerError.textContent = "";
    });

    closeModal.addEventListener("click", function () {
        closeModalChange();
    });
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" || event.keyCode === 27) {
            closeModalChange();
        }
    });

    function closeModalChange() {
        modal.style.display = "none";

        // 清空登入表單
        document.querySelector("#login-email").value = "";
        document.querySelector("#login-password").value = "";
        loginError.textContent = "";
        //改為預設值
        loginForm.style.display = "flex";

        // 清空註冊表單
        document.querySelector("#register-name").value = "";
        document.querySelector("#register-email").value = "";
        document.querySelector("#register-password").value = "";
        registerError.textContent = "";
        //改為預設值
        registerError.style.color = "rgb(235, 71, 71)";
        registerForm.style.display = "none";
    }

    const bookingTrip = document.querySelector("#booking-trip");

    bookingTrip.addEventListener("click", async function () {
        if (!localStorage.getItem("token")) {
            modal.style.display = "flex";
        } else {
            const response = await fetch("/api/user/auth", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `${localStorage.getItem("token")}`,
                },
            });

            const responseData = await response.json();

            if (responseData.data !== null) {
                window.open(window.location.origin + "/booking", "_self");
            } else {
                modal.style.display = "flex";
            }
        }
    });

    loginForm.addEventListener("submit", function (event) {
        event.preventDefault();
        //  Ajax?
        const email = document.querySelector("#login-email").value.trim();
        const password = document.querySelector("#login-password").value.trim();

        if (!email || !password) {
            loginError.textContent = "請填寫所有必填欄位";
            return;
        }

        // 發送 API 請求
        fetch("/api/user/auth", {
            method: "PUT",
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
        const name = document.querySelector("#register-name").value.trim();
        const email = document.querySelector("#register-email").value.trim();
        const password = document
            .querySelector("#register-password")
            .value.trim();

        if (!name || !email || !password) {
            registerError.textContent = "請填寫所有必填欄位";
            registerError.style.color = "rgb(235, 71, 71)";
            return;
        }

        // 密碼格式檢查
        const passwordRegex =
            /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])[A-Za-z\d@$!%*?&]{8,}$/;
        if (!passwordRegex.test(password)) {
            registerError.textContent =
                "密碼必須包含大小寫英文、數字、特殊符號，且最少八碼";
            registerError.style.color = "rgb(235, 71, 71)";
            return;
        }
        // ^ 和 $：這兩個符號分別表示字串的開始和結束。
        // (?=.*[a-z])：這是一個前瞻（lookahead）斷言，用於檢查字串中是否至少有一個小寫字母。
        // (?=.*[A-Z])：另一個前瞻斷言，檢查是否至少有一個大寫字母。
        // (?=.*[!@#$%^&*(),.?":{}|<>])：再一個前瞻斷言，檢查是否至少有一個特殊字符。
        // [A-Za-z\d@$!%*?&]{8,}：這部分檢查整個字串是否由上述定義的字符組成，並且長度至少為8。
        // (?=.*\d): 加入了一個前瞻斷言，檢查是否至少有一個數字

        // 信箱格式檢查
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailRegex.test(email)) {
            registerError.textContent = "請輸入有效的信箱地址";
            registerError.style.color = "rgb(235, 71, 71)";
            return;
        }
        //         ^ 和 $：同上，表示字串的開始和結束。
        // [a-zA-Z0-9._%+-]+：這部分匹配信箱地址的使用者名稱部分，它可以包含字母、數字以及一些特殊字符（如.、_、%、+、-）。
        // @：這是信箱地址中必須有的符號。
        // [a-zA-Z0-9.-]+：這部分匹配信箱的域名部分（在@之後），可以包含字母、數字和一些特殊字符（如. 和 -）。
        // \.[a-zA-Z]{2,}：最後這部分檢查頂級域名（如 .com、.org 等），它應該是由至少兩個字母組成。

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
                    registerError.style.color = "#448899";
                    registerError.textContent = "註冊成功";
                } else {
                    // console.log(data.message);
                    registerError.style.color = "rgb(235, 71, 71)";
                    registerError.textContent = data.message || "註冊失敗";
                }
            });
    });

    // window.addEventListener("beforeunload", function (event) {
    // 在頁面即將卸載前清空表單和錯誤訊息
    // });

    checkLoginStatus();

    function checkLoginStatus() {
        fetch("/api/user/auth", {
            method: "GET",
            headers: {
                Authorization: `${localStorage.getItem("token")}`,
            },
        })
            .then((response) => response.json())
            .then((data) => {
                if (data && data.data) {
                    userName = data.data.name;
                    userId = data.data.id;
                    userEmail = data.data.email;

                    const event = new CustomEvent("getUserData", {
                        detail: {
                            userName,
                            userId,
                            userEmail,
                        },
                    });
                    document.dispatchEvent(event);

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
