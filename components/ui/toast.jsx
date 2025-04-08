"use client"

import { createContext, useContext, useState } from 'react'
import { cn } from '../../lib/utils'
import { FiX, FiInfo, FiCheckCircle, FiAlertCircle } from 'react-icons/fi'

// Create a Toast context
const ToastContext = createContext({
  toast: () => {},
  success: () => {},
  error: () => {},
  info: () => {},
  warning: () => {},
})

export function useToast() {
  return useContext(ToastContext)
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])
  
  const addToast = (message, type = 'default', duration = 5000) => {
    const id = Math.random().toString(36).substring(2, 9)
    const newToast = {
      id,
      message,
      type,
      duration
    }
    
    setToasts(prev => [...prev, newToast])
    
    if (duration !== Infinity) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }
    
    return id
  }
  
  const removeToast = (id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }
  
  // Toast types
  const toast = (message, duration) => addToast(message, 'default', duration)
  const success = (message, duration) => addToast(message, 'success', duration)
  const error = (message, duration) => addToast(message, 'error', duration)
  const info = (message, duration) => addToast(message, 'info', duration)
  const warning = (message, duration) => addToast(message, 'warning', duration)
  
  return (
    <ToastContext.Provider value={{ toast, success, error, info, warning }}>
      {children}
      
      {/* Toast container */}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
        {toasts.map(toast => (
          <Toast 
            key={toast.id} 
            type={toast.type} 
            message={toast.message} 
            onClose={() => removeToast(toast.id)} 
          />
        ))}
      </div>
    </ToastContext.Provider>
  )
}

function Toast({ type, message, onClose }) {
  const getIcon = () => {
    switch (type) {
      case 'success':
        return <FiCheckCircle className="text-green-500" />
      case 'error':
        return <FiAlertCircle className="text-red-500" />
      case 'info':
        return <FiInfo className="text-blue-500" />
      case 'warning':
        return <FiAlertCircle className="text-amber-500" />
      default:
        return <FiInfo className="text-gray-500" />
    }
  }
  
  const getStyles = () => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200'
      case 'error':
        return 'bg-red-50 border-red-200'
      case 'info':
        return 'bg-blue-50 border-blue-200'
      case 'warning':
        return 'bg-amber-50 border-amber-200'
      default:
        return 'bg-white border-gray-200'
    }
  }
  
  return (
    <div className={cn(
      'p-4 rounded-md shadow-md border animate-in fade-in slide-in-from-top-5 duration-300',
      getStyles()
    )}>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 pt-0.5">
          {getIcon()}
        </div>
        <div className="flex-1 pr-6">
          <p className="text-sm text-gray-700">{message}</p>
        </div>
        <button
          onClick={onClose}
          className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <FiX size={16} />
        </button>
      </div>
    </div>
  )
} 