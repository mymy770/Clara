import React from 'react'

export default function ConfirmModal({ isOpen, message, onConfirm, onCancel }) {
  if (!isOpen) return null

  return (
    <div
      className="modal-overlay"
      onClick={onCancel}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
    >
      <div
        className="modal"
        onClick={(e) => e.stopPropagation()}
        style={{
          background: '#fff',
          borderRadius: '12px',
          padding: '20px',
          maxWidth: '400px',
          width: '90%',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
        }}
      >
        <h3 style={{
          marginBottom: '12px',
          fontSize: '16px',
          color: '#000',
        }}>
          Confirmer la suppression
        </h3>
        <p style={{
          marginBottom: '20px',
          fontSize: '14px',
          color: '#666',
          lineHeight: '1.5',
        }}>
          {message}
        </p>
        <div className="modal-buttons" style={{
          display: 'flex',
          gap: '10px',
          justifyContent: 'flex-end',
        }}>
          <button
            className="modal-btn modal-btn-cancel"
            onClick={onCancel}
            style={{
              padding: '8px 16px',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '500',
              background: '#f0f0f0',
              color: '#000',
            }}
          >
            Annuler
          </button>
          <button
            className="modal-btn modal-btn-confirm"
            onClick={onConfirm}
            style={{
              padding: '8px 16px',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '500',
              background: '#ff3b30',
              color: '#fff',
            }}
          >
            Supprimer
          </button>
        </div>
      </div>
    </div>
  )
}

