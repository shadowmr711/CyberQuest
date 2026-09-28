/**
 * CyberQuest API Client
 * Wraps browser fetch with credentials, JSON handling, and unified error parsing.
 */
const API = {
  async request(endpoint, options = {}) {
    const url = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    
    const defaultHeaders = {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers
      },
      credentials: 'same-origin' // Ensures session cookie travels with requests
    };

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(url, config);
      const isJson = (response.headers.get('content-type') || '').includes('application/json');
      const data = isJson ? await response.json() : await response.text();

      if (!response.ok) {
        const errorMsg = (data && data.error) || response.statusText || 'Request failed';
        const error = new Error(errorMsg);
        error.status = response.status;
        error.code = data && data.code;
        error.data = data;
        throw error;
      }

      return data;
    } catch (err) {
      console.error(`[API Error] ${options.method || 'GET'} ${url}:`, err);
      throw err;
    }
  },

  // Auth endpoints
  async register(payload) {
    return this.request('/api/auth/register', { method: 'POST', body: payload });
  },

  async login(usernameOrEmail, password) {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: { username_or_email: usernameOrEmail, password }
    });
  },

  async logout() {
    return this.request('/api/auth/logout', { method: 'POST' });
  },

  async getMe() {
    return this.request('/api/auth/me');
  },

  // User endpoints
  async getProfile() {
    return this.request('/api/user/profile');
  },

  async updateProfile(updates) {
    return this.request('/api/user/profile', { method: 'PUT', body: updates });
  },

  async switchPath(pathName) {
    return this.request('/api/user/path', { method: 'POST', body: { path: pathName } });
  },

  async submitDiagnostic(scores) {
    return this.request('/api/user/diagnostic', { method: 'POST', body: { scores } });
  },

  // Navigation snapshot
  async getNavState() {
    return this.request('/api/navigation/state');
  }
};
