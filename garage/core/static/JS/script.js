// Burger Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    console.log('Garage Management loaded');
    
    const burgerMenu = document.getElementById('burger-menu');
    const mobileNav = document.getElementById('mobile-nav');
    
    if (burgerMenu && mobileNav) {
        burgerMenu.addEventListener('click', function() {
            burgerMenu.classList.toggle('active');
            mobileNav.classList.toggle('active');
        });
        
        // Fermer le menu quand on clique sur un lien
        const navLinks = mobileNav.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                burgerMenu.classList.remove('active');
                mobileNav.classList.remove('active');
            });
        });
        
        // Fermer le menu quand on clique en dehors
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.header-top')) {
                burgerMenu.classList.remove('active');
                mobileNav.classList.remove('active');
            }
        });
    }
    
    // Responsive text adjustments
    function adjustResponsiveText() {
        const width = window.innerWidth;
        
        // Logo adjustments
        const logo = document.querySelector('.logo');
        if (logo) {
            if (width < 480) {
                logo.style.gap = '4px';
            } else if (width < 768) {
                logo.style.gap = '8px';
            }
        }
        
        // Heading adjustments
        const headings = document.querySelectorAll('h1');
        headings.forEach(h => {
            if (width < 480) {
                h.style.fontSize = 'clamp(1.5rem, 4vw, 2rem)';
            }
        });
    }

    function applyFadeUpAnimations() {
        const fadeItems = document.querySelectorAll('.fade-up');
        if (!('IntersectionObserver' in window) || fadeItems.length === 0) {
            fadeItems.forEach(item => item.classList.add('visible'));
            return;
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                entry.target.classList.toggle('visible', entry.isIntersecting);
            });
        }, {
            threshold: 0.15
        });

        fadeItems.forEach(item => observer.observe(item));
    }

    function ensureBottomOverlay() {
        let overlay = document.querySelector('.bottom-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'bottom-overlay';
            document.body.appendChild(overlay);
        }
        return overlay;
    }

    function updateScrollEffects() {
        const header = document.querySelector('header');
        const texts = document.querySelectorAll('.hero-text');
        const overlay = ensureBottomOverlay();
        const scrollTop = window.scrollY || window.pageYOffset;
        const atTop = scrollTop <= 0;
        const atBottom = window.innerHeight + scrollTop >= document.documentElement.scrollHeight - 2;

        if (header) {
            header.classList.toggle('transparent', atTop);
        }

        texts.forEach(text => {
            text.classList.toggle('flexible', atBottom);
        });

        overlay.classList.toggle('visible', atBottom);
    }
    
    adjustResponsiveText();
    applyFadeUpAnimations();
    updateScrollEffects();
    window.addEventListener('resize', adjustResponsiveText);
    window.addEventListener('scroll', updateScrollEffects);
});

