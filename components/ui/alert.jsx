/**
 * Alert Component
 * A reusable alert component that follows ACT brand guidelines
 * Location: /components/ui/alert.jsx
 */

'use client';

import React from 'react';
import { cn } from '../../lib/utils';
import { X } from 'lucide-react';

const Alert = ({
  children,
  variant = 'info',
  className = '',
  onClose,
  ...props
}) => {
  const variants = {
    info: 'bg-seafoam-blue border-l-4 border-spring-green text-midnight-forest',
    success: 'bg-seafoam-blue border-l-4 border-spring-green text-midnight-forest',
    warning: 'bg-sand-gray border-l-4 border-moss-green text-moss-green',
    error: 'bg-red-50 border-l-4 border-red-500 text-red-700',
  };

  return (
    <div
      role="alert"
      className={cn(
        'relative p-4 rounded-r font-inter leading-body',
        variants[variant],
        className
      )}
      {...props}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">{children}</div>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-4 text-midnight-forest hover:text-spring-green transition-colors"
            aria-label="Close alert"
          >
            <X size={20} />
          </button>
        )}
      </div>
    </div>
  );
};

const AlertTitle = ({
  children,
  className = '',
  ...props
}) => {
  return (
    <h5
      className={cn(
        'font-heading text-lg tracking-tightest leading-title mb-1',
        className
      )}
      {...props}
    >
      {children}
    </h5>
  );
};

const AlertDescription = ({
  children,
  className = '',
  ...props
}) => {
  return (
    <div
      className={cn(
        'text-sm leading-body',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export { Alert, AlertTitle, AlertDescription }; 