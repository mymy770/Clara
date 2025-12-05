import React, { useState, useEffect, useRef } from 'react'
import { loadThemeFromLocalStorage, saveThemeToLocalStorage, applyThemeToDocument, DEFAULT_THEME } from '../config/themeManager'

export default function AppearanceSettings({ isOpen, onClose }) {
  const [theme, setTheme] = useState(DEFAULT_THEME)
  const [originalTheme, setOriginalTheme] = useState(null)
  const panelRef = useRef(null)

  useEffect(() => {
    if (isOpen) {
      const loaded = loadThemeFromLocalStorage()
      setTheme(loaded)
      setOriginalTheme({ ...loaded })
    }
  }, [isOpen])

  useEffect(() => {
    if (isOpen) {
      applyThemeToDocument(theme)
    }
  }, [theme, isOpen])

  useEffect(() => {
    function handleClickOutside(event) {
      if (panelRef.current && !panelRef.current.contains(event.target)) {
        handleCancel()
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen])

  function handleColorChange(key, value) {
    setTheme(prev => ({ ...prev, [key]: value }))
  }

  function handleFontSizeChange(value) {
    setTheme(prev => ({ ...prev, fontSize: value }))
  }

  function handleApply() {
    saveThemeToLocalStorage(theme)
    setOriginalTheme({ ...theme })
    onClose()
  }

  function handleCancel() {
    if (originalTheme) {
      setTheme(originalTheme)
      applyThemeToDocument(originalTheme)
    }
    onClose()
  }

  function handleReset() {
    setTheme(DEFAULT_THEME)
    applyThemeToDocument(DEFAULT_THEME)
    setOriginalTheme({ ...DEFAULT_THEME })
  }

  if (!isOpen) return null

  const settingsSections = [
    {
      title: 'Sidebar',
      items: [
        { key: 'sidebarBg', label: 'Fond sidebar' },
        { key: 'sidebarText', label: 'Texte sidebar' },
        { key: 'sidebarBorder', label: 'Bordure sidebar' },
      ]
    },
    {
      title: 'Header Sidebar (Conversations)',
      items: [
        { key: 'sidebarHeaderBg', label: 'Fond header' },
        { key: 'sidebarHeaderText', label: 'Texte header' },
      ]
    },
    {
      title: 'Bouton Nouvelle Session',
      items: [
        { key: 'newSessionBtnBg', label: 'Fond' },
        { key: 'newSessionBtnText', label: 'Texte' },
        { key: 'newSessionBtnBorder', label: 'Bordure' },
      ]
    },
    {
      title: 'Header',
      items: [
        { key: 'headerBg', label: 'Fond header' },
        { key: 'headerText', label: 'Texte header' },
        { key: 'headerBorder', label: 'Bordure header' },
      ]
    },
    {
      title: 'Chat',
      items: [
        { key: 'chatBg', label: 'Fond chat' },
        { key: 'textColor', label: 'Couleur texte' },
        { key: 'timeColor', label: 'Couleur heure' },
        { key: 'fontSize', label: 'Taille police', type: 'number' },
      ]
    },
    {
      title: 'Bulle Jeremy',
      items: [
        { key: 'jeremyBg', label: 'Fond' },
        { key: 'jeremyBorder', label: 'Bordure' },
        { key: 'jeremyText', label: 'Texte' },
      ]
    },
    {
      title: 'Bulle Clara',
      items: [
        { key: 'claraBg', label: 'Fond' },
        { key: 'claraBorder', label: 'Bordure' },
        { key: 'claraText', label: 'Texte' },
      ]
    },
    {
      title: 'Zone d\'input - Texte',
      items: [
        { key: 'inputAreaBg', label: 'Fond zone' },
        { key: 'inputBg', label: 'Fond textarea' },
        { key: 'inputText', label: 'Texte' },
        { key: 'inputBorder', label: 'Bordure' },
      ]
    },
    {
      title: 'Zone d\'input - Bouton Envoyer',
      items: [
        { key: 'sendBtnBg', label: 'Fond' },
        { key: 'sendBtnText', label: 'Texte' },
        { key: 'sendBtnBorder', label: 'Bordure' },
      ]
    },
    {
      title: 'Bande droite',
      items: [
        { key: 'rightPanelBg', label: 'Fond panel' },
        { key: 'rightPanelHeaderBg', label: 'Fond header "Todo & Process"' },
        { key: 'rightPanelHeaderText', label: 'Texte header' },
        { key: 'rightPanelBorder', label: 'Bordure panel' },
      ]
    },
    {
      title: 'Bouton Todo',
      items: [
        { key: 'todoBtnBg', label: 'Fond' },
        { key: 'todoBtnText', label: 'Texte' },
        { key: 'todoBtnBorder', label: 'Bordure' },
      ]
    },
    {
      title: 'Bouton Paramètres (⚙️ Couleurs)',
      items: [
        { key: 'settingsBtnBg', label: 'Fond' },
        { key: 'settingsBtnText', label: 'Texte' },
        { key: 'settingsBtnBorder', label: 'Bordure' },
      ]
    },
    {
      title: 'Bouton Supprimer Tout (🗑️)',
      items: [
        { key: 'deleteAllBtnBg', label: 'Fond' },
        { key: 'deleteAllBtnText', label: 'Texte' },
        { key: 'deleteAllBtnBorder', label: 'Bordure' },
      ]
    },
    {
      title: 'Bas Sidebar (Footer)',
      items: [
        { key: 'sidebarFooterBg', label: 'Fond' },
        { key: 'sidebarFooterBorder', label: 'Bordure' },
      ]
    },
    {
      title: 'Think',
      items: [
        { key: 'thinkBg', label: 'Fond panel' },
        { key: 'thinkHeaderBg', label: 'Fond header' },
        { key: 'thinkHeaderText', label: 'Texte header' },
        { key: 'thinkBorder', label: 'Bordure' },
        { key: 'thinkText', label: 'Couleur texte' },
      ]
    },
  ]

  return (
    <div
      ref={panelRef}
      id="settings-panel"
      style={{
        position: 'absolute',
        top: '45px',
        right: '12px',
        background: '#fff',
        border: '1px solid #ddd',
        padding: '15px',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        display: isOpen ? 'block' : 'none',
        width: '300px',
        maxHeight: '80vh',
        overflowY: 'auto',
        fontSize: '12px',
        zIndex: 10,
      }}
    >
      <h4 style={{
        marginBottom: '12px',
        fontSize: '14px',
        color: '#000',
      }}>
        Paramètres d'apparence
      </h4>

      {settingsSections.map((section, idx) => (
        <div key={idx} className="settings-section" style={{
          marginBottom: '15px',
          paddingBottom: '15px',
          borderBottom: idx < settingsSections.length - 1 ? '1px solid #eee' : 'none',
        }}>
          <div className="settings-section-title" style={{
            fontSize: '12px',
            fontWeight: '600',
            marginBottom: '8px',
            color: '#666',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
          }}>
            {section.title}
          </div>
          {section.items.map((item) => (
            <div key={item.key} className="settings-item" style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              margin: '6px 0',
            }}>
              <label style={{
                flex: 1,
                fontSize: '12px',
                color: '#333',
              }}>
                {item.label}
              </label>
              {item.type === 'number' ? (
                <input
                  type="number"
                  min="10"
                  max="20"
                  value={theme[item.key] || '14'}
                  onChange={(e) => handleFontSizeChange(e.target.value)}
                  style={{
                    width: '60px',
                    padding: '4px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '12px',
                  }}
                />
              ) : (
                <input
                  type="color"
                  value={theme[item.key] || '#000000'}
                  onChange={(e) => handleColorChange(item.key, e.target.value)}
                  style={{
                    width: '50px',
                    height: '30px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    padding: '2px',
                  }}
                />
              )}
            </div>
          ))}
        </div>
      ))}

      <div style={{
        marginTop: '15px',
        paddingTop: '15px',
        borderTop: '1px solid #eee',
      }}>
        <div style={{
          display: 'flex',
          gap: '8px',
          marginBottom: '8px',
        }}>
          <button
            onClick={handleApply}
            style={{
              flex: 1,
              padding: '8px',
              border: 'none',
              borderRadius: '6px',
              background: '#007AFF',
              color: '#fff',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: '500',
            }}
          >
            ✓ Appliquer
          </button>
          <button
            onClick={handleCancel}
            style={{
              flex: 1,
              padding: '8px',
              border: '1px solid #ddd',
              borderRadius: '6px',
              background: '#f5f5f5',
              color: '#333',
              cursor: 'pointer',
              fontSize: '12px',
            }}
          >
            ✕ Annuler
          </button>
        </div>
        <button
          onClick={handleReset}
          className="settings-reset"
          style={{
            marginTop: '0',
            padding: '8px',
            width: '100%',
            border: '1px solid #ddd',
            borderRadius: '6px',
            background: '#f5f5f5',
            cursor: 'pointer',
            fontSize: '12px',
          }}
        >
          Réinitialiser par défaut
        </button>
      </div>
    </div>
  )
}

