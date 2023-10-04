// JS for content editable trick from Chris Coyier

const urlParams = new URLSearchParams(window.location.search);
const orderNumber = urlParams.get('number');

console.log(orderNumber);

// 找到 HTML 元素並更新它

document.addEventListener("DOMContentLoaded",  () => {
	const orderNumberElement = document.getElementById("orderNumber");

	console.log(orderNumberElement);

	if (orderNumber) {
		orderNumberElement.textContent = `您的訂單編號是：${orderNumber}`;
	} else {
		orderNumberElement.textContent = '無法獲取訂單編號';
	}

	const thankYou = document.querySelector(".thank-you");

	thankYou.addEventListener("input", function() {
		let text = this.innerText;
		this.setAttribute("data-heading", text);
		this.parentElement.setAttribute("data-heading", text);
	});
});
