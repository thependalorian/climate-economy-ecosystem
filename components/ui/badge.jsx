'use client';

import React from 'react';
import { cn } from '../../lib/utils';

/**
 * Badge Component
 * A reusable badge component that follows ACT brand guidelines
 * Location: /components/ui/badge.jsx
 */

const Badge = ({
  children,
  variant = 'default',
  size = 'md',
  className = '',
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-inter rounded-full text-center whitespace-nowrap font-medium';

  const variantStyles = {
    default: 'bg-sand-gray text-midnight-forest border border-spring-green/20',
    primary: 'bg-spring-green text-midnight-forest border border-spring-green',
    secondary: 'bg-moss-green text-white border border-moss-green',
    outline: 'bg-transparent border border-spring-green text-moss-green',
    muted: 'bg-seafoam-blue text-midnight-forest border border-spring-green/20',
    success: 'bg-green-100 text-green-800 border border-green-200',
    error: 'bg-red-100 text-red-800 border border-red-200',
    warning: 'bg-amber-100 text-amber-800 border border-amber-200',
  };

  const sizeStyles = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
    lg: 'text-base px-3 py-1.5',
  };

  return (
    <span
      className={cn(
        baseStyles,
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};

export { Badge }; 