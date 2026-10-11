/* ============================================================
   KARATINA UNIVERSITY NATURE CLUB LMS — MAIN JAVASCRIPT
   ============================================================ */

'use strict';

// ── Dark Mode ──────────────────────────────────────────────
const Theme = (() => {
  const root = document.documentElement;
  const btn  = document.getElementById('themeBtn');
  const icon = document.getElementById('themeIcon');

  function apply(t) {
    root.setAttribute('data-theme', t);
    localStorage.setItem('lms-theme', t);
    if (icon) {
      icon.className = t === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
  }

  function init() {
    const saved = localStorage.getItem('lms-theme') ||
      (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    apply(saved);
    btn?.addEventListener('click', () => {
      apply(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
    });
  }
  return { init };
})();

// ── Page Loader ────────────────────────────────────────────
const Loader = (() => {
  function hide() {
    const el = document.getElementById('pageLoader');
    if (!el) return;
    setTimeout(() => el.classList.add('hidden'), 400);
    setTimeout(() => el.remove(), 1000);
  }
  return { hide };
})();

// ── Navbar ─────────────────────────────────────────────────
const Navbar = (() => {
  function init() {
    const nav  = document.getElementById('mainNav');
    const ham  = document.getElementById('hamburger');
    const menu = document.getElementById('mobileMenu');
    if (!nav) return;

    // Scroll shadow
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 20);
    }, { passive: true });

    // Mobile menu
    ham?.addEventListener('click', () => {
      ham.classList.toggle('open');
      menu?.classList.toggle('open');
      document.body.style.overflow = menu?.classList.contains('open') ? 'hidden' : '';
    });

    // Close mobile menu on link click
    menu?.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        ham?.classList.remove('open');
        menu.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
  }
  return { init };
})();

// ── FAQ Accordion ──────────────────────────────────────────
const FAQ = (() => {
  function init() {
    document.querySelectorAll('.faq-trigger').forEach(trigger => {
      trigger.addEventListener('click', () => {
        const item   = trigger.closest('.faq-item');
        const isOpen = item.classList.contains('open');
        // Close all
        document.querySelectorAll('.faq-item.open').forEach(i => i.classList.remove('open'));
        if (!isOpen) item.classList.add('open');
      });
    });
  }
  return { init };
})();

// ── Tabs ───────────────────────────────────────────────────
const Tabs = (() => {
  function init(scope = document) {
    scope.querySelectorAll('.tab-nav').forEach(nav => {
      nav.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const group = btn.dataset.tab;
          const parent = nav.closest('[data-tabs]') || nav.parentElement;

          nav.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');

          parent.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
          parent.querySelector(`#${group}`)?.classList.add('active');
        });
      });
      // Activate first tab
      nav.querySelector('.tab-btn:first-child')?.click();
    });
  }
  return { init };
})();

// ── Scroll reveal ──────────────────────────────────────────
const Reveal = (() => {
  function init() {
    if (!('IntersectionObserver' in window)) {
      document.querySelectorAll('.reveal').forEach(el => el.classList.add('in'));
      return;
    }
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); obs.unobserve(e.target); } });
    }, { threshold: 0.12 });
    document.querySelectorAll('.reveal').forEach(el => obs.observe(el));
  }
  return { init };
})();

// ── Toast Notifications ─────────────────────────────────────
const Toast = (() => {
  function show(msg, type = 'success') {
    const icons = { success: 'fa-check-circle', error: 'fa-times-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
    const container = document.getElementById('toastContainer') || (() => {
      const c = document.createElement('div');
      c.className = 'toast-container'; c.id = 'toastContainer';
      document.body.appendChild(c); return c;
    })();
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.innerHTML = `<i class="fas ${icons[type] || icons.info}" style="color:${type==='success'?'#059669':type==='error'?'#dc3545':type==='warning'?'#f59e0b':'#3b82f6'};flex-shrink:0;"></i><span>${msg}</span>`;
    container.appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateX(60px)'; t.style.transition = 'all .4s'; setTimeout(() => t.remove(), 400); }, 4000);
  }
  return { show };
})();

// ── Modal ──────────────────────────────────────────────────
const Modal = (() => {
  function open(id) {
    const m = document.getElementById(id);
    m?.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function close(id) {
    const m = document.getElementById(id);
    m?.classList.remove('open');
    document.body.style.overflow = '';
  }
  function init() {
    // Close on overlay click
    document.querySelectorAll('.modal-overlay').forEach(m => {
      m.addEventListener('click', e => { if (e.target === m) close(m.id); });
    });
    // Close buttons
    document.querySelectorAll('[data-modal-close]').forEach(btn => {
      btn.addEventListener('click', () => close(btn.dataset.modalClose));
    });
    // Open triggers
    document.querySelectorAll('[data-modal-open]').forEach(btn => {
      btn.addEventListener('click', () => open(btn.dataset.modalOpen));
    });
    // ESC key
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.open').forEach(m => close(m.id));
      }
    });
  }
  return { open, close, init };
})();

// ── Animated Counters ──────────────────────────────────────
const Counter = (() => {
  function animateValue(el, target, duration = 1800) {
    const start = 0;
    const startTime = performance.now();
    const step = (time) => {
      const progress = Math.min((time - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.floor(eased * target) + (el.dataset.suffix || '');
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  function init() {
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting && !e.target.dataset.counted) {
          e.target.dataset.counted = '1';
          animateValue(e.target, parseInt(e.target.dataset.target, 10));
          obs.unobserve(e.target);
        }
      });
    }, { threshold: 0.5 });
    document.querySelectorAll('[data-target]').forEach(el => obs.observe(el));
  }
  return { init };
})();

// ── Progress Bar animation ─────────────────────────────────
const ProgressBars = (() => {
  function init() {
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.style.width = e.target.dataset.width || e.target.style.width;
          obs.unobserve(e.target);
        }
      });
    }, { threshold: 0.2 });
    document.querySelectorAll('.progress-fill[data-width]').forEach(b => { b.style.width = '0'; obs.observe(b); });
  }
  return { init };
})();

// ── Password Toggle ────────────────────────────────────────
const PasswordToggle = (() => {
  function init() {
    document.querySelectorAll('[data-pw-toggle]').forEach(btn => {
      btn.addEventListener('click', () => {
        const target = document.getElementById(btn.dataset.pwToggle);
        if (!target) return;
        const isText = target.type === 'text';
        target.type = isText ? 'password' : 'text';
        btn.querySelector('i').className = isText ? 'fas fa-eye' : 'fas fa-eye-slash';
      });
    });
  }
  return { init };
})();

// ── Star Rating ────────────────────────────────────────────
const StarRating = (() => {
  function init() {
    document.querySelectorAll('.star-rating').forEach(group => {
      const stars = group.querySelectorAll('.star');
      const input = group.parentElement.querySelector('input[name="rating"]');
      stars.forEach((star, i) => {
        star.addEventListener('mouseenter', () => stars.forEach((s, j) => s.classList.toggle('active', j <= i)));
        star.addEventListener('click', () => {
          const val = i + 1;
          if (input) input.value = val;
          stars.forEach((s, j) => s.classList.toggle('selected', j < val));
        });
      });
      group.addEventListener('mouseleave', () => {
        const val = input ? parseInt(input.value, 10) || 0 : 0;
        stars.forEach((s, j) => s.classList.toggle('active', j < val));
      });
    });
  }
  return { init };
})();

// ── Smooth scroll for anchor links ─────────────────────────
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    });
  });
}

// ── Sidebar panel switching (dashboard) ────────────────────
const SidebarNav = (() => {
  function init() {
    document.querySelectorAll('[data-panel]').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const panel = link.dataset.panel;
        document.querySelectorAll('[data-panel]').forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        document.querySelectorAll('.dash-panel').forEach(p => p.classList.remove('active'));
        document.getElementById('panel-' + panel)?.classList.add('active');
      });
    });
    // Activate first
    document.querySelector('[data-panel]')?.click();
  }
  return { init };
})();

// ── Course Enrollment (demo) ────────────────────────────────
const Enrollment = (() => {
  function init() {
    document.querySelectorAll('[data-enroll]').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.enroll;
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enrolling...';
        setTimeout(() => {
          btn.innerHTML = '<i class="fas fa-check"></i> Enrolled!';
          btn.classList.add('btn-success');
          btn.classList.remove('btn-primary');
          Toast.show('Successfully enrolled in course!', 'success');
        }, 1200);
      });
    });
  }
  return { init };
})();

// ── INIT ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  Theme.init();
  Navbar.init();
  FAQ.init();
  Tabs.init();
  Reveal.init();
  Modal.init();
  Counter.init();
  ProgressBars.init();
  PasswordToggle.init();
  StarRating.init();
  SidebarNav.init();
  Enrollment.init();
  initSmoothScroll();
});

window.addEventListener('load', () => Loader.hide());

// Expose globals for inline usage
window.LMS = { Toast, Modal, Theme };
