'use client';

import { useState, createContext, useContext } from 'react';
import { X } from 'lucide-react';
import { cn } from '../../lib/utils';

/**
 * Toast System
 * Provides toast notifications throughout the application following ACT brand guidelines
 * Location: /components/ui/use-toast.js
 */

// Types
const TOAST_TYPES = {
  DEFAULT: 'default',
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
};

// Create toast context
const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  // Add a new toast
  const toast = (options) => {
    const id = Math.random().toString(36).substring(2, 9);
    const newToast = {
      id,
      title: options.title,
      description: options.description,
      type: options.type || TOAST_TYPES.DEFAULT,
      duration: options.duration || 5000,
    };

    setToasts((prevToasts) => [...prevToasts, newToast]);

    // Auto-dismiss after duration
    if (newToast.duration) {
      setTimeout(() => {
        dismiss(id);
      }, newToast.duration);
    }

    return id;
  };

  // Add convenience methods for different toast types
  const success = (options) => toast({ ...options, type: TOAST_TYPES.SUCCESS });
  const error = (options) => toast({ ...options, type: TOAST_TYPES.ERROR });
  const warning = (options) => toast({ ...options, type: TOAST_TYPES.WARNING });
  const info = (options) => toast({ ...options, type: TOAST_TYPES.INFO });

  // Dismiss a toast by id
  const dismiss = (id) => {
    setToasts((prevToasts) => prevToasts.filter((toast) => toast.id !== id));
  };

  // Dismiss all toasts
  const dismissAll = () => {
    setToasts([]);
  };

  // Toast context value
  const value = {
    toasts,
    toast,
    success,
    error,
    warning,
    info,
    dismiss,
    dismissAll,
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastContainer />
    </ToastContext.Provider>
  );
}

// Toast container component
function ToastContainer() {
  const { toasts, dismiss } = useToast();

  if (!toasts.length) return null;

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-3 w-full max-w-md">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={cn(
            "p-4 rounded-md shadow-brand border-l-4 animate-in slide-in-from-right",
            {
              'bg-seafoam-blue border-spring-green': toast.type === TOAST_TYPES.SUCCESS,
              'bg-seafoam-blue border-spring-green': toast.type === TOAST_TYPES.DEFAULT,
              'bg-red-50 border-red-500': toast.type === TOAST_TYPES.ERROR,
              'bg-sand-gray border-moss-green': toast.type === TOAST_TYPES.WARNING,
              'bg-seafoam-blue border-moss-green': toast.type === TOAST_TYPES.INFO,
            }
          )}
        >
          <div className="flex justify-between items-start">
            <div>
              {toast.title && (
                <h5 className="font-heading text-lg tracking-tightest leading-title text-midnight-forest">
                  {toast.title}
                </h5>
              )}
              {toast.description && (
                <p className="mt-1 font-inter text-sm text-midnight-forest leading-body">
                  {toast.description}
                </p>
              )}
            </div>
            <button
              className="ml-4 text-moss-green opacity-70 hover:opacity-100 transition-opacity"
              onClick={() => dismiss(toast.id)}
              aria-label="Dismiss"
            >
              <X size={16} />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

// Custom hook to use toast context
export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

export { TOAST_TYPES }; 