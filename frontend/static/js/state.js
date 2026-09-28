/**
 * CyberQuest State Manager
 * Central store for user profile, active navigation, and UI state.
 */
class StateManager {
  constructor() {
    this.state = {
      user: null,
      isAuthenticated: false,
      activeView: 'dashboard',
      navState: null,
      isLoading: false
    };
    this.listeners = [];
  }

  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  notify() {
    for (const listener of this.listeners) {
      listener(this.state);
    }
  }

  setUser(user) {
    this.state.user = user;
    this.state.isAuthenticated = !!user;
    this.notify();
  }

  setActiveView(viewName) {
    this.state.activeView = viewName;
    this.notify();
  }

  setNavState(navState) {
    this.state.navState = navState;
    this.notify();
  }

  setLoading(isLoading) {
    this.state.isLoading = isLoading;
    this.notify();
  }
}

const state = new StateManager();
