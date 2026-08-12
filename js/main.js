/* ============================================================
   Jays-Graphic-Arts — Main JavaScript
   ============================================================ */

(function () {
  'use strict';

  const CONTACT_EMAIL = 'hello@jays-graphic-arts.ai';
  const MAILTO_BODY_LIMIT = 1600;
  const BRIEF_PREVIEW_LIMIT = 500;

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

  function buildBriefSummary(data) {
    const lines = [
      `First name: ${data.firstName || ''}`,
      `Last name: ${data.lastName || ''}`,
      `Email: ${data.email || ''}`,
      `Company: ${data.company || 'N/A'}`,
      `Service: ${data.service || ''}`,
      `Budget: ${data.budget || ''}`,
      `Timeline: ${data.timeline || ''}`,
      `Referral: ${data.referral || 'N/A'}`,
      '',
      'Project brief:',
      data.brief || '',
    ];

    return lines.join('\n');
  }

  async function copyText(text) {
    if (!navigator.clipboard || !navigator.clipboard.writeText) {
      return false;
    }

    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      return false;
    }
  }

  /* ---- Contact form --------------------------------------- */
  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', async function (e) {
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
      const summary = buildBriefSummary(data);
      const briefPreview = (data.brief || '').length > BRIEF_PREVIEW_LIMIT
        ? `${(data.brief || '').slice(0, BRIEF_PREVIEW_LIMIT)}…`
        : (data.brief || '');
      const copied = await copyText(summary);
      const subject = `Project brief: ${data.service || 'new inquiry'} — ${data.firstName || ''} ${data.lastName || ''}`.trim();
      const backupLine = copied
        ? 'The full brief was also copied to my clipboard as a backup.'
        : 'If your email client trims long messages, please keep a copy of this brief before sending.';
      const fullBody = [
        'Hello Jays-Graphic-Arts,',
        '',
        'I would like to start a project. My brief is below:',
        '',
        summary,
        '',
        backupLine,
      ].join('\n');
      const body = fullBody.length > MAILTO_BODY_LIMIT
        ? [
            'Hello Jays-Graphic-Arts,',
            '',
            'I would like to start a project. My full brief is too long to safely include in a mailto draft.',
            '',
            `Name: ${data.firstName || ''} ${data.lastName || ''}`.trim(),
            `Email: ${data.email || ''}`,
            `Company: ${data.company || 'N/A'}`,
            `Service: ${data.service || ''}`,
            `Budget: ${data.budget || ''}`,
            `Timeline: ${data.timeline || ''}`,
            '',
            'Brief preview:',
            briefPreview,
            '',
            copied
              ? 'The full brief was copied to my clipboard. Please paste it into the email before sending.'
              : 'The full brief is still in the form on the page. Please copy it into the email before sending.',
          ].join('\n')
        : fullBody;
      const mailtoHref = `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      const mailtoLink = document.createElement('a');
      mailtoLink.href = mailtoHref;
      mailtoLink.style.display = 'none';
      document.body.appendChild(mailtoLink);
      mailtoLink.click();
      mailtoLink.remove();

      showToast(copied
        ? '✓ Email draft opened, your full brief was copied, and your form entries were kept in place.'
        : '✓ Email draft opened. Your form entries were kept in place in case you need to resend.');
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
