import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/global.css'
import './styles/layout.css'
import { initTheme } from './config/themeManager'

// Charger et appliquer le thème AVANT le rendu React (évite le flash)
initTheme()

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

