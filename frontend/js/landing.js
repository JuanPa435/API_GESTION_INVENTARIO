// Menú móvil
function initMobileMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });

        // Cerrar menú al hacer clic en un enlace
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
            });
        });
    }
}

// Scroll suave
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Animación de números (soporta decimales y sufijo)
function animateNumbers() {
    const stats = document.querySelectorAll('.stat-value[data-value]');

    stats.forEach(stat => {
        const raw = stat.getAttribute('data-value');
        const decimals = parseInt(stat.getAttribute('data-decimals')) || 0;
        const suffix = stat.getAttribute('data-suffix') || '';
        const target = parseFloat(raw);
        if (Number.isNaN(target)) return;

        let current = 0;
        const frames = 60; // número de pasos
        const duration = 1200; // ms
        const stepTime = duration / frames;
        const increment = target / frames;

        const update = () => {
            current += increment;
            if (current < target) {
                stat.textContent = (decimals ? current.toFixed(decimals) : Math.round(current)).toLocaleString() + suffix;
                setTimeout(update, stepTime);
            } else {
                const finalText = decimals ? target.toFixed(decimals) : Math.round(target);
                stat.textContent = ('' + finalText).toLocaleString() + suffix;
            }
        };

        update();
    });
}

// Animación de aparición al scroll con IntersectionObserver
function initScrollAnimations() {
    const elements = document.querySelectorAll('.animate-on-scroll');
    if (!('IntersectionObserver' in window)) {
        elements.forEach(el => el.classList.add('in-view'));
        return;
    }
    const obs = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
                obs.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });
    elements.forEach(el => obs.observe(el));
}

// Parallax sutil para blobs de fondo
function initParallax() {
    const blobs = document.querySelectorAll('.fx-blob');
    const onScroll = () => {
        const y = window.pageYOffset || 0;
        blobs.forEach((blob, idx) => {
            const speed = 0.03 + idx * 0.02;
            blob.style.transform = `translate3d(0, ${y * speed}px, 0)`;
        });
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
}

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    initMobileMenu();
    initSmoothScroll();
    animateNumbers();
    initScrollAnimations();
    initParallax();
});