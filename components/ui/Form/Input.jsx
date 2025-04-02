'use client';

import React, { forwardRef } from 'react';
import { cn } from '../../../lib/utils';
import { FormLabel, ErrorMessage } from '../Typography';

/**
 * Input Component
 * 
 * A form input component that follows ACT brand guidelines.
 * Supports various types, states, and validation.
 */
const Input = forwardRef(({
  type = 'text',
  label,
  error,
  required,
  className,
  inputClassName,
  labelClassName,
  helpText,
  icon,
  iconPosition = 'left',
  ...props
}, ref) => {
  // Base input styles
  const baseInputStyles = "w-full px-3 py-2 bg-white border rounded-md font-inter text-midnight-forest placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-0 disabled:opacity-50 disabled:cursor-not-allowed";
  
  // Input state styles
  const stateStyles = error
    ? "border-red-500 focus:border-red-500 focus:ring-red-500"
    : "border-moss-green focus:border-spring-green focus:ring-spring-green";
  
  // Icon container styles
  const iconContainerStyles = cn(
    "absolute inset-y-0 flex items-center",
    iconPosition === 'left' ? "left-3" : "right-3"
  );
  
  // Adjust padding if icon is present
  const iconPaddingStyles = icon
    ? iconPosition === 'left'
      ? "pl-10"
      : "pr-10"
    : "";
  
  return (
    <div className={className}>
      {label && (
        <FormLabel
          error={error}
          required={required}
          className={labelClassName}
        >
          {label}
        </FormLabel>
      )}
      
      <div className="relative">
        {icon && (
          <div className={iconContainerStyles}>
            {icon}
          </div>
        )}
        
        <input
          ref={ref}
          type={type}
          className={cn(
            baseInputStyles,
            stateStyles,
            iconPaddingStyles,
            inputClassName
          )}
          aria-invalid={error ? "true" : "false"}
          aria-describedby={error ? `${props.id}-error` : undefined}
          required={required}
          {...props}
        />
      </div>
      
      {error && (
        <ErrorMessage
          id={`${props.id}-error`}
          role="alert"
        >
          {error}
        </ErrorMessage>
      )}
      
      {helpText && !error && (
        <p className="mt-1 text-sm text-moss-green">
          {helpText}
        </p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export { Input }; 