async function showToast(message, type = "success") {
	const container = document.getElementById("toastContainer");

	const toast = document.createElement("div");
	toast.className = `toast ${type}`;
	toast.textContent = message;
	container.appendChild(toast);

	setTimeout(() => toast.classList.add("show"), 100);

	setTimeout(() => {
		toast.classList.remove("show");
		setTimeout(() => toast.remove(), 500);
	}, 3000);
}
