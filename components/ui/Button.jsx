"use client";

import React from 'react';
import { cn } from '../../lib/utils';
import { Loader2 } from '../../lib/icons-shim';

/**
 * Button Component
 * A versatile button component that supports various styles and states.
 * When "asChild" is true, it clones the only child with merged props.
 * Location: /components/ui/Button.jsx
 */
const Button = React.forwardRef(({
  className,
  variant = 'default',
  size = 'md',
  asChild = false,
  isLoading = false,
  disabled,
  children,
  ...props
}, ref) => {
  // Compute className
  const variantClassNames = {
    default: 'bg-primary text-primary-content hover:bg-primary-focus',
    outline: 'border border-primary bg-transparent text-primary hover:bg-primary/10',
    ghost: 'bg-transparent hover:bg-gray-100 text-gray-700',
    link: 'bg-transparent underline-offset-4 hover:underline text-primary hover:bg-transparent',
    destructive: 'bg-error text-error-content hover:bg-error-focus',
    success: 'bg-success text-success-content hover:bg-success-focus',
    secondary: 'bg-secondary text-secondary-content hover:bg-secondary-focus',
  };

  const sizeClassNames = {
    sm: 'h-8 px-3 text-xs rounded-md',
    md: 'h-10 px-4 py-2 rounded-md',
    lg: 'h-12 px-6 text-lg rounded-md',
    icon: 'h-10 w-10 rounded-full',
  };

  const computedClassName = cn(
    'inline-flex items-center justify-center font-medium transition-colors',
    'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
    'disabled:opacity-50 disabled:pointer-events-none',
    variantClassNames[variant],
    sizeClassNames[size],
    isLoading && 'opacity-70 pointer-events-none',
    className
  );

  if (asChild) {
    const child = React.Children.only(children);
    // If the child is a React.Fragment, wrap its children in a <span> to apply the computedClassName
    if (child.type === React.Fragment) {
      return (
        <span ref={ref} className={computedClassName} disabled={disabled || isLoading} {...props}>
          {child.props.children}
        </span>
      );
    }
    return React.cloneElement(child, {
      ...props,
      ref,
      className: cn(child.props.className, computedClassName),
      disabled: disabled || isLoading || child.props.disabled
    });
  }

  return (
    <button
      ref={ref}
      className={computedClassName}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && (
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      )}
      {children}
    </button>
  );
});

Button.displayName = 'Button';

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

// Add default export at the end of the file
export default Button; 