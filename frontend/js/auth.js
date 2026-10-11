'use strict';

(() => {
  const ACCOUNTS_KEY = 'nature-club-lms-accounts';
  const SESSION_KEY = 'nature-club-lms-session';
  const DASHBOARDS = {
    admin: 'admin-dashboard.html',
    instructor: 'instructor-dashboard.html',
    student: 'student-dashboard.html'
  };

  function demoAccounts() {
    return (window.NATURE_CLUB_DEMO_CREDENTIALS || []).map(account => ({
      ...account,
      name: account.role === 'admin' ? 'Nature Club Admin' : `Demo ${account.role}`,
      phone: '',
      dashboard: DASHBOARDS[account.role],
      status: 'active'
    }));
  }

  function loadAccounts() {
    let accounts = [];
    try {
      const saved = JSON.parse(localStorage.getItem(ACCOUNTS_KEY) || '[]');
      if (Array.isArray(saved)) accounts = saved;
    } catch {
      accounts = [];
    }

    let changed = false;
    const emails = new Set(accounts.map(account => account.email));
    demoAccounts().forEach(account => {
      if (!emails.has(account.email)) {
        accounts.push(account);
        changed = true;
      }
    });

    if (changed) {
      try {
        localStorage.setItem(ACCOUNTS_KEY, JSON.stringify(accounts));
      } catch {
        // Demo accounts remain available in memory when storage is disabled.
      }
    }
    return accounts;
  }

  function showMessage(form, message) {
    const element = form.querySelector('[data-auth-message]');
    if (!element) return;
    element.textContent = message;
    element.hidden = !message;
  }

  function saveSession(account) {
    try {
      localStorage.setItem(SESSION_KEY, JSON.stringify({
        email: account.email,
        name: account.name,
        role: account.role,
        dashboard: account.dashboard
      }));
      return true;
    } catch {
      return false;
    }
  }

  function redirectToDashboard(account) {
    if (!saveSession(account)) return false;
    window.location.href = account.dashboard || DASHBOARDS[account.role];
    return true;
  }

  function handleLogin(form) {
    form.addEventListener('submit', event => {
      event.preventDefault();
      const email = form.elements.email.value.trim().toLowerCase();
      const password = form.elements.password.value;
      const account = loadAccounts().find(user =>
        user.email.toLowerCase() === email && user.password === password
      );

      if (!account) {
        showMessage(form, 'The email or password is incorrect.');
        return;
      }
      if (!redirectToDashboard(account)) {
        showMessage(form, 'Browser storage is unavailable, so sign-in could not be completed.');
      }
    });
  }

  function handleRegistration(form) {
    form.addEventListener('submit', event => {
      event.preventDefault();

      const formData = new FormData(form);
      const email = form.elements.email.value.trim().toLowerCase();
      const role = formData.get('role');
      const account = {
        name: form.elements.fullname.value.trim(),
        email,
        phone: form.elements.phone.value.trim(),
        password: form.elements.password.value,
        role,
        dashboard: DASHBOARDS[role],
        status: 'active'
      };

      if (!DASHBOARDS[role] || !account.name || !email) {
        showMessage(form, 'Enter your name, a valid email, and select an account type.');
        return;
      }

      const accounts = loadAccounts();
      if (accounts.some(user => user.email.toLowerCase() === email)) {
        showMessage(form, 'An account with this email already exists. Sign in instead.');
        return;
      }

      accounts.push(account);
      try {
        localStorage.setItem(ACCOUNTS_KEY, JSON.stringify(accounts));
      } catch {
        showMessage(form, 'Browser storage is unavailable, so your account could not be saved.');
        return;
      }

      if (!redirectToDashboard(account)) {
        showMessage(form, 'Your account was created, but browser storage is unavailable for sign-in.');
      }
    });
  }

  function init() {
    loadAccounts();
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    if (loginForm) handleLogin(loginForm);
    if (registerForm) handleRegistration(registerForm);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();