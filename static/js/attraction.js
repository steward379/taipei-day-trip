const domainURL = `http://127.0.0.1:`;
// const domainURL = `http://54.253.20.174:`;
const port = `3000`;

let isRadioChanged = false; // 用來追踪是否有改變選項

function getAttractionIdFromURL() {
    const pathQuery = window.location.pathname.split("/");
    const lastQuery = pathQuery[pathQuery.length - 1];
    // const url = window.location.href;
    // const attractionId = url.split("/").pop();

    if (/^[0-9]+$/.test(lastQuery)) {
        return lastQuery;
    } else {
        return null;
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    const attraction_id = getAttractionIdFromURL();

    if (attraction_id) await initialize(attraction_id);
});

async function initialize(id) {
    // let formatAPIurl = `${domainURL}${port}/api/attraction/${id}`; // CORS
    let formatAPIurl = `/api/attraction/${id}`;

    try {
        const response = await fetch(formatAPIurl);
        const dataAttractionsPrimitive = await response.json();
        const dataAttractions = dataAttractionsPrimitive["data"];

        if (dataAttractions) {
            // createElements(dataAttractions);

            const attractionName = document.querySelector(".attraction-name");
            const attractionMrt = document.querySelector(".attraction-mrt");
            const attractionCategory = document.querySelector(
                ".attraction-category"
            );
            const attractionDescription = document.querySelector(
                ".attraction-description"
            );

            const attractionAddress = document.querySelector(
                ".attraction-address"
            );
            const attractionTransport = document.querySelector(
                ".attraction-transport"
            );
            const attractionImages = document.querySelector(".images-wrapper");

            attractionName.textContent = dataAttractions["name"];
            attractionCategory.textContent = dataAttractions["category"];
            attractionDescription.textContent = dataAttractions["description"];
            attractionAddress.textContent = dataAttractions["address"];
            attractionMrt.textContent = dataAttractions["mrt"];
            attractionTransport.textContent = dataAttractions["transport"];

            const feeElement = document.getElementById("photo-fee");
            const morningRadio = document.getElementById("morning");
            const afternoonRadio = document.getElementById("afternoon");
            const dateElement = document.getElementById("photo-date");

            dateNormalize(dateElement);

            morningRadio.addEventListener("change", function () {
                feeElement.textContent = "新台幣 2000 元";
            });

            afternoonRadio.addEventListener("change", function () {
                feeElement.textContent = "新台幣 2500 元";
            });

            document
                .querySelectorAll('input[name="photo-radio"]')
                .forEach((input) => {
                    input.addEventListener("click", function () {
                        isRadioChanged = true; // 當有改變時，將 isChanged 設為 true
                        console.log("changeRadio");
                    });
                });

            const photoSubmit =
                document.getElementsByClassName("photo-submit")[0];

            photoSubmit.onclick = function (event) {
                event.preventDefault();

                checkUserLoggedIn();
                SendBookingData(
                    id,
                    dateElement,
                    feeElement,
                    morningRadio,
                    afternoonRadio
                );
                // window.open(window.location.origin + "/booking", "_self");
            };

            for (let i = 0; i < dataAttractions["images"].length; i++) {
                const img = document.createElement("img");

                img.src = dataAttractions["images"][i];

                img.alt = `attraction image ${dataAttractions["name"]} - ${
                    i + 1
                }`;
                img.className = `attraction-image attraction-image-${i + 1}`;
                attractionImages.appendChild(img);
            }

            for (let i = 0; i < dataAttractions["images"].length; i++) {
                const dotDiv = document.createElement("div");
                dotDiv.className = `img-nav-button-${i + 1} img-nav-button`;

                const dotWrapper = document.querySelector(
                    ".dot-button-wrapper"
                );
                dotWrapper.appendChild(dotDiv);
            }

            const dotFirstDiv = document.querySelector(".img-nav-button-1");
            dotFirstDiv.classList.add("img-nav-button-active");

            const imageCount = dataAttractions["images"].length;

            arrowMotion(imageCount);

            // 讀取先前暫存的資料，並填入表單，這樣登入後就不用重來
            if (localStorage.getItem("formData")) {
                const savedFormData = JSON.parse(
                    localStorage.getItem("formData")
                );

                // 檢查儲存的日期是否早於今天
                const today = new Date();
                const savedDate = new Date(savedFormData.date);
                if (savedDate >= today) {
                    document.getElementById("photo-date").value =
                        savedFormData.date;
                }

                document.querySelector(
                    `input[name="photo-radio"][value="${savedFormData.time}"]`
                ).checked = true;

                // 刪除儲存的表單資料
                localStorage.removeItem("formData");
            }
        }

        // DOM
    } catch (error) {
        console.log(error);
    }
}

function dateNormalize(dateElement) {
    const today = new Date();
    const year = today.getFullYear();
    let month = today.getMonth() + 1;
    let day = today.getDate();

    // 日期和月份需要為雙位數
    if (month < 10) {
        month = `0${month}`;
    }
    if (day < 10) {
        day = `0${day}`;
    }

    const minDate = `${year}-${month}-${day}`;
    dateElement.setAttribute("min", minDate);
}

function checkUserLoggedIn() {
    const token = localStorage.getItem("token"); // 假設使用者的 JWT Token 存在本地存儲的 "userToken" 鍵下
    return token !== null;
}

async function SendBookingData(id, dateElement, fee, morning, afternoon) {
    const dateWarning = document.querySelector(".date-warning");

    if (dateWarning.classList.contains("showWarning")) {
        dateWarning.classList.remove("showWarning");
        dateWarning.classList.add("hideWarning");
        dateWarning.textContent = "";
    }

    if (dateElement.value == "") {
        dateWarning.classList.add("showWarning");
        dateWarning.classList.remove("hideWarning");
        dateWarning.textContent = "請選擇日期 👆";
        return;
    }

    if (!isRadioChanged) {
        dateWarning.classList.add("showWarning");
        dateWarning.classList.remove("hideWarning");
        dateWarning.textContent = "確定要上半場嗎？ 👇";
        return;
    }

    const attractionId = id;
    const date = dateElement.value;
    const time = morning.checked ? "morning" : "afternoon";
    const price = morning.checked ? 2000 : 2500;

    console.log(attractionId, date, time, price);

    const response = await fetch("/api/booking", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({ attractionId, date, time, price }),
    });

    const responseData = await response.json();

    if (responseData.ok) {
        window.open(window.location.origin + "/booking", "_self");
    } else {
        // 暫存資料，以免登入後消失
        const formData = {
            date: dateElement.value,
            time: morning.checked ? "上半天" : "下半天",
        };
        localStorage.setItem("formData", JSON.stringify(formData));

        const modal = document.getElementById("modal");
        modal.style.display = "flex";
    }
}

async function arrowMotion(imageCount) {
    const buttonListWrapper = document.querySelector(".button-list-wrapper");
    const leftArrowButton = buttonListWrapper.querySelector(".left-arrow");
    const rightArrowButton = buttonListWrapper.querySelector(".right-arrow");

    if (imageCount <= 1) {
        leftArrowButton.style.display = "none";
        rightArrowButton.style.display = "none";
        return;
    }

    const imagesWrapper = document.querySelector(".images-wrapper");
    const images = document.querySelectorAll(".attraction-image");

    images.forEach((img) => {
        img.addEventListener("dragstart", function (e) {
            e.preventDefault();
        });
    });

    let targetScroll = 0;
    let imageIndex = 0;
    let isScrolling = false;
    let programmaticScroll = false;
    console.log("scroll false, program False");

    function resizeImages(imageCount) {
        const screenWidth = window.screen.width; // 獲取螢幕寬度
        if (screenWidth < 580) {
            images.forEach((image) => {
                image.style.width = `${screenWidth}px`; // 設定每個圖片的寬度
            });
            // const imagesWrapper = document.querySelector(".images-wrapper");
            imagesWrapper.style.width = `${screenWidth}px`;

            console.log("screenWidth", screenWidth, "px");
        } else if (screenWidth > 580) {
            images.forEach((image) => {
                image.style.width = ""; // 或者你想設定的其他寬度
            });
            imagesWrapper.style.width = ""; // 或者你想設定的其他寬度
        }
    }

    window.addEventListener("resize", () => resizeImages(imageCount));

    resizeImages(imageCount);

    function updateDots(imageIndex, previousIndex) {
        const dotNowDiv = document.querySelector(
            `.img-nav-button-${imageIndex + 1}`
        );
        const dotLastDiv = document.querySelector(
            `.img-nav-button-${previousIndex + 1}`
        );
        dotNowDiv.classList.add("img-nav-button-active");
        dotLastDiv.classList.remove("img-nav-button-active");
    }

    imagesWrapper.addEventListener("scroll", function (e) {
        if (!programmaticScroll) {
            // imagesWrapper.scrollLeft = targetScroll;

            // bounceBack(programmaticScroll, targetScroll, imagesWrapper);
            imagesWrapper.scrollTo({
                left: targetScroll,
                behavior: "instant",
            });
        }
    });

    function getImageWidth() {
        const images = document.querySelectorAll(".attraction-image");
        return images[0] ? images[0].getBoundingClientRect().width : 0;
    }

    leftArrowButton.addEventListener("click", function () {
        let imageWidth = getImageWidth();
        console.log("imageWidth", imageWidth);

        if (isScrolling) return;

        isScrolling = true;
        programmaticScroll = true;
        console.log("scroll true, program true");

        let previousIndex = imageIndex;

        if (imageIndex > 0) {
            imageIndex--;
        } else {
            imageIndex = imageCount - 1;
        }
        console.log("LEFT", "imageIndex", imageIndex);
        updateDots(imageIndex, previousIndex);

        let documentWidth = document.documentElement.clientWidth;
        let windowWidth = window.innerWidth;
        let screenWidth = window.screen.width;
        console.log("documentWidth", documentWidth);
        console.log("innerWidth", windowWidth);
        console.log("screenWidth", screenWidth);

        targetScroll = imageIndex * imageWidth;
        console.log("👉 targetScroll", targetScroll);

        function checkIfScrollingFinished() {
            if (Math.abs(imagesWrapper.scrollLeft - targetScroll) < 1) {
                imagesWrapper.scrollLeft = targetScroll;
                isScrolling = false;
                programmaticScroll = false;
                console.log("scroll false, program False");
            } else {
                requestAnimationFrame(checkIfScrollingFinished);
            }
        }
        requestAnimationFrame(checkIfScrollingFinished);

        imagesWrapper.scrollTo({
            left: targetScroll,
            behavior: "smooth",
        });

        const maxScrollLeft =
            imagesWrapper.scrollWidth - imagesWrapper.clientWidth;
        console.log(imagesWrapper.scrollLeft, maxScrollLeft);
    });

    rightArrowButton.addEventListener("click", function () {
        let imageWidth = getImageWidth();
        console.log("imageWidth", imageWidth);

        if (isScrolling) return;

        isScrolling = true;
        programmaticScroll = true;

        let previousIndex = imageIndex;

        if (imageIndex < imageCount - 1) {
            imageIndex++;
        } else {
            imageIndex = 0;
        }

        console.log("RIGHT", "imageIndex", imageIndex);
        updateDots(imageIndex, previousIndex);

        let documentWidth = document.documentElement.clientWidth; // 如果你想要獲取不包括捲軸的視窗寬度
        let windowWidth = window.innerWidth;
        let screenWidth = window.screen.width;
        console.log("documentWidth", documentWidth);
        console.log("innerWidth", windowWidth);
        console.log("screenWidth", screenWidth);

        targetScroll = imageIndex * imageWidth;
        console.log("👉 targetScroll", targetScroll);

        function checkIfScrollingFinished() {
            if (Math.abs(imagesWrapper.scrollLeft - targetScroll) < 1) {
                imagesWrapper.scrollLeft = targetScroll;
                isScrolling = false;
                programmaticScroll = false;
                console.log("scroll false, program False");
            } else {
                requestAnimationFrame(checkIfScrollingFinished);
            }
        }
        requestAnimationFrame(checkIfScrollingFinished);
        if (imageIndex === 0) {
            imagesWrapper.scrollTo({
                left: targetScroll,
                behavior: "instant", //instant
            });
        } else {
            imagesWrapper.scrollTo({
                left: targetScroll,
                behavior: "smooth", //instant
            });
        }

        const maxScrollLeft =
            imagesWrapper.scrollWidth - imagesWrapper.clientWidth;
        console.log(imagesWrapper.scrollLeft, maxScrollLeft);
    });
}

function bounceBack(programmaticScroll, targetScroll, imagesWrapper) {
    let bouncing = false;

    if (!programmaticScroll && !bouncing) {
        bouncing = true;

        let currentScroll = imagesWrapper.scrollLeft;
        let target = targetScroll;

        // 計算回彈動畫的各個階段
        let stages = [
            currentScroll + 20, // 向右 20px
            currentScroll - 30, // 向左 30px
            target, // 回到原始位置
        ];

        let stageIndex = 0;

        function animateBounce() {
            if (stageIndex < stages.length) {
                imagesWrapper.scrollTo({
                    left: stages[stageIndex],
                    behavior: "auto",
                });
                stageIndex++;
                requestAnimationFrame(animateBounce);
            } else {
                bouncing = false;
            }
        }

        // 開始執行回彈動畫
        requestAnimationFrame(animateBounce);
    }
}
