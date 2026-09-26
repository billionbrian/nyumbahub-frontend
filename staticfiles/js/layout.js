// ============================================
// LAYOUT COMPONENT LOADER
// ============================================

const LayoutLoader = {
  /**
   * Load shared components into the page
   */
  async loadComponents() {
    try {
      // Load navbar
      const navbarPlaceholder = document.getElementById('navbar');
      if (navbarPlaceholder) {
        const navbarResponse = await fetch('components/navbar.html');
        if (navbarResponse.ok) {
          const navbarHTML = await navbarResponse.text();
          navbarPlaceholder.innerHTML = navbarHTML;
          // Critical: tell HTMX to scan the newly injected navbar for hx-* attributes
          if (window.htmx) window.htmx.process(navbarPlaceholder);
        } else {
          console.error('Failed to load navbar:', navbarResponse.status);
        }
      }

      // Load footer
      const footerPlaceholder = document.getElementById('footer');
      if (footerPlaceholder) {
        const footerResponse = await fetch('components/footer.html');
        if (footerResponse.ok) {
          const footerHTML = await footerResponse.text();
          footerPlaceholder.innerHTML = footerHTML;
          // Critical: tell HTMX to scan the newly injected footer for hx-* attributes
          if (window.htmx) window.htmx.process(footerPlaceholder);
        } else {
          console.error('Failed to load footer:', footerResponse.status);
        }
      }

      // Initialize mobile navigation rail after components are loaded
      this.initializeMobileMenu();

      // Update bottom nav & rail auth buttons if authenticated
      this.syncAuthBottomNav();

      // Set active link based on current page
      this.setActiveLink();

      // Trigger auth UI update if auth.js is loaded
      if (typeof updateAuthUI === 'function') {
        updateAuthUI();
      }

      // Re-initialize theme selector after navbar is injected
      if (window.ThemeManager) {
        setTimeout(() => {
          window.ThemeManager.setupThemeSelector();
          window.ThemeManager.updateThemeSelectorUI();
        }, 50);
      }
    } catch (error) {
      console.error('Error loading layout components:', error);
    }
  },

  /**
   * Sync bottom navigation account tab & mobile rail footer with user authentication state
   */
  syncAuthBottomNav() {
    const token = localStorage.getItem('token');
    const bottomNavAccount = document.getElementById('bottomNavAccount');
    const bottomNavAccountLabel = document.getElementById('bottomNavAccountLabel');
    const mobileRailAuth = document.getElementById('mobileRailAuth');

    if (token) {
      if (bottomNavAccount) {
        bottomNavAccount.href = 'account.html';
        bottomNavAccount.dataset.nav = 'account.html';
      }
      if (bottomNavAccountLabel) {
        bottomNavAccountLabel.textContent = 'Profile';
      }
      if (mobileRailAuth) {
        mobileRailAuth.innerHTML = `
          <a href="account.html" class="login-btn">My Profile</a>
          <a href="#" class="signup-btn" onclick="event.preventDefault(); localStorage.removeItem('token'); localStorage.removeItem('user'); window.location.href='login.html';">Sign Out</a>
        `;
      }
    }
  },

  /**
   * Initialize mobile navigation rail (drawer) functionality
   */
  initializeMobileMenu() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileMenuBackdrop = document.getElementById('mobileMenuBackdrop');
    const mobileRailClose = document.getElementById('mobileRailClose');

    const closeRail = () => {
      if (mobileMenu) mobileMenu.classList.remove('active');
      if (mobileMenuBackdrop) mobileMenuBackdrop.classList.remove('active');
      if (mobileMenuBtn) {
        mobileMenuBtn.classList.remove('active');
        mobileMenuBtn.setAttribute('aria-expanded', 'false');
      }
      document.body.style.overflow = '';
    };

    const toggleRail = (e) => {
      if (e) e.stopPropagation();
      if (!mobileMenu) return;
      const isOpen = mobileMenu.classList.toggle('active');
      if (mobileMenuBackdrop) mobileMenuBackdrop.classList.toggle('active', isOpen);
      if (mobileMenuBtn) {
        mobileMenuBtn.classList.toggle('active', isOpen);
        mobileMenuBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      }
      document.body.style.overflow = isOpen ? 'hidden' : '';
    };

    if (mobileMenuBtn && mobileMenu) {
      mobileMenuBtn.removeAttribute('onclick');
      mobileMenuBtn.addEventListener('click', toggleRail);
    }

    if (mobileRailClose) {
      mobileRailClose.addEventListener('click', closeRail);
    }

    if (mobileMenuBackdrop) {
      mobileMenuBackdrop.addEventListener('click', closeRail);
    }

    // Close rail when pressing Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && mobileMenu && mobileMenu.classList.contains('active')) {
        closeRail();
      }
    });
  },

  /**
   * Set active navigation link based on current page
   */
  setActiveLink() {
    const currentPath = window.location.pathname;
    const currentFile = currentPath.split('/').pop() || 'index.html';

    // Top nav & mobile rail links
    const navLinks = document.querySelectorAll('#navMenu a, #mobileMenu .mobile-rail-link, #mobileMenu .mobile-rail-sublink');
    navLinks.forEach(link => {
      link.classList.remove('active');
      const linkFile = (link.getAttribute('href') || '').split('?')[0];
      if (
        linkFile === currentFile ||
        (currentFile === '' && linkFile === 'index.html') ||
        (link.id === 'desktopNavProfile' && ['account.html', 'login.html', 'signup.html'].includes(currentFile))
      ) {
        link.classList.add('active');
      }
    });

    // Mobile bottom navigation items
    const bottomNavItems = document.querySelectorAll('#mobileBottomNav .bottom-nav-item');
    bottomNavItems.forEach(item => {
      item.classList.remove('active');
      const targetNav = item.dataset.nav || item.getAttribute('href');
      if (
        targetNav === currentFile ||
        (item.id === 'bottomNavAccount' && ['login.html', 'signup.html', 'account.html'].includes(currentFile))
      ) {
        item.classList.add('active');
      }
    });
  }
};

// ============================================
// GLOBAL MOBILE MENU FUNCTION (for compatibility)
// ============================================
function toggleMobileMenu() {
  const mobileMenu = document.getElementById('mobileMenu');
  const mobileMenuBackdrop = document.getElementById('mobileMenuBackdrop');
  const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
  if (mobileMenu) {
    const isOpen = mobileMenu.classList.toggle('active');
    if (mobileMenuBackdrop) mobileMenuBackdrop.classList.toggle('active', isOpen);
    if (mobileMenuBtn) mobileMenuBtn.classList.toggle('active', isOpen);
    document.body.style.overflow = isOpen ? 'hidden' : '';
  }
}

// ============================================
// INITIALIZE LAYOUT
// ============================================
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => LayoutLoader.loadComponents());
} else {
  LayoutLoader.loadComponents();
}

// ============================================
// HTMX LIFECYCLE HANDLERS
// ============================================

/**
 * After every HTMX swap: scroll to top, update active links, close mobile rail,
 * reset overflow locks, and invoke the page-specific initializer.
 */
document.addEventListener('htmx:afterSwap', function(evt) {
  const swap = document.getElementById('content-swap');
  const isSwapTarget = evt.detail.target && (
    evt.detail.target.id === 'content-swap' ||
    (evt.detail.target.classList && evt.detail.target.classList.contains('content-swap')) ||
    evt.detail.target === swap
  );
  if (!isSwapTarget) return;

  // Unconditionally unlock scrolling on body and document element
  document.body.style.overflow = '';
  document.documentElement.style.overflow = '';

  // Explicitly scroll to top — don't rely on HTMX's show: modifier alone
  window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;

  // Determine current page from URL
  const currentPath = window.location.pathname;
  const currentFile = currentPath.split('/').pop() || 'index.html';
  const pageKey = (currentFile.replace('.html', '') || 'index').split('?')[0];

  // Update data-page on #content-swap so scoped styles (like map) work accurately
  if (swap) {
    swap.setAttribute('data-page', pageKey);
  }

  // Update active nav link
  LayoutLoader.setActiveLink();

  // Close mobile rail drawer if open
  const mobileMenu = document.getElementById('mobileMenu');
  const mobileMenuBackdrop = document.getElementById('mobileMenuBackdrop');
  const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
  if (mobileMenu && mobileMenu.classList.contains('active')) {
    mobileMenu.classList.remove('active');
    if (mobileMenuBackdrop) mobileMenuBackdrop.classList.remove('active');
    if (mobileMenuBtn) {
      mobileMenuBtn.classList.remove('active');
      mobileMenuBtn.setAttribute('aria-expanded', 'false');
    }
  }

  // Close any modal backdrops or lightboxes that might have lingered
  const lightbox = document.getElementById('lightbox');
  if (lightbox) lightbox.classList.remove('active');
  const filterModal = document.getElementById('filterModal');
  if (filterModal) filterModal.classList.remove('active');

  // Trigger page-specific initializer
  if (pageKey && window.PageInitializers && typeof window.PageInitializers[pageKey] === 'function') {
    window.PageInitializers[pageKey]();
  }
});

/**
 * History restore (browser back/forward): re-run page init because
 * content is pulled from the HTMX history cache and scripts don't re-run.
 */
document.addEventListener('htmx:historyRestore', function() {
  document.body.style.overflow = '';
  document.documentElement.style.overflow = '';
  window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;

  const currentPath = window.location.pathname;
  const currentFile = currentPath.split('/').pop() || 'index.html';
  const pageKey = (currentFile.replace('.html', '') || 'index').split('?')[0];

  const swap = document.getElementById('content-swap');
  if (swap) {
    swap.setAttribute('data-page', pageKey);
  }

  if (pageKey && window.PageInitializers && typeof window.PageInitializers[pageKey] === 'function') {
    window.PageInitializers[pageKey]();
  }
  LayoutLoader.setActiveLink();
});

