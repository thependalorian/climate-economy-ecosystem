'use client';

import React from 'react';
import { cn } from '../../../lib/utils';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import { createPortal } from 'react-dom';

/**
 * Toast Component
 * 
 * A notification component that follows ACT brand guidelines.
 * Supports different variants, auto-dismiss, and custom actions.
 */
export function Toast({
  variant = 'info',
  title,
  description,
  action,
  onClose,
  duration = 5000,
  className,
}) {
  const [isVisible, setIsVisible] = React.useState(true);

  // Handle auto-dismiss
  React.useEffect(() => {
    if (duration === Infinity) return;

    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(onClose, 300); // Allow exit animation to complete
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  // Variant-specific styles and icons
  const variants = {
    success: {
      icon: <CheckCircle className="h-5 w-5" />,
      styles: "bg-green-50 text-green-800 border-green-200",
      iconColor: "text-green-500",
    },
    error: {
      icon: <AlertCircle className="h-5 w-5" />,
      styles: "bg-red-50 text-red-800 border-red-200",
      iconColor: "text-red-500",
    },
    warning: {
      icon: <AlertTriangle className="h-5 w-5" />,
      styles: "bg-yellow-50 text-yellow-800 border-yellow-200",
      iconColor: "text-yellow-500",
    },
    info: {
      icon: <Info className="h-5 w-5" />,
      styles: "bg-seafoam-blue text-midnight-forest border-spring-green",
      iconColor: "text-spring-green",
    },
  };

  const { icon, styles, iconColor } = variants[variant];

  return createPortal(
    <div
      className={cn(
        "fixed bottom-4 right-4 z-50 transform transition-all duration-300",
        isVisible ? "translate-y-0 opacity-100" : "translate-y-2 opacity-0",
        className
      )}
    >
      <div
        className={cn(
          "flex items-start p-4 rounded-lg border shadow-lg max-w-sm",
          styles
        )}
        role="alert"
      >
        <div className={cn("flex-shrink-0", iconColor)}>
          {icon}
        </div>

        <div className="ml-3 w-0 flex-1">
          {title && (
            <p className="text-sm font-medium">
              {title}
            </p>
          )}
          {description && (
            <p className="mt-1 text-sm opacity-90">
              {description}
            </p>
          )}
          {action && (
            <div className="mt-3">
              {action}
            </div>
          )}
        </div>

        <div className="ml-4 flex-shrink-0 flex">
          <button
            className={cn(
              "inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2",
              "transition-colors hover:bg-black/5",
              variant === 'info' && "focus:ring-spring-green",
              variant === 'success' && "focus:ring-green-500",
              variant === 'error' && "focus:ring-red-500",
              variant === 'warning' && "focus:ring-yellow-500"
            )}
            onClick={() => {
              setIsVisible(false);
              setTimeout(onClose, 300);
            }}
          >
            <span className="sr-only">Close</span>
            <X className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}

/**
 * ToastProvider Component
 * 
 * A context provider for managing multiple toasts.
 */
const ToastContext = React.createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = React.useState([]);

  const addToast = React.useCallback((toast) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { ...toast, id }]);
    return id;
  }, []);

  const removeToast = React.useCallback((id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const value = React.useMemo(() => ({
    addToast,
    removeToast,
  }), [addToast, removeToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed bottom-0 right-0 z-50 p-4 space-y-4">
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            {...toast}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

/**
 * useToast Hook
 * 
 * A hook for using toasts throughout the application.
 */
export function useToast() {
  const context = React.useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
} 