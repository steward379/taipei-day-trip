const domainURL = `http://127.0.0.1:`;
// const domainURL = `http://54.253.20.174:`;
const port = `3000`;

const state = {
    nextPage: null,
    currentPage: 0,
    isLoading: false,
    currentKeyword: "",
    mrtOnly: false,
};

let observer;

function loadingLiState() {
    if (document.querySelector(".main-image")) {
        document.querySelector(
            ".main-image"
        ).style.animation = `loading-animation 0.5s ease-in-out infinite`;
    }
}

function finishLiLoading() {
    if (document.querySelector(".main-image")) {
        const images = document.querySelectorAll(".main-image");
        images.forEach((image) => {
            image.style.animation = `none`;
        });
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    await initialize();
});
// window.addEventListener('load', async () => {
//   await fetchMRTData();
//   fetchData();
// });
async function initialize() {
    // let currentPage = 0;
    // let nextPage = null;
    // let isLoading = false;
    // let currentKeyword = "";
    setupSearchButtonListener();
    setupEnterKeyListener();
    observer = setupObserver();
    await firstFetchLoad();
}

async function firstFetchLoad() {
    await fetchMRTData();

    fetchData();
}
function setupEnterKeyListener() {
    const searchInput = document.getElementById("search-input");

    searchInput.addEventListener("keydown", (event) => {
        if (event.isComposing) {
            return;
        }
        //   中文輸入法

        if (event.key === "Enter") {
            const keywordInputSubmit = searchInput.value;
            state.currentPage = 0;
            state.currentKeyword = keywordInputSubmit;
            state.mrtOnly = false;

            fetchData();
        }
    });
}
// debounce (don't need it for now)
//  取消請求 AbortController - axios 先不用
function setupObserver() {
    const options = {
        root: null, // 以 viewport 為基準
        rootMargin: "0px", // 不添加額外邊距
        threshold: 0.5, // 至少 50% 的目標元素需要在 viewport 內
    };
    return new IntersectionObserver(handleIntersection, options);
}
function handleIntersection(entries) {
    // if (
    //   entries[0].isIntersecting &&
    //   ...
    // ) {
    //     ...
    // }
    entries.forEach((entry) => {
        if (
            entry.isIntersecting &&
            !state.isLoading &&
            state.nextPage !== null
        ) {
            observer.unobserve(entry.target);
            state.currentPage = state.nextPage;
            fetchData();
        }
    });
}
// async function fetchData(currentPage = 0, keyword = "", mrtOnly = false) {
async function fetchData() {
    if (state.isLoading) return;
    state.isLoading = true;

    const { currentPage, currentKeyword, mrtOnly, isLoading, nextPage } = state;

    console.log(
        `Fetching data for page ${currentPage} (human ${
            currentPage + 1
        }  ) on ${
            mrtOnly && currentKeyword
                ? currentKeyword + " MRT station only"
                : currentKeyword
                ? currentKeyword + " Place Name or MRT Station"
                : "all attractions"
        }.`
    );
    // const url = `http://54.253.20.174:3000/api/attractions?page=${currentPage}`;
    // let formatAPIurl = `${domainURL}${port}/api/attractions?page=${currentPage}`; //// CORS
    let formatAPIurl = `/api/attractions?page=${currentPage}`;
    if (currentKeyword) {
        formatAPIurl += `&keyword=${currentKeyword}`;
        if (mrtOnly) {
            formatAPIurl += `&mrtOnly=true`;
        }
    }

    console.log(formatAPIurl);

    // renderData(formatAPIurl)

    try {
        const response = await fetch(formatAPIurl);
        const dataAttractionsPrimitive = await response.json();
        const dataAttractions = dataAttractionsPrimitive["data"];

        // fetch(url)
        //   .then(response => response.json())
        //   .then(data => {

        if (currentPage === 0) {
            const photoProfile = document.querySelector(".photo-profile");
            if (photoProfile) photoProfile.innerHTML = "";
        }
        // createElements(dataAttractions);

        const mainElement = document.querySelector("main");
        const existingNoDataDiv = mainElement.querySelector(".no-data");

        // 如果 .no-data 存在，則先將其刪除
        if (existingNoDataDiv) {
            existingNoDataDiv.remove();
        }

        if (dataAttractions && dataAttractions.length > 0) {
            createElements(dataAttractions);
            loadingLiState();
        } else {
            const mainElement = document.querySelector("main");
            const existingNoDataDiv = mainElement.querySelector(".no-data");
            if (existingNoDataDiv) {
                existingNoDataDiv.remove();
            }
            const noDataDiv = document.createElement("div");
            noDataDiv.className = "no-data";
            noDataDiv.textContent = "沒有資料";
            mainElement.appendChild(noDataDiv);
        }
        // async await
        setTimeout(() => {
            const ulProfile = document.querySelector(".photo-profile");
            if (ulProfile && ulProfile.lastChild) {
                observer.observe(ulProfile.lastChild);
            }
            finishLiLoading();
        }, 300); // 延遲 300 毫秒

        state.nextPage = dataAttractionsPrimitive["nextPage"];

        let nowNextPage = state.nextPage;
        console.log("real data.nextPage now", nowNextPage);
        // })

        state.isLoading = false;
    } catch (error) {
        console.log("Error Fetching data:", error);
        finishLiLoading();
        state.isLoading = false;
    }
}
// Search Function
function setupSearchButtonListener() {
    const searchButton = document.getElementById("search-button");
    searchButton.addEventListener("click", () => {
        // keyword = document.getElementById("search-input").value;
        const keywordInputSubmit =
            document.getElementById("search-input").value;

        state.currentPage = 0;
        state.currentKeyword = keywordInputSubmit;
        state.mrtOnly = false;

        fetchData();
        // fetchData(currentPage, keywordSubmit);
    });
}
// MRT Buttons Line Up
async function fetchMRTData() {
    try {
        // const urlMrt = `${domainURL}${port}/api/mrts`; // // CORS
        const urlMrt = `/api/mrts`;
        const response = await fetch(urlMrt);
        const dataMRT = await response.json();

        generateMRTButtons(dataMRT.data);
    } catch (error) {
        console.log("Error Fetching data:", error);
    }
}
// Search for MRT Only
function generateMRTButtons(mrtData) {
    const buttonWrapper = document.querySelector(".button-wrapper");
    buttonWrapper.innerHTML = "";

    mrtData.forEach((mrt) => {
        const button = document.createElement("button");
        button.className = "keyword-button";
        button.textContent = mrt;
        button.setAttribute("data-keyword", mrt);

        button.addEventListener("click", function () {
            const keywordMRTButton = this.textContent;
            // const keywordMRTButton = this.getAttribute("data-keyword");

            const searchInput = document.getElementById("search-input");
            searchInput.value = keywordMRTButton;

            state.currentPage = 0;
            state.currentKeyword = keywordMRTButton;
            state.mrtOnly = true;

            fetchData();
            // fetchData(currentPage, keywordMRTButton, true);
        });
        buttonWrapper.appendChild(button);
    });
    const buttonListWrapper = document.querySelector(".button-list-wrapper");
    const leftArrowButton = buttonListWrapper.querySelector(".left-arrow");
    const rightArrowButton = buttonListWrapper.querySelector(".right-arrow");

    leftArrowButton.addEventListener("click", function () {
        const maxScrollLeft =
            buttonWrapper.scrollWidth - buttonWrapper.clientWidth;

        if (buttonWrapper.scrollLeft > 0) {
            buttonWrapper.scrollTo({
                left: buttonWrapper.scrollLeft - 250,
                behavior: "smooth",
            });
        } else {
            // 模擬彈跳效果
            buttonWrapper.scrollTo({
                left: buttonWrapper.scrollLeft + 20,
                behavior: "smooth",
            });
            setTimeout(() => {
                buttonWrapper.scrollTo({
                    left: buttonWrapper.scrollLeft - 20,
                    behavior: "smooth",
                });
            }, 100);
        }
    });

    rightArrowButton.addEventListener("click", function () {
        const maxScrollLeft =
            buttonWrapper.scrollWidth - buttonWrapper.clientWidth;

        if (buttonWrapper.scrollLeft + 50 < maxScrollLeft) {
            buttonWrapper.scrollTo({
                left: buttonWrapper.scrollLeft + 250,
                behavior: "smooth",
            });
        } else {
            // 模擬彈跳效果
            console.log("end");
            buttonWrapper.scrollTo({
                left: buttonWrapper.scrollLeft - 20,
                behavior: "smooth",
            });
            setTimeout(() => {
                buttonWrapper.scrollTo({
                    left: buttonWrapper.scrollLeft + 20,
                    behavior: "smooth",
                });
            }, 100);
        }
    });
}

function createElements(attractions) {
    const mainElement = document.querySelector("main");
    const ulProfile =
        mainElement.querySelector(".photo-profile") ||
        document.createElement("ul");
    ulProfile.className = "photo-profile";

    attractions.forEach((attraction, i) => {
        const liProfile = document.createElement("li");
        liProfile.className = `profile-li profile-li-${i + 1}`;

        profileGenerate(i, attraction, liProfile);

        ulProfile.appendChild(liProfile);
    });

    loadingLiState();

    if (!mainElement.contains(ulProfile)) {
        mainElement.appendChild(ulProfile);
        observer.observe(ulProfile.lastChild);
    }
}

function profileGenerate(i, attraction, newProfileList) {
    let divElement = document.createElement("div");
    divElement.className = `profile-img profile-img-${i + 1}`;

    let imgElement = document.createElement("img");
    if (attraction.images && attraction.images[0]) {
        // imgElement.src = "https://" + attractions[i].file.split('https://')[1]; // 使用 JSON 資料中的圖片 URL
        // imgElement.src = attractions[i].images[0] || "http://placekitten.com/420/500";
        imgElement.src = attraction.images[0];
        divElement.appendChild(imgElement);
    } else {
        let textDiv = document.createElement("div");
        textDiv.className = "fallback-text";
        textDiv.textContent = "【缺圖中】" + attraction.name;
        divElement.appendChild(textDiv);
    }
    imgElement.alt = `profile-img-${i}`;
    imgElement.className = "main-image";
    imgElement.setAttribute("loading", "lazy");
    // imgElement = imgElement.cloneNode(true);

    // attraction/<id>.html

    imgElement.onclick = function () {
        window.open(`./attraction/${attraction.id}`, "_self");
    };

    // let svgElement = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    // svgElement.setAttribute("class", "star");
    // svgElement.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    // svgElement.setAttribute("fill", "white");
    // svgElement.setAttribute("height", "1.5em");
    // svgElement.setAttribute("viewBox", "0 0 576 512");

    // let pathElement = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    // pathElement.setAttribute('d',
    //   'M316.9 18C311.6 7 300.4 0 288.1 0s-23.4 7-28.8 18L195 150.3 51.4 171.5c-12 1.8-22 10.2-25.7 21.7s-.7 24.2 7.9 32.7L137.8 329 113.2 474.7c-2 12 3 24.2 12.9 31.3s23 8 33.8 2.3l128.3-68.5 128.3 68.5c10.8 5.7 23.9 4.9 33.8-2.3s14.9-19.3 12.9-31.3L438.5 329 542.7 225.9c8.6-8.5 11.7-21.2 7.9-32.7s-13.7-19.9-25.7-21.7L381.2 150.3 316.9 18z'
    // );

    let divElementTitle = document.createElement("div");
    divElementTitle.className = `profile-img-div profile-title profile-title-${
        i + 1
    }`;
    divElementTitle.textContent = attraction.name || "【沒有名稱】";

    if (attraction.name.length > 15) {
        divElementTitle.style.fontSize = "14px";
    }

    let ulElement = document.createElement("ul");
    ulElement.className = `profile-img-div profile-des profile-des-${i + 1}`;

    let liElement = document.createElement("li");
    liElement.textContent = attraction.mrt || "沒有捷運站";
    liElement.className = `profile-des-li-mrt`;

    let liElement2 = document.createElement("li");
    liElement2.textContent = attraction.category || "沒有分類";
    liElement2.className = `profile-des-li-category`;

    newProfileList.appendChild(divElement);
    divElement.appendChild(imgElement);
    // divElement.appendChild(svgElement);
    // svgElement.appendChild(pathElement);
    divElement.appendChild(divElementTitle);
    newProfileList.appendChild(ulElement);
    ulElement.appendChild(liElement);
    ulElement.appendChild(liElement2);
}
