'use client';

import React from 'react';
import { cn } from '../../../lib/utils';
import { Toast, ToastProvider, useToast } from './Toast';
import {
  Alert,
  AlertTitle,
  AlertDescription,
  AlertActions,
  InlineAlert,
} from './Alert';

export { 
  Toast, 
  ToastProvider, 
  useToast,
  Alert,
  AlertTitle,
  AlertDescription,
  AlertActions,
  InlineAlert,
};

// Re-export common feedback components
export function LoadingSpinner({
  className,
  size = 'md',
}) {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
  };

  return (
    <div
      className={cn(
        'animate-spin rounded-full border-2 border-current border-t-transparent',
        sizes[size],
        className
      )}
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
}

export function LoadingOverlay({
  children,
  loading,
  className,
}) {
  if (!loading) return children;

  return (
    <div className="relative">
      {children}
      <div
        className={cn(
          'absolute inset-0 flex items-center justify-center bg-white/50',
          className
        )}
      >
        <LoadingSpinner size="lg" className="text-spring-green" />
      </div>
    </div>
  );
}

export function ErrorBoundary({
  children,
  fallback,
}) {
  const [hasError, setHasError] = React.useState(false);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    const handleError = (error) => {
      setHasError(true);
      setError(error);
    };

    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  if (hasError) {
    return fallback ? (
      fallback(error)
    ) : (
      <Alert
        variant="error"
        title="Something went wrong"
        description="An unexpected error occurred. Please try again later."
      />
    );
  }

  return children;
}

export function ProgressBar({
  value,
  max = 100,
  className,
  showLabel = false,
}) {
  const percentage = Math.round((value / max) * 100);

  return (
    <div className={className}>
      <div className="relative h-2 bg-moss-green/10 rounded-full overflow-hidden">
        <div
          className="absolute inset-y-0 left-0 bg-spring-green transition-all duration-300 ease-out rounded-full"
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <p className="mt-2 text-sm text-moss-green">
          {percentage}%
        </p>
      )}
    </div>
  );
}

export function Badge({
  children,
  variant = 'default',
  className,
}) {
  const variants = {
    default: 'bg-moss-green/10 text-moss-green',
    primary: 'bg-spring-green text-midnight-forest',
    success: 'bg-green-100 text-green-800',
    error: 'bg-red-100 text-red-800',
    warning: 'bg-yellow-100 text-yellow-800',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
} 