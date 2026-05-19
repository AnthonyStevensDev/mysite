// ===== Initialize Lucide Icons =====
document.addEventListener('DOMContentLoaded', () => {
  lucide.createIcons();

  // ===== Year in Footer =====
  const yearEl = document.getElementById('current-year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // ===== Navbar Scroll Effect =====
  const navbar = document.getElementById('navbar');
  const handleScroll = () => {
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  };
  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();

  // ===== Mobile Menu Toggle =====
  const menuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  let menuOpen = false;

  menuBtn.addEventListener('click', () => {
    menuOpen = !menuOpen;
    mobileMenu.classList.toggle('hidden', !menuOpen);
    const icon = menuBtn.querySelector('[data-lucide]');
    if (menuOpen) {
      icon.setAttribute('data-lucide', 'x');
    } else {
      icon.setAttribute('data-lucide', 'menu');
    }
    lucide.createIcons();
  });

  // Close mobile menu on link click
  document.querySelectorAll('.mobile-nav-link').forEach(link => {
    link.addEventListener('click', () => {
      menuOpen = false;
      mobileMenu.classList.add('hidden');
      const icon = menuBtn.querySelector('[data-lucide]');
      icon.setAttribute('data-lucide', 'menu');
      lucide.createIcons();
    });
  });

  // ===== Intersection Observer for Reveal Animations =====
  const observerOptions = {
    root: null,
    rootMargin: '0px 0px -80px 0px',
    threshold: 0.1,
  };

  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');

        // Animate skill bars within the revealed element
        const skillBars = entry.target.querySelectorAll('.skill-bar');
        skillBars.forEach((bar) => {
          const parent = bar.closest('.skill-card');
          const skillLevel = parent ? parent.dataset.skill : 80;
          bar.style.width = skillLevel + '%';
          bar.style.transition = 'width 1.2s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
        });

        revealObserver.unobserve(entry.target);
      }
    });
  }, observerOptions);

  document.querySelectorAll('.reveal-element').forEach((el) => {
    revealObserver.observe(el);
  });

  // ===== Hero Grid/Particle Canvas =====
const canvas = document.getElementById('hero-grid');
const ctx = canvas.getContext('2d');

let animationId;
let particles = [];
let mouseX = 0;
let mouseY = 0;

function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  // IMPORTANT: rebuild particles on resize
  initParticles();
}

window.addEventListener('resize', resizeCanvas);

// Track mouse
window.addEventListener('mousemove', (e) => {
  mouseX = e.clientX;
  mouseY = e.clientY;
});

// Grid dot class
class GridDot {
  constructor() {
    this.reset();
  }

  reset() {
    this.x = Math.random() * canvas.width;
    this.y = Math.random() * canvas.height;
    this.size = Math.random() * 1.5 + 0.5;
    this.baseAlpha = Math.random() * 0.3 + 0.05;
    this.alpha = this.baseAlpha;
    this.drift = {
      x: (Math.random() - 0.5) * 0.3,
      y: (Math.random() - 0.5) * 0.3,
    };
  }

  update() {
    this.x += this.drift.x;
    this.y += this.drift.y;

    const dx = this.x - mouseX;
    const dy = this.y - mouseY;
    const dist = Math.sqrt(dx * dx + dy * dy);

    const maxDist = 200;

    if (dist < maxDist) {
      this.alpha = this.baseAlpha + (1 - dist / maxDist) * 0.4;
    } else {
      this.alpha += (this.baseAlpha - this.alpha) * 0.02;
    }

    if (this.x < -10) this.x = canvas.width + 10;
    if (this.x > canvas.width + 10) this.x = -10;
    if (this.y < -10) this.y = canvas.height + 10;
    if (this.y > canvas.height + 10) this.y = -10;
  }

  draw() {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(0, 212, 170, ${this.alpha})`;
    ctx.fill();
  }
}

// init / rebuild particles based on screen size
function initParticles() {
  particles = [];

  const particleCount = Math.min(
    Math.floor((canvas.width * canvas.height) / 8000),
    150
  );

  for (let i = 0; i < particleCount; i++) {
    particles.push(new GridDot());
  }
}

// connections
function drawConnections() {
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x;
      const dy = particles[i].y - particles[j].y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < 120) {
        const alpha = (1 - dist / 120) * 0.08;

        ctx.beginPath();
        ctx.moveTo(particles[i].x, particles[i].y);
        ctx.lineTo(particles[j].x, particles[j].y);
        ctx.strokeStyle = `rgba(0, 212, 170, ${alpha})`;
        ctx.lineWidth = 0.5;
        ctx.stroke();
      }
    }
  }
}

// animation loop
function animate() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  particles.forEach((p) => {
    p.update();
    p.draw();
  });

  drawConnections();
  animationId = requestAnimationFrame(animate);
}

// init
resizeCanvas();
initParticles();
animate();

  // ===== Contact Form Handler =====
  const contactForm = document.getElementById('contact-form');
  const formStatus = document.getElementById('form-status');

  contactForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const formData = new FormData(contactForm);
    const data = Object.fromEntries(formData.entries());

    // Validate
    if (!data.name || !data.email || !data.message) {
      formStatus.className = 'text-center text-sm font-medium py-3 rounded-xl bg-red-500/10 text-red-400 border border-red-500/20';
      formStatus.textContent = 'Please fill in all required fields.';
      formStatus.classList.remove('hidden');
      return;
    }

    // Simulate sending (ready for FastAPI integration)
    const submitBtn = contactForm.querySelector('button[type="submit"]');
    const originalContent = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="inline-flex items-center gap-2"><svg class="animate-spin w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>Sending...</span>';

    // Simulated API call — replace with real endpoint
    setTimeout(() => {
      formStatus.className = 'text-center text-sm font-medium py-3 rounded-xl bg-accent/10 text-accent border border-accent/20';
      formStatus.textContent = '✓ Message sent successfully! I\'ll get back to you soon.';
      formStatus.classList.remove('hidden');
      contactForm.reset();
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalContent;

      // Hide status after 5s
      setTimeout(() => {
        formStatus.classList.add('hidden');
      }, 5000);
    }, 1500);
  });

  // ===== Typing effect for hero (subtle) =====
  const heroTitle = document.querySelector('#hero h1');
  if (heroTitle) {
    heroTitle.style.opacity = '1';
  }

  // ===== Active nav link highlighting =====
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link');

  window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach((section) => {
      const sectionTop = section.offsetTop - 120;
      if (window.scrollY >= sectionTop) {
        current = section.getAttribute('id');
      }
    });

    navLinks.forEach((link) => {
      link.classList.remove('text-white', 'bg-white/5');
      if (link.getAttribute('href') === `#${current}`) {
        link.classList.add('text-white', 'bg-white/5');
      }
    });
  });

  // ===== Smooth scroll for anchor links =====
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
        });
      }
    });
  });
});