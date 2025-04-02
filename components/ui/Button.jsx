'use client';

import React from 'react';
import { cn } from '../../lib/utils';
import { Loader2 } from 'lucide-react';

/**
 * Button Component
 * A reusable button component that follows ACT brand guidelines
 * Location: /components/ui/Button.jsx
 */

const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  disabled = false,
  loading = false,
  onClick,
  type = 'button',
  ...props
}) => {
  const baseClasses = 'font-inter transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center';
  
  const variantClasses = {
    primary: 'bg-spring-green text-midnight-forest hover:bg-spring-green/90 focus:ring-spring-green border-2 border-spring-green',
    secondary: 'bg-moss-green text-white hover:bg-moss-green/90 focus:ring-moss-green border-2 border-moss-green',
    tertiary: 'text-moss-green hover:text-spring-green bg-transparent hover:bg-spring-green/10 focus:ring-moss-green',
    outline: 'bg-transparent border-2 border-spring-green text-midnight-forest hover:bg-spring-green/10 focus:ring-spring-green',
    ghost: 'bg-transparent text-midnight-forest hover:bg-spring-green/10 focus:ring-spring-green',
    danger: 'bg-red-500 text-white hover:bg-red-600 focus:ring-red-500',
  };
  
  const sizeClasses = {
    xs: 'text-xs px-2.5 py-1.5 rounded font-medium',
    sm: 'text-sm px-3 py-2 rounded-md font-medium',
    md: 'text-base px-5 py-2.5 rounded-md font-medium',
    lg: 'text-lg px-6 py-3 rounded-md font-semibold',
  };

  const classes = cn(
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    className
  );

  return (
    <button
      type={type}
      className={classes}
      disabled={disabled || loading}
      onClick={onClick}
      {...props}
    >
      {loading ? (
        <Loader2 className="animate-spin mr-2" size={
          size === 'sm' ? 16 : size === 'md' ? 18 : 20
        } />
      ) : null}
      {children}
    </button>
  );
};

export { Button };

/**
 * IconButton Component
 * A circular button designed for icon-only interactions following ACT brand guidelines
 */
const IconButton = ({
  icon,
  className,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  tooltip,
  ...props
}) => {
  const baseClasses = 'rounded-full inline-flex items-center justify-center transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variantClasses = {
    primary: 'bg-spring-green text-midnight-forest hover:bg-spring-green/90 focus:ring-spring-green border-2 border-spring-green',
    secondary: 'bg-moss-green text-white hover:bg-moss-green/90 focus:ring-moss-green border-2 border-moss-green',
    tertiary: 'text-moss-green hover:text-spring-green bg-transparent hover:bg-spring-green/10 focus:ring-moss-green',
    ghost: 'bg-transparent text-midnight-forest hover:bg-spring-green/10 focus:ring-spring-green',
    danger: 'bg-red-500 text-white hover:bg-red-600 focus:ring-red-500',
  };
  
  const sizeClasses = {
    sm: "p-1.5",
    md: "p-2",
    lg: "p-3",
  };
  
  const classes = cn(
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    className
  );
  
  const button = (
    <button
      type="button"
      disabled={disabled || loading}
      className={classes}
      {...props}
    >
      {loading ? (
        <Loader2 className="animate-spin" size={
          size === 'sm' ? 16 : size === 'md' ? 20 : 24
        } />
      ) : (
        icon
      )}
    </button>
  );
  
  if (tooltip) {
    return (
      <div className="relative group">
        {button}
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs font-medium text-white bg-midnight-forest rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
          {tooltip}
        </div>
      </div>
    );
  }
  
  return button;
};

export { IconButton }; 