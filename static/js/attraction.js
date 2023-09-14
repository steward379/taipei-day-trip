// http://54.253.20.174/
const domainURL = `http://127.0.0.1:`;
const port = `3000`;

function getAttractionIdFromURL() {
    const pathQuery = window.location.pathname.split("/");
    const lastQuery = pathQuery[pathQuery.length - 1];

    if (/^[0-9]+$/.test(lastQuery)) {
        return lastQuery;
    } else {
        return null;
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    const attraction_id = getAttractionIdFromURL();
    console.log(attraction_id);

    if (attraction_id) await initialize(attraction_id);
});

async function initialize(id) {
    let formatAPIurl = `${domainURL}${port}/api/attraction/${id}`;
    console.log(id);

    try {
        const response = await fetch(formatAPIurl);
        const dataAttractionsPrimitive = await response.json();
        const dataAttractions = dataAttractionsPrimitive["data"];

        console.log(dataAttractions);

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
            const attractionImages = document.querySelector(
                ".photo-img-left-div"
            );

            attractionName.textContent = dataAttractions["name"];
            attractionCategory.textContent = dataAttractions["category"];
            attractionDescription.textContent = dataAttractions["description"];
            attractionAddress.textContent = dataAttractions["address"];
            attractionMrt.textContent = dataAttractions["mrt"];
            attractionTransport.textContent = dataAttractions["transport"];

            for (let i = 0; i < dataAttractions["images"].length; i++) {
                const img = document.createElement("img");

                img.src = dataAttractions["images"][i];

                img.alt = `attraction image ${dataAttractions["name"]} - ${i}`;
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

            // attractions.forEach((attraction, i) => {
            //         const liProfile = document.createElement("li");
            //         liProfile.className = `profile-li profile-li-${i + 1}`;

            //         profileGenerate(i, attraction, liProfile);

            //         ulProfile.appendChild(liProfile);
            //     });
            //     if (!mainElement.contains(ulProfile)) {
            //         mainElement.appendChild(ulProfile);
            //         observer.observe(ulProfile.lastChild);
            //     }
        }

        // DOM
    } catch {
        console.log("error");
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
    let programmaticScroll = false;

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
    let imageIndex = 0;

    let isScrolling = false;
    console.log("now False");

    leftArrowButton.addEventListener("click", function () {
        const maxScrollLeft =
            imagesWrapper.scrollWidth - imagesWrapper.clientWidth;

        console.log("Left arrow clicked");
        if (isScrolling) return;

        isScrolling = true;
        console.log("now True");
        programmaticScroll = true;

        if (imagesWrapper.scrollLeft > 0) {
            if (imageIndex > 0) {
                targetScroll = imagesWrapper.scrollLeft - 540;
                imagesWrapper.scrollTo({
                    left: imagesWrapper.scrollLeft - 540,
                    behavior: "smooth",
                });

                const dotNowDiv = document.querySelector(
                    `.img-nav-button-${imageIndex}`
                );
                const dotLastDiv = document.querySelector(
                    `.img-nav-button-${imageIndex + 1}`
                );
                dotNowDiv.classList.add("img-nav-button-active");
                dotLastDiv.classList.remove("img-nav-button-active");

                imageIndex--;
                console.log("left", imageIndex);
            }
        } else {
            targetScroll = maxScrollLeft;
            imagesWrapper.scrollTo({
                left: maxScrollLeft,
                behavior: "smooth",
            });

            console.log("imageCount", imageCount);

            const dotFirstDiv = document.querySelector(".img-nav-button-1");
            const dotEndDiv = document.querySelector(
                `.img-nav-button-${imageCount}`
            );
            dotFirstDiv.classList.remove("img-nav-button-active");
            dotEndDiv.classList.add("img-nav-button-active");

            imageIndex = imageCount - 1;
            console.log("go to last", imageIndex);
        }

        function checkIfScrollingFinished() {
            if (Math.abs(imagesWrapper.scrollLeft - targetScroll) < 1) {
                isScrolling = false;
                programmaticScroll = false;
                console.log("now False");
            } else {
                requestAnimationFrame(checkIfScrollingFinished);
            }
        }
        requestAnimationFrame(checkIfScrollingFinished);
    });

    rightArrowButton.addEventListener("click", function () {
        const maxScrollLeft =
            imagesWrapper.scrollWidth - imagesWrapper.clientWidth;

        if (isScrolling) return;

        isScrolling = true;
        console.log("now True");
        programmaticScroll = true;

        console.log(imagesWrapper.scrollLeft, maxScrollLeft);

        if (imagesWrapper.scrollLeft < maxScrollLeft) {
            if (imageIndex < imageCount) {
                targetScroll = imagesWrapper.scrollLeft + 540;
                imagesWrapper.scrollTo({
                    left: imagesWrapper.scrollLeft + 540,
                    behavior: "smooth",
                });

                const dotNowDiv = document.querySelector(
                    `.img-nav-button-${imageIndex + 2}`
                );
                const dotLastDiv = document.querySelector(
                    `.img-nav-button-${imageIndex + 1}`
                );
                dotNowDiv.classList.add("img-nav-button-active");
                dotLastDiv.classList.remove("img-nav-button-active");

                imageIndex++;
                console.log("right", imageIndex);
            }
        } else {
            targetScroll = 0;
            imagesWrapper.scrollTo({
                left: 0,
                behavior: "smooth",
            });

            const dotFirstDiv = document.querySelector(".img-nav-button-1");
            const dotEndDiv = document.querySelector(
                `.img-nav-button-${imageCount}`
            );
            dotFirstDiv.classList.add("img-nav-button-active");
            dotEndDiv.classList.remove("img-nav-button-active");

            imageIndex = 0;
            console.log("back to start", imageIndex);
        }

        function checkIfScrollingFinished() {
            if (Math.abs(imagesWrapper.scrollLeft - targetScroll) < 1) {
                isScrolling = false;
                programmaticScroll = false;
                console.log("now False");
            } else {
                requestAnimationFrame(checkIfScrollingFinished);
            }
        }
        requestAnimationFrame(checkIfScrollingFinished);
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
