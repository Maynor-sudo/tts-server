// ELEMENTOS
const menuBtn = document.getElementById("menuBtn");
const sidebar = document.getElementById("sidebar");
const overlay = document.getElementById("overlay");

const textarea = document.getElementById("text");
const counter = document.getElementById("counter");
const form = document.querySelector("form");
const loader = document.getElementById("loader");

// SIDEBAR
if (menuBtn && sidebar && overlay) {
    menuBtn.addEventListener("click", () => {
        sidebar.classList.toggle("active");
        overlay.classList.toggle("active");
    });

    overlay.addEventListener("click", () => {
        sidebar.classList.remove("active");
        overlay.classList.remove("active");
    });
}

// CONTADOR
if (textarea && counter) {
    textarea.addEventListener("input", () => {
        counter.textContent = textarea.value.length + " / 500";
    });
}

// LOADER
if (form && loader) {
    form.addEventListener("submit", () => {
        loader.style.display = "block";
    });
}

// EFECTO TEXTAREA
if (textarea) {
    textarea.addEventListener("focus", () => {
        textarea.style.boxShadow = "0 0 10px #6c5ce7";
    });

    textarea.addEventListener("blur", () => {
        textarea.style.boxShadow = "none";
    });
}

// BOTÓN
const convertBtn = document.querySelector("button[type='submit']");

if (convertBtn) {
    convertBtn.addEventListener("click", () => {
        convertBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
    });
}