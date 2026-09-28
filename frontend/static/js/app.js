/**
 * CyberQuest — Command Center Application Controller
 */

// Toast Notifications
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Diagnostic Assessment Questions
const DIAGNOSTIC_QUESTIONS = [
  {
    topic: "Networking",
    question: "Which transport protocol provides reliable, connection-oriented data transfer via a 3-way handshake?",
    options: ["UDP", "TCP", "ICMP", "ARP"],
    answer: "TCP"
  },
  {
    topic: "Linux",
    question: "Which Linux utility changes read, write, and execute permissions on a filesystem object?",
    options: ["chown", "chmod", "ps", "ls -l"],
    answer: "chmod"
  },
  {
    topic: "Windows",
    question: "Which Windows administrative tool is primary for reviewing authentication logon events and security audit logs?",
    options: ["Event Viewer", "Registry Editor", "Task Manager", "Device Manager"],
    answer: "Event Viewer"
  },
  {
    topic: "Web Security",
    question: "Which cookie flag instructs the web browser to block client-side JavaScript from accessing session tokens?",
    options: ["SameSite=Strict", "HttpOnly", "Secure", "Domain"],
    answer: "HttpOnly"
  },
  {
    topic: "Security Fundamentals",
    question: "Which core principle states that an entity should possess only the absolute minimum permissions required to perform its function?",
    options: ["Defense in Depth", "Least Privilege", "Fail-Safe Defaults", "Separation of Duties"],
    answer: "Least Privilege"
  },
  {
    topic: "Cryptography",
    question: "What is the primary fundamental difference between encryption and cryptographic hashing?",
    options: [
      "Hashing is reversible with a private key; encryption is not",
      "Hashing is a one-way irreversible transformation; encryption is reversible with the proper key",
      "Encryption produces fixed-length outputs; hashing produces variable-length outputs",
      "There is no difference; they are synonymous"
    ],
    answer: "Hashing is a one-way irreversible transformation; encryption is reversible with the proper key"
  },
  {
    topic: "Authentication",
    question: "What is the core distinction between Authentication (AuthN) and Authorization (AuthZ)?",
    options: [
      "Authentication verifies who you are; Authorization determines what you are allowed to access",
      "Authentication controls file permissions; Authorization validates passwords",
      "Authentication happens after authorization",
      "They are identical security concepts"
    ],
    answer: "Authentication verifies who you are; Authorization determines what you are allowed to access"
  },
  {
    topic: "Operating Systems",
    question: "In standard OS architecture, what separates user applications from having direct unrestricted access to hardware?",
    options: [
      "User Mode vs. Kernel Mode privilege rings",
      "The swap partition",
      "The command shell",
      "The filesystem inode table"
    ],
    answer: "User Mode vs. Kernel Mode privilege rings"
  }
];

// App Initialization
document.addEventListener('DOMContentLoaded', async () => {
  setupNavigation();
  setupAuthModals();
  await checkSession();
});

// Setup Navigation Clicks
function setupNavigation() {
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const viewName = item.getAttribute('data-view');
      switchView(viewName);
    });
  });
}

function switchView(viewName) {
  // Update sidebar active state
  document.querySelectorAll('.nav-item').forEach(item => {
    if (item.getAttribute('data-view') === viewName) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  // Switch view section visibility
  document.querySelectorAll('.view-section').forEach(section => {
    if (section.id === `view-${viewName}`) {
      section.classList.add('active');
    } else {
      section.classList.remove('active');
    }
  });

  state.setActiveView(viewName);

  // Trigger view renderers
  if (viewName === 'dashboard') renderDashboard();
  if (viewName === 'learning-path') renderLearningPath();
  if (viewName === 'analytics') renderAnalytics();
  if (viewName === 'profile') renderProfile();
}

// Session & Authentication Handling
async function checkSession() {
  try {
    const data = await API.getMe();
    if (data.authenticated && data.user) {
      state.setUser(data.user);
      updateUserUI(data.user);
      await loadNavState();
      
      // Check if diagnostic assessment needed
      if (!data.user.diagnostic_completed) {
        openDiagnosticModal();
      } else {
        switchView('dashboard');
      }
    } else {
      state.setUser(null);
      openAuthModal('login');
    }
  } catch (err) {
    console.error('Session check failed:', err);
    openAuthModal('login');
  }
}

function updateUserUI(user) {
  const nameEl = document.getElementById('topbar-user-name');
  const pathBadge = document.getElementById('topbar-path-badge');
  const sideNameEl = document.getElementById('sidebar-user-name');
  const sidePathEl = document.getElementById('sidebar-user-path');

  if (nameEl) nameEl.textContent = user.name;
  if (sideNameEl) sideNameEl.textContent = user.name;
  if (sidePathEl) sidePathEl.textContent = user.current_path;

  if (pathBadge) {
    pathBadge.textContent = user.current_path;
    pathBadge.className = 'track-badge';
    if (user.current_path === 'Red Team') pathBadge.classList.add('red-team');
    if (user.current_path === 'Blue Team') pathBadge.classList.add('blue-team');
  }

  // Logout button event
  const logoutBtn = document.getElementById('btn-logout');
  if (logoutBtn) {
    logoutBtn.onclick = async () => {
      try {
        await API.logout();
        state.setUser(null);
        showToast('Logged out of CyberQuest.', 'info');
        openAuthModal('login');
      } catch (e) {
        showToast('Logout failed', 'error');
      }
    };
  }
}

async function loadNavState() {
  try {
    const navState = await API.getNavState();
    state.setNavState(navState);
    renderDashboard();
  } catch (err) {
    console.error('Failed to load navigation state:', err);
  }
}

// Setup Auth & Modals
function setupAuthModals() {
  // Switch between login & register
  const switchRegisterLink = document.getElementById('link-to-register');
  const switchLoginLink = document.getElementById('link-to-login');

  if (switchRegisterLink) {
    switchRegisterLink.addEventListener('click', (e) => {
      e.preventDefault();
      openAuthModal('register');
    });
  }

  if (switchLoginLink) {
    switchLoginLink.addEventListener('click', (e) => {
      e.preventDefault();
      openAuthModal('login');
    });
  }

  // Handle Login Submission
  const loginForm = document.getElementById('form-login');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const identifier = document.getElementById('login-identifier').value.trim();
      const password = document.getElementById('login-password').value;

      try {
        const res = await API.login(identifier, password);
        closeModal('modal-auth');
        state.setUser(res.user);
        updateUserUI(res.user);
        showToast(`Welcome, ${res.user.name}`, 'success');
        await loadNavState();
        if (!res.user.diagnostic_completed) {
          openDiagnosticModal();
        } else {
          switchView('dashboard');
        }
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // Handle Registration Submission
  const registerForm = document.getElementById('form-register');
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        name: document.getElementById('reg-name').value.trim(),
        username: document.getElementById('reg-username').value.trim(),
        email: document.getElementById('reg-email').value.trim(),
        password: document.getElementById('reg-password').value,
        experience_level: document.getElementById('reg-exp-level').value,
        linux_exp: document.getElementById('reg-linux-exp').value,
        networking_exp: document.getElementById('reg-net-exp').value,
        programming_exp: document.getElementById('reg-prog-exp').value,
        security_exp: document.getElementById('reg-sec-exp').value,
        preferred_path: document.getElementById('reg-preferred-path').value
      };

      try {
        const res = await API.register(payload);
        closeModal('modal-auth');
        state.setUser(res.user);
        updateUserUI(res.user);
        showToast('Profile created. Starting diagnostic assessment...', 'success');
        openDiagnosticModal();
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }
}

function openAuthModal(mode = 'login') {
  const modal = document.getElementById('modal-auth');
  const loginPane = document.getElementById('auth-pane-login');
  const registerPane = document.getElementById('auth-pane-register');
  const modalTitle = document.getElementById('auth-modal-title');

  if (mode === 'login') {
    loginPane.style.display = 'block';
    registerPane.style.display = 'none';
    modalTitle.textContent = 'Command Center Authentication';
  } else {
    loginPane.style.display = 'none';
    registerPane.style.display = 'block';
    modalTitle.textContent = 'Learner Registration & Onboarding';
  }

  modal.classList.add('active');
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove('active');
}

// Diagnostic Assessment Modal Logic
let currentDiagIndex = 0;
const diagnosticAnswers = {};

function openDiagnosticModal() {
  currentDiagIndex = 0;
  const modal = document.getElementById('modal-diagnostic');
  modal.classList.add('active');
  renderDiagnosticStep();
}

function renderDiagnosticStep() {
  const container = document.getElementById('diagnostic-content');
  const total = DIAGNOSTIC_QUESTIONS.length;
  
  if (currentDiagIndex >= total) {
    finishDiagnostic();
    return;
  }

  const q = DIAGNOSTIC_QUESTIONS[currentDiagIndex];
  container.innerHTML = `
    <div style="margin-bottom: 12px; font-family: var(--font-mono); font-size: 12px; color: var(--accent-cyan); display: flex; justify-content: space-between;">
      <span>DIAGNOSTIC TOPIC: ${q.topic.toUpperCase()}</span>
      <span>QUESTION ${currentDiagIndex + 1} OF ${total}</span>
    </div>
    <h3 style="font-size: 16px; margin-bottom: 20px; color: var(--text-primary); font-weight: 600;">${q.question}</h3>
    <div style="display: flex; flex-direction: column; gap: 10px;">
      ${q.options.map(opt => `
        <button class="btn btn-secondary diag-opt-btn" style="text-align: left; justify-content: flex-start; padding: 12px 16px; font-family: var(--font-sans);" data-answer="${opt.replace(/"/g, '&quot;')}">
          ${opt}
        </button>
      `).join('')}
    </div>
  `;

  container.querySelectorAll('.diag-opt-btn').forEach(btn => {
    btn.onclick = () => {
      const selected = btn.getAttribute('data-answer');
      const isCorrect = selected === q.answer;
      diagnosticAnswers[q.topic] = isCorrect ? 45.0 : 15.0; // Baseline topic mastery
      currentDiagIndex++;
      renderDiagnosticStep();
    };
  });
}

async function finishDiagnostic() {
  const container = document.getElementById('diagnostic-content');
  container.innerHTML = `
    <div style="text-align: center; padding: 24px 0;">
      <h3 style="color: var(--accent-emerald); font-size: 18px; margin-bottom: 12px;">Diagnostic Assessment Complete</h3>
      <p style="color: var(--text-secondary); font-size: 14px; margin-bottom: 20px;">
        Synthesizing baseline topic mastery profile. Calibrating adaptive learning engine...
      </p>
      <button id="btn-save-diag" class="btn btn-primary">Enter Training Environment</button>
    </div>
  `;

  document.getElementById('btn-save-diag').onclick = async () => {
    try {
      await API.submitDiagnostic(diagnosticAnswers);
      closeModal('modal-diagnostic');
      showToast('Baseline knowledge profile established.', 'success');
      const user = state.state.user;
      if (user) user.diagnostic_completed = true;
      await loadNavState();
      switchView('dashboard');
    } catch (e) {
      showToast('Failed to save assessment', 'error');
    }
  };
}

// View Renderers
function renderDashboard() {
  const navState = state.state.navState;
  const user = state.state.user;
  if (!navState || !user) return;

  // 1. Where am I?
  const currentPathEl = document.getElementById('dash-current-path');
  if (currentPathEl) currentPathEl.textContent = user.current_path;

  // 2. Weak, Medium, Strong Mastery Lists
  const weakContainer = document.getElementById('dash-weak-topics');
  if (weakContainer) {
    if (navState.weak_topics.length === 0) {
      weakContainer.innerHTML = '<div style="color: var(--text-muted); font-size: 13px;">No critically weak topics detected.</div>';
    } else {
      weakContainer.innerHTML = navState.weak_topics.map(t => `
        <div class="mastery-row">
          <span class="mastery-name">${t.name}</span>
          <div class="mastery-bar-container">
            <div class="mastery-bar-fill weak" style="width: ${t.mastery}%"></div>
          </div>
          <span class="mastery-score">${t.mastery}%</span>
        </div>
      `).join('');
    }
  }

  const mediumContainer = document.getElementById('dash-medium-topics');
  if (mediumContainer) {
    if (navState.medium_topics.length === 0) {
      mediumContainer.innerHTML = '<div style="color: var(--text-muted); font-size: 13px;">No medium topics.</div>';
    } else {
      mediumContainer.innerHTML = navState.medium_topics.map(t => `
        <div class="mastery-row">
          <span class="mastery-name">${t.name}</span>
          <div class="mastery-bar-container">
            <div class="mastery-bar-fill medium" style="width: ${t.mastery}%"></div>
          </div>
          <span class="mastery-score">${t.mastery}%</span>
        </div>
      `).join('');
    }
  }

  // 3. What should I learn next?
  const nextLessonEl = document.getElementById('dash-next-lesson');
  const nextReasonEl = document.getElementById('dash-next-reason');
  if (nextLessonEl && nextReasonEl) {
    if (navState.weak_topics.length > 0) {
      const topWeak = navState.weak_topics[0];
      nextLessonEl.textContent = `Targeted Revision: ${topWeak.name}`;
      nextReasonEl.textContent = `Adaptive Engine Flag: Mastery score is ${topWeak.mastery}% (below 40% threshold). Relearning fundamentals and targeted practice are recommended before advancing.`;
    } else {
      nextLessonEl.textContent = `Cybersecurity Foundations: Networking Protocols`;
      nextReasonEl.textContent = `Adaptive Engine Flag: Standard curriculum progression. Foundations form the prerequisite bedrock for ${user.preferred_path || 'specialization'}.`;
    }
  }
}

function renderLearningPath() {
  const user = state.state.user;
  if (!user) return;

  const currentPathDisplay = document.getElementById('lp-current-path-name');
  if (currentPathDisplay) currentPathDisplay.textContent = user.current_path;

  // Track switcher buttons
  document.querySelectorAll('.btn-switch-track').forEach(btn => {
    btn.onclick = async () => {
      const targetPath = btn.getAttribute('data-track');
      try {
        await API.switchPath(targetPath);
        user.current_path = targetPath;
        updateUserUI(user);
        renderLearningPath();
        showToast(`Learning track updated to ${targetPath}`, 'info');
      } catch (e) {
        showToast(e.message, 'error');
      }
    };
  });
}

function renderAnalytics() {
  const navState = state.state.navState;
  if (!navState) return;

  const listContainer = document.getElementById('analytics-mastery-list');
  if (!listContainer) return;

  const allTopics = [...navState.weak_topics, ...navState.medium_topics, ...navState.strong_topics];
  if (allTopics.length === 0) {
    listContainer.innerHTML = '<div style="color: var(--text-muted); font-size: 13px; padding: 12px 0;">No topic mastery data recorded yet. Complete diagnostic or practice exercises.</div>';
    return;
  }

  listContainer.innerHTML = allTopics.map(t => {
    let barClass = 'weak';
    if (t.mastery >= 70) barClass = 'strong';
    else if (t.mastery >= 40) barClass = 'medium';

    return `
      <div class="mastery-row">
        <div>
          <div class="mastery-name">${t.name}</div>
          <div style="font-size: 11px; color: var(--text-muted); font-family: var(--font-mono);">${t.category}</div>
        </div>
        <div class="mastery-bar-container">
          <div class="mastery-bar-fill ${barClass}" style="width: ${t.mastery}%"></div>
        </div>
        <span class="mastery-score">${t.mastery}%</span>
      </div>
    `;
  }).join('');
}

function renderProfile() {
  const user = state.state.user;
  if (!user) return;

  document.getElementById('profile-name').value = user.name;
  document.getElementById('profile-username').value = user.username;
  document.getElementById('profile-email').value = user.email;
  document.getElementById('profile-exp-level').value = user.experience_level;
  document.getElementById('profile-linux-exp').value = user.linux_exp;
  document.getElementById('profile-net-exp').value = user.networking_exp;
  document.getElementById('profile-prog-exp').value = user.programming_exp;
  document.getElementById('profile-sec-exp').value = user.security_exp;
  document.getElementById('profile-preferred-path').value = user.preferred_path;

  const form = document.getElementById('form-update-profile');
  if (form) {
    form.onsubmit = async (e) => {
      e.preventDefault();
      const updates = {
        name: document.getElementById('profile-name').value.trim(),
        experience_level: document.getElementById('profile-exp-level').value,
        linux_exp: document.getElementById('profile-linux-exp').value,
        networking_exp: document.getElementById('profile-net-exp').value,
        programming_exp: document.getElementById('profile-prog-exp').value,
        security_exp: document.getElementById('profile-sec-exp').value,
        preferred_path: document.getElementById('profile-preferred-path').value
      };

      try {
        const res = await API.updateProfile(updates);
        state.setUser(res.user);
        updateUserUI(res.user);
        showToast('Profile updated successfully.', 'success');
      } catch (err) {
        showToast(err.message, 'error');
      }
    };
  }
}
