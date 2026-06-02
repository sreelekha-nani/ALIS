// ALIS Main System Scripts

// Smooth Scroll for Navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Landing Page Navbar Effect
window.addEventListener('scroll', () => {
    const nav = document.querySelector('.landing-nav');
    if (nav) {
        if (window.scrollY > 20) {
            nav.style.background = 'rgba(5, 5, 5, 0.8)';
            nav.style.backdropFilter = 'blur(20px)';
            nav.style.padding = '1.2rem 5%';
            nav.style.borderBottom = '1px solid rgba(255, 255, 255, 0.05)';
        } else {
            nav.style.background = 'transparent';
            nav.style.backdropFilter = 'none';
            nav.style.padding = '2rem 5%';
            nav.style.borderBottom = 'none';
        }
    }
});

// System Initialization Log
document.addEventListener('DOMContentLoaded', () => {
    console.log("ALIS Intelligence OS initialized.");
});
