document.addEventListener("goBackHome", function () {
    window.location.href = "/";
});

function dateNormalize(dateElement) {
    const today = new Date();
    const year = today.getFullYear();
    let month = today.getMonth() + 1;
    // let day = today.getDate();

    // 日期和月份需要為雙位數
    if (month < 10) {
        month = `0${month}`;
    }
    // if (day < 10) {
    //     day = `0${day}`;
    // }

    // const minDate = `${year}-${month}-${day}`;
    const minDate = `${year}-${month}`;
    dateElement.setAttribute("min", minDate);
}

function loadingState() {
    const loadingGray = "#aabbcc";

    console.log("trigged");

    document.querySelector(
        ".booking-image"
    ).style.background = `rgba(${loadingGray}, 0.5)`;
    document.querySelector(
        ".booking-title"
    ).style.background = `rgba(${loadingGray}, 0.5)`;
    document.querySelector(
        ".booking-subtitle"
    ).style.background = `rgba(${loadingGray}, 0.5)`;

    // document.querySelector(
    //     ".booking-image"
    // ).style.animation = `loading-animation 1.5s infinite alternate`;
    // document.querySelector(
    //     ".booking-title"
    // ).style.animation = `loading-animation 1.5s infinite alternate`;
    // document.querySelector(
    //     ".booking-subtitle"
    // ).style.animation = `loading-animation 1.5s infinite alternate`;
}

function finishLoading() {
    document.querySelector(".booking-image").style.background = `none`;
    document.querySelector(".booking-title").style.background = `none`;
    document.querySelector(".booking-subtitle").style.background = `none`;
    // document.querySelector(".booking-image").style.animation = `none`;
    // document.querySelector(".booking-title").style.animation = `none`;
    // document.querySelector(".booking-subtitle").style.animation = `none`;
}

document.addEventListener("DOMContentLoaded", async function () {
    const token = localStorage.getItem("token");

    loadingState();

    // await checkLoginStatus();

    // async function checkLoginStatus() {
    //     try {
    //         const response = await fetch("/api/user/auth", {
    //             method: "GET",
    //             headers: {
    //                 Authorization: token,
    //             },
    //         });
    //         // .then((response) => response.json())
    //         const data = await response.json();

    //         // .then((data) => {
    //         if (data.data) {
    //             document.querySelector(".booking-user").textContent =
    //                 userData.userName;
    //             await fetchBooking();
    //         } else {
    //             window.location.href = "/";
    //         }
    //         // })
    //         // .catch((error) => console.error("Error:", error));
    //     } catch (error) {
    //         console.error(error);
    //     }
    // }

    let userData = {};

    document.addEventListener("getUserData", async function (event) {
        // format ~ userData = { userName, userId, userEmail };

        userData = event.detail;

        await fetchBooking();

        document.querySelector(".booking-user").textContent = userData.userName;
        document.querySelector("#booking-name").value = userData.userName;
        document.querySelector("#booking-email").value = userData.userEmail;
    });

    async function fetchBooking() {
        try {
            const response = await fetch("/api/booking", {
                method: "GET",
                headers: {
                    Authorization: token,
                },
            });
            // .then((response) => response.json())
            // .then((data) => {
            const data = await response.json();

            if (data.data) {
                finishLoading();

                document.querySelector(".main-division-line").style.display =
                    "flex";

                updateBookingPage(data.data);
            } else {
                document.querySelector(".booking-cube-list").textContent =
                    "目前沒有任何待預訂的行程";
                document.querySelector(".booking-cube-list").style.color =
                    "#666";
                document.querySelector(".main-division-line").style.display =
                    "none";
                document.querySelector(".booking-form").textContent = "";
            }
        } catch (error) {
            console.error("Error:", error);
        }

        function updateBookingPage(data) {
            document.querySelector(".booking-attraction").textContent =
                data.attraction.name;
            document.querySelector(".booking-date").textContent = data.date;
            document.querySelector(".booking-time").textContent = data.time;
            document.querySelector(".booking-fee").textContent = data.price;
            document.querySelector(".booking-place").textContent =
                data.attraction.address;
            document.querySelector(".booking-image").src =
                data.attraction.image;
            document.querySelector(".booking-total-fee").textContent = parseInt(
                data.price
            ); // 更新總價
        }
    }

    const deleteBookingBtn = document.querySelector(".delete-booking");

    deleteBookingBtn.addEventListener("click", async function () {
        try {
            const response = await fetch("/api/booking", {
                method: "DELETE",
                headers: {
                    Authorization: token,
                },
            });
            // .then((response) => response.json())
            // .then((data) => {
            const data = await response.json();

            if (data.ok) {
                window.location.reload();
            } else {
                alert("刪除失敗");
            }
        } catch (error) {
            console.error("Error:", error);
        }
    });

    const dateCredit = document.querySelector("#booking-credit-card-exp");

    dateNormalize(dateCredit);
});
