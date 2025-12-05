// Gestionnaire de thème complet pour Clara UI v2
// Basé sur l'ancien index.html avec toutes les variables CSS

const COLOR_MAP = {
  'sidebarBg': '--sidebar-bg',
  'sidebarText': '--sidebar-text',
  'sidebarBorder': '--sidebar-border',
  'headerBg': '--header-bg',
  'headerText': '--header-text',
  'headerBorder': '--header-border',
  'chatBg': '--chat-bg',
  'textColor': '--text-color',
  'timeColor': '--time-color',
  'jeremyBg': '--jeremy-bubble-bg',
  'jeremyBorder': '--jeremy-bubble-border',
  'jeremyText': '--jeremy-bubble-text',
  'claraBg': '--clara-bubble-bg',
  'claraBorder': '--clara-bubble-border',
  'claraText': '--clara-bubble-text',
  'inputAreaBg': '--input-area-bg',
  'inputBg': '--input-bg',
  'inputText': '--input-text',
  'inputBorder': '--input-border',
  'sendBtnBg': '--send-btn-bg',
  'sendBtnText': '--send-btn-text',
  'sendBtnBorder': '--send-btn-border',
  'rightPanelBg': '--right-panel-bg',
  'rightPanelHeaderBg': '--right-panel-header-bg',
  'rightPanelHeaderText': '--right-panel-header-text',
  'rightPanelBorder': '--right-panel-border',
  'todoBtnBg': '--todo-btn-bg',
  'todoBtnText': '--todo-btn-text',
  'todoBtnBorder': '--todo-btn-border',
  'settingsBtnBg': '--settings-btn-bg',
  'settingsBtnText': '--settings-btn-text',
  'settingsBtnBorder': '--settings-btn-border',
  'thinkBg': '--think-bg',
  'thinkHeaderBg': '--think-header-bg',
  'thinkHeaderText': '--think-header-text',
  'thinkBorder': '--think-border',
  'thinkText': '--think-text',
  'sidebarFooterBg': '--sidebar-footer-bg',
  'sidebarFooterBorder': '--sidebar-footer-border',
  'deleteAllBtnBg': '--delete-all-btn-bg',
  'deleteAllBtnText': '--delete-all-btn-text',
  'deleteAllBtnBorder': '--delete-all-btn-border',
  'newSessionBtnBg': '--new-session-btn-bg',
  'newSessionBtnText': '--new-session-btn-text',
  'newSessionBtnBorder': '--new-session-btn-border',
  'sidebarHeaderBg': '--sidebar-header-bg',
  'sidebarHeaderText': '--sidebar-header-text',
};

export const DEFAULT_THEME = {
  sidebarBg: '#ffffff',
  sidebarText: '#000000',
  sidebarBorder: '#dddddd',
  headerBg: '#ffffff',
  headerText: '#000000',
  headerBorder: '#eeeeee',
  chatBg: '#fafafa',
  textColor: '#000000',
  timeColor: '#666666',
  jeremyBg: '#d5f9c5',
  jeremyBorder: '#c7e8b5',
  jeremyText: '#000000',
  claraBg: '#ffffff',
  claraBorder: '#dddddd',
  claraText: '#000000',
  inputAreaBg: '#ffffff',
  inputBg: '#ffffff',
  inputText: '#000000',
  inputBorder: '#dddddd',
  sendBtnBg: '#007AFF',
  sendBtnText: '#ffffff',
  sendBtnBorder: '#007AFF',
  rightPanelBg: '#ffffff',
  rightPanelHeaderBg: '#ffffff',
  rightPanelHeaderText: '#000000',
  rightPanelBorder: '#dddddd',
  todoBtnBg: '#ffffff',
  todoBtnText: '#000000',
  todoBtnBorder: '#dddddd',
  settingsBtnBg: '#ffffff',
  settingsBtnText: '#000000',
  settingsBtnBorder: '#dddddd',
  thinkBg: '#ffffff',
  thinkHeaderBg: '#ffffff',
  thinkHeaderText: '#000000',
  thinkBorder: '#dddddd',
  thinkText: '#000000',
  sidebarFooterBg: '#ffffff',
  sidebarFooterBorder: '#dddddd',
  deleteAllBtnBg: '#ffffff',
  deleteAllBtnText: '#000000',
  deleteAllBtnBorder: '#dddddd',
  newSessionBtnBg: '#007AFF',
  newSessionBtnText: '#ffffff',
  newSessionBtnBorder: '#007AFF',
  sidebarHeaderBg: '#ffffff',
  sidebarHeaderText: '#000000',
  fontSize: '14',
};

export function loadThemeFromLocalStorage() {
  try {
    const saved = JSON.parse(localStorage.getItem('clara_colors') || '{}');
    if (Object.keys(saved).length > 0) {
      return { ...DEFAULT_THEME, ...saved };
    }
  } catch (e) {
    console.error('Error loading theme from localStorage:', e);
  }
  return DEFAULT_THEME;
}

export function saveThemeToLocalStorage(theme) {
  try {
    localStorage.setItem('clara_colors', JSON.stringify(theme));
  } catch (e) {
    console.error('Error saving theme to localStorage:', e);
  }
}

export function applyThemeToDocument(theme) {
  const root = document.documentElement;
  
  // Appliquer toutes les variables CSS
  Object.entries(COLOR_MAP).forEach(([key, cssVar]) => {
    if (theme[key]) {
      root.style.setProperty(cssVar, theme[key]);
    }
  });
  
  // Appliquer la taille de police
  if (theme.fontSize) {
    root.style.setProperty('--chat-font-size', theme.fontSize + 'px');
  }
}

// Charger et appliquer le thème au démarrage (avant le rendu React)
export function initTheme() {
  const theme = loadThemeFromLocalStorage();
  applyThemeToDocument(theme);
  return theme;
}

