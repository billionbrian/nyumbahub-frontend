/* ============================================
   THEME MANAGEMENT SYSTEM - JAVASCRIPT
   ============================================ */

const ThemeManager = {
  // Theme preference storage key
  STORAGE_KEY: 'themePreference',

  // Available themes
  THEMES: {
    SYSTEM: 'system',
    LIGHT: 'light',
    DARK: 'dark'
  },

  /**
   * Initialize the theme system
   */
  init() {
    this.applyTheme();
    this.setupSystemThemeListener();
    this.setupThemeSelector();
  },

  /**
   * Get the current theme preference from localStorage
   */
  getThemePreference() {
    const preference = localStorage.getItem(this.STORAGE_KEY);
    return preference || this.THEMES.SYSTEM;
  },

  /**
   * Save theme preference to localStorage
   */
  setThemePreference(theme) {
    localStorage.setItem(this.STORAGE_KEY, theme);
  },

  /**
   * Detect system theme preference
   */
  getSystemTheme() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return this.THEMES.DARK;
    }
    return this.THEMES.LIGHT;
  },

  /**
   * Get the effective theme (resolves 'system' to actual theme)
   */
  getEffectiveTheme() {
    const preference = this.getThemePreference();
    if (preference === this.THEMES.SYSTEM) {
      return this.getSystemTheme();
    }
    return preference;
  },

  /**
   * Apply the theme to the document
   */
  applyTheme() {
    const effectiveTheme = this.getEffectiveTheme();
    const html = document.documentElement;
    
    // Remove existing theme attribute
    html.removeAttribute('data-theme');
    
    // Apply dark theme if needed
    if (effectiveTheme === this.THEMES.DARK) {
      html.setAttribute('data-theme', 'dark');
    }
    
    // Update theme selector UI
    this.updateThemeSelectorUI();
  },

  /**
   * Set a specific theme
   */
  setTheme(theme) {
    this.setThemePreference(theme);
    this.applyTheme();
  },

  /**
   * Listen for system theme changes
   */
  setupSystemThemeListener() {
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      
      // Modern browsers
      if (mediaQuery.addEventListener) {
        mediaQuery.addEventListener('change', () => {
          if (this.getThemePreference() === this.THEMES.SYSTEM) {
            this.applyTheme();
          }
        });
      }
      // Legacy browsers
      else if (mediaQuery.addListener) {
        mediaQuery.addListener(() => {
          if (this.getThemePreference() === this.THEMES.SYSTEM) {
            this.applyTheme();
          }
        });
      }
    }
  },

  /**
   * Setup theme selector dropdown functionality
   */
  /**
   * Setup theme selector dropdown functionality
   */
  setupThemeSelector() {
    const themeBtn = document.querySelector('.theme-selector-btn');
    const themeDropdown = document.querySelector('.theme-dropdown');
    
    if (themeBtn && themeDropdown) {
      if (!themeBtn.dataset.themeBound) {
        themeBtn.dataset.themeBound = 'true';
        
        // Toggle dropdown
        themeBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          themeDropdown.classList.toggle('active');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
          if (!themeBtn.contains(e.target) && !themeDropdown.contains(e.target)) {
            themeDropdown.classList.remove('active');
          }
        });
      }

      // Handle desktop theme selection
      const dropdownItems = themeDropdown.querySelectorAll('.theme-dropdown-item');
      dropdownItems.forEach(item => {
        if (!item.dataset.bound) {
          item.dataset.bound = 'true';
          item.addEventListener('click', (e) => {
            e.stopPropagation();
            const theme = item.dataset.theme;
            this.setTheme(theme);
            themeDropdown.classList.remove('active');
          });
        }
      });
    }

    // Handle mobile theme options (segmented pill buttons)
    const mobileOptions = document.querySelectorAll('.mobile-theme-option');
    mobileOptions.forEach(option => {
      if (!option.dataset.bound) {
        option.dataset.bound = 'true';
        option.addEventListener('click', (e) => {
          e.stopPropagation();
          const theme = option.dataset.theme;
          this.setTheme(theme);
        });
      }
    });

    this.updateThemeSelectorUI();
  },

  /**
   * Update theme selector UI to reflect current preference
   */
  updateThemeSelectorUI() {
    const preference = this.getThemePreference();
    
    // Update desktop dropdown
    const dropdownItems = document.querySelectorAll('.theme-dropdown-item');
    dropdownItems.forEach(item => {
      item.classList.remove('selected');
      if (item.dataset.theme === preference) {
        item.classList.add('selected');
      }
    });

    // Update mobile options
    const mobileOptions = document.querySelectorAll('.mobile-theme-option');
    mobileOptions.forEach(option => {
      option.classList.remove('selected');
      if (option.dataset.theme === preference) {
        option.classList.add('selected');
      }
    });

    // Update button text/icon
    const themeBtn = document.querySelector('.theme-selector-btn');
    if (themeBtn) {
      const btnText = themeBtn.querySelector('.theme-btn-text');
      const btnIcon = themeBtn.querySelector('.theme-btn-icon');
      
      if (btnText) {
        const themeNames = {
          system: 'System',
          light: 'Light',
          dark: 'Dark'
        };
        btnText.textContent = themeNames[preference] || 'System';
      }
      
      if (btnIcon) {
        const themeSVGs = {
          system: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>',
          light: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>',
          dark: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>'
        };
        btnIcon.innerHTML = themeSVGs[preference] || themeSVGs.system;
      }
    }
  }
};

// Initialize theme system when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => ThemeManager.init());
} else {
  ThemeManager.init();
}

// Make ThemeManager available globally for manual theme switching
window.ThemeManager = ThemeManager;
