document.addEventListener("goBackHome", function () {
    window.location.href = "/";
});

document.addEventListener("DOMContentLoaded", async function () {
    document.addEventListener("getUserData", async function (event) {
        // format ~ userData = { userName, userId, userEmail };

        userData = event.detail;
        userId = userData.userId;
        document.querySelector(".user-info").setAttribute("data-user-id", userId);
        document.querySelector(".user-name").textContent = userData.userName;
        document.querySelector(".user-email").textContent = userData.userEmail;

        // const dateCredit = document.querySelector("#booking-credit-card-exp");
        // dateNormalize(dateCredit);
        console.log("getUserData");
    });

    const memberLogout = document.querySelector("#member-logout");


    memberLogout.addEventListener("click", function () {
        if (localStorage.getItem("token")) {
            // window.open(window.location.origin + "/member", "_self");
            localStorage.removeItem("token");
            const openLoginBtn = document.querySelector("#open-login");

            console.log(openLoginBtn);

            openLoginBtn.textContent = "登入/註冊";
        } else {
            //回到首頁
            window.open(window.location.origin + "/", "_self");
        }
    });

});