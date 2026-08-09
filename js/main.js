/* ============================================================
   Jays-Graphic-Arts — Main JavaScript
   ============================================================ */

(function () {
  'use strict';

  /* ---- Navigation: scroll behaviour ----------------------- */
  const nav = document.getElementById('nav');
  if (nav) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 40) {
        nav.classList.add('scrolled');
      } else {
        nav.classList.remove('scrolled');
      }
    }, { passive: true });
  }

  /* ---- Navigation: mobile toggle -------------------------- */
  const navToggle = document.getElementById('navToggle');
  const navLinks  = document.getElementById('navLinks');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
    });

    // Close when a link is clicked
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
      });
    });
  }

  /* ---- Toast helper --------------------------------------- */
  function showToast(message) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    if (message) toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 4000);
  }

  /* ---- Contact form --------------------------------------- */
  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
      e.preventDefault();

      // Simple client-side validation
      const required = contactForm.querySelectorAll('[required]');
      let valid = true;
      required.forEach(field => {
        if (!field.value.trim()) {
          valid = false;
          field.style.borderColor = '#ff4444';
          field.addEventListener('input', () => {
            field.style.borderColor = '';
          }, { once: true });
        }
      });

      if (!valid) {
        showToast('⚠️ Please fill in all required fields.');
        return;
      }

      // Serialize form data
      const data = Object.fromEntries(new FormData(contactForm));

      // In a real deployment this would POST to an API endpoint.
      // For now we log to console and show the success toast.
      console.log('[Jays-Graphic-Arts] Brief submitted:', data);

      contactForm.reset();
      showToast('✓ Brief submitted! Check your email for your quote within 60 seconds.');
    });
  }

  /* ---- Intersection observer: fade-up animations ---------- */
  if ('IntersectionObserver' in window) {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -40px 0px',
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    // Observe service cards, stat cards, portfolio cards
    const animatables = document.querySelectorAll(
      '.service-card, .stat-card, .portfolio-card, .testimonial-card, .metric, .step, .pricing-card'
    );

    animatables.forEach((el, i) => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(20px)';
      el.style.transition = `opacity 0.5s ease ${i * 0.06}s, transform 0.5s ease ${i * 0.06}s`;
      observer.observe(el);
    });
  }

  /* ---- Active nav link based on current page -------------- */
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });

})();
