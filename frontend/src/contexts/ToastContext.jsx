import React, { createContext, useContext, useState } from 'react'
import Toast from '../components/Toast'

/**
 * Toast Context
 * 
 * Provides global toast notification functionality.
 * Any component can trigger toast messages via useToast() hook.
 * 
 * Usage:
 *   const { show } = useToast()
 *   show('Message', 'warning')
 * 
 * Types: info, success, warning, error
 */
const ToastContext = createContext(null)

export function ToastProvider({ children }) {
  const [toast, setToast] = useState(null)

  const show = (message, type = 'info', duration = 5000) => {
    setToast({ message, type, duration })
  }

  const hide = () => {
    setToast(null)
  }

  return (
    <ToastContext.Provider value={{ show, hide }}>
      {children}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          duration={toast.duration}
          onClose={hide}
        />
      )}
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within ToastProvider')
  }
  return context
}
