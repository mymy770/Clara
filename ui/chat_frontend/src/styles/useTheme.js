import { useState, useEffect } from 'react'
import { themes } from '../config/theme'

export function useTheme() {
  const [theme, setThemeState] = useState(() => {
    // Récupérer depuis localStorage ou utiliser 'dark' par défaut
    const saved = localStorage.getItem('clara-theme')
    return saved && themes[saved] ? saved : 'dark'
  })

  useEffect(() => {
    // Sauvegarder dans localStorage
    localStorage.setItem('clara-theme', theme)
    
    // Appliquer les variables CSS
    const root = document.documentElement
    const themeColors = themes[theme]
    
    Object.entries(themeColors).forEach(([key, value]) => {
      if (key !== 'name') {
        root.style.setProperty(`--${key}`, value)
      }
    })
  }, [theme])

  const setTheme = (newTheme) => {
    if (themes[newTheme]) {
      setThemeState(newTheme)
    }
  }

  return { theme, setTheme, themeData: themes[theme] }
}

