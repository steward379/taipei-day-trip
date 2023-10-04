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

document.addEventListener("DOMContentLoaded", async function () {
    const token = localStorage.getItem("token");

    let userData = {};

    document.addEventListener("getUserData", async function (event) {
        // format ~ userData = { userName, userId, userEmail };

        userData = event.detail;
        document.querySelector(".booking-user").textContent = userData.userName;
        document.querySelector("#booking-name").value = userData.userName;
        document.querySelector("#booking-email").value = userData.userEmail;

        // const dateCredit = document.querySelector("#booking-credit-card-exp");
        // dateNormalize(dateCredit);

        await fetchBooking();
    });

    TPDirect.setupSDK(appId, appKey, "sandbox");

    TPDirect.card.setup({
        fields: {
            number: {
                element: "#card-number",
                placeholder: "**** **** **** ****",
            },
            expirationDate: {
                element: "#card-expiration-date",
                placeholder: "MM / YY",
            },
            ccv: {
                element: "#card-ccv",
                placeholder: "ccv",
            },
        },
        styles: {
            ":focus": {
                "color": "black",
            },
            // style valid state
            ".valid": {
                "color" : "rgb(41, 145, 92)",
            },
            // style invalid state
            ".invalid": {
                "color" : "rgb(226, 75, 75)",
            },
        },
        // 此設定會顯示卡號輸入正確後，會顯示前六後四碼信用卡卡號
        isMaskCreditCardNumber: true,
        maskCreditCardNumberRange: {
            beginIndex: 6,
            endIndex: 11,
        },
    });

    const confirmBooking = document.querySelector("#confirm-booking");

    confirmBooking.addEventListener("click", function (event) {
        event.preventDefault();

        // const tappayStatus = TPDirect.card.getTappayFieldsStatus();

        // if (tappayStatus.canGetPrime === false) {
        //     alert("can not get prime");
        //     return;
        // }

        TPDirect.card.getPrime(async (result) => {
            if (result.status !== 0) {
                alert("get prime error " + result.msg);
                return;
            }
            
            const prime = result.card.prime;


            const trip = Array.from(document.querySelectorAll(".booking-details")).map((detail, index) => {
                return {
                    bookingId: detail.getAttribute("data-id"),
                    attraction: {
                        id: detail.querySelector(".booking-attraction").getAttribute("data-id"),
                        name: detail.querySelector(".booking-attraction").textContent,
                        address: detail.querySelector(".booking-place").textContent,
                        image: document.querySelectorAll(".booking-image")[index].src,  // 使用索引來匹配相應的圖片
                    },
                    date: detail.querySelector(".booking-date").textContent,
                    time: detail.querySelector(".booking-time").textContent,
                };
            });

            
            const requestData = {
                prime: prime,
                order: {
                    // id : document.querySelector(".booking-details").getAttribute("data-id"),
                    price: document.querySelector(".booking-total-fee")
                        .textContent,
                    trips: trip,
                        // attraction: {
                        //     id: document
                        //         .querySelector(".booking-attraction")
                        //         .getAttribute("data-id"),
                        //     name: document.querySelector(".booking-attraction")
                        //         .textContent,
                        //     address:
                        //         document.querySelector(".booking-place")
                        //             .textContent,
                        //     image: document.querySelector(".booking-image").src,
                        // },
                        // date: document.querySelector(".booking-date")
                        //     .textContent,
                        // time: document.querySelector(".booking-time")
                        //     .textContent,
                    contact: {
                        name: document.querySelector("#booking-name").value,
                        email: document.querySelector("#booking-email").value,
                        phone: document.querySelector("#booking-phone").value,
                    },
                },
            };

            console.log(requestData);

            try {
                const response = await fetch("/api/orders", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: token,
                    },
                    body: JSON.stringify(requestData),
                });

                const data = await response.json();

                if (data.data && data.data.payment.status === 0) {
                    alert("付款成功");
                    console.log(data.data.number);
                    window.open(window.location.origin + `/thankyou?number=${data.data.number}`, "_self");
                } else {
                    alert("付款失敗：" + data.message);
                }
            } catch (error) {
                console.error("錯誤:", error);
                alert("付款失敗");
            }
        });

        // send prime to your server, to pay with Pay by Prime API .
        // Pay By Prime Docs: https://docs.tappaysdk.com/tutorial/zh/back.html#pay-by-prime-api
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
    }

    function updateBookingPage(bookings) {
        let totalFee = 0;
        const bookingList = document.querySelector(".booking-cube-list");
        bookingList.innerHTML = "";

        bookings.forEach((booking) => {
            totalFee += parseInt(booking.price);
            const bookingCube = document.createElement("div");
            bookingCube.classList.add("booking-cube");

            bookingCube.innerHTML = `
                    <a href="/attraction/${booking.attraction.id}">
                    <img class="booking-image" src="${booking.attraction.image}" alt="" width="266px" height="200px">
                    </a>
                    <div class="booking-details" data-id="${booking.id}">
                        <h3 class="booking-title">台北一日遊： <span class="booking-attraction" data-id="${booking.attraction.id}">${booking.attraction.name}</span></h3>
                        <h5 class="booking-subtitle"> <span class="booking-subtitle-bold">日期：</span><span class="booking-date">${booking.date}</span></h5>
                        <h5 class="booking-subtitle"> <span class="booking-subtitle-bold">時間：</span><span class="booking-time">${booking.time}</span></h5>
                        <h5 class="booking-subtitle"> <span class="booking-subtitle-bold">費用：</span><span class="booking-fee">${booking.price}</span></h5>
                        <h5 class="booking-subtitle"> <span class="booking-subtitle-bold">地點：</span><span class="booking-place">${booking.attraction.address}</span></h5>
                    </div>
                    <div class="delete-booking delete-booking-normal" id="delete-booking">
                        <img src="../static/images/rubbish_bin.png" alt="delete" width="30px" height="30px">
                    </div>
                `;

            // bookingCube.setAttribute("data-id", booking.id);
            // bookingCube.setAttribute(
            //     "data-attraction-id",
            //     booking.attraction.id
            // );

            // const currentBookingCube = bookingCube;
            const currentBookingId = booking.id;
            const currentAttractionId = booking.attraction.id;

            const deleteBookingBtn =
                bookingCube.querySelector(".delete-booking");

            deleteBookingBtn.addEventListener("click", async function () {
                // const bookingId = bookingCube.getAttribute("data-id");
                // const bookAttractionId =
                //     bookingCube.getAttribute("data-attraction-id");

                try {
                    const response = await fetch(
                        `/api/booking/${currentBookingId}`,
                        {
                            method: "DELETE",
                            headers: {
                                Authorization: token,
                            },
                        }
                    );
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

            bookingList.appendChild(bookingCube);

            document.querySelector(".booking-total-fee").textContent = totalFee;
        });

        // document.querySelector(".booking-attraction").textContent =
        //     data.attraction.name;
        // document.querySelector(".booking-date").textContent = data.date;
        // document.querySelector(".booking-time").textContent = data.time;
        // document.querySelector(".booking-fee").textContent = data.price;
        // document.querySelector(".booking-place").textContent =
        //     data.attraction.address;
        // document.querySelector(".booking-image").src =
        //     data.attraction.image;
        // document.querySelector(".booking-total-fee").textContent = parseInt(
        //     data.price
        // ); // 更新總價
    }
});

