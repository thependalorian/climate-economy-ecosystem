'use client';

import React, { forwardRef } from 'react';
import { cn } from '../../../lib/utils';
import { Check } from 'lucide-react';

/**
 * Checkbox Component
 * 
 * A form checkbox component that follows ACT brand guidelines.
 * Supports custom styling, states, and group functionality.
 */
const Checkbox = forwardRef(({
  label,
  error,
  className,
  checkboxClassName,
  labelClassName,
  helpText,
  ...props
}, ref) => {
  // Base checkbox styles
  const baseCheckboxStyles = "h-5 w-5 rounded border focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";
  
  // Checkbox state styles
  const stateStyles = error
    ? "border-red-500 focus:border-red-500 focus:ring-red-500"
    : "border-moss-green text-spring-green focus:border-spring-green focus:ring-spring-green";
  
  return (
    <div className={cn("flex items-start", className)}>
      <div className="flex items-center h-5">
        <input
          ref={ref}
          type="checkbox"
          className={cn(
            baseCheckboxStyles,
            stateStyles,
            checkboxClassName
          )}
          {...props}
        />
      </div>
      
      {(label || helpText) && (
        <div className="ml-3">
          {label && (
            <label
              htmlFor={props.id}
              className={cn(
                "font-inter text-sm font-medium text-midnight-forest",
                error && "text-red-500",
                labelClassName
              )}
            >
              {label}
            </label>
          )}
          
          {helpText && (
            <p className="text-sm text-moss-green">
              {helpText}
            </p>
          )}
        </div>
      )}
    </div>
  );
});

Checkbox.displayName = 'Checkbox';

/**
 * CheckboxGroup Component
 * 
 * A group of checkboxes with shared styling and state management.
 */
const CheckboxGroup = forwardRef(({
  label,
  error,
  required,
  className,
  options = [],
  value = [],
  onChange,
  orientation = 'vertical',
  ...props
}, ref) => {
  const handleChange = (optionValue) => (e) => {
    const newValue = e.target.checked
      ? [...value, optionValue]
      : value.filter(v => v !== optionValue);
    
    onChange?.(newValue);
  };
  
  return (
    <div
      role="group"
      aria-labelledby={`${props.id}-group-label`}
      className={className}
    >
      {label && (
        <div
          id={`${props.id}-group-label`}
          className={cn(
            "font-inter text-sm font-medium text-midnight-forest mb-2",
            error && "text-red-500"
          )}
        >
          {label}
          {required && (
            <span className="text-red-500 ml-1" aria-hidden="true">
              *
            </span>
          )}
        </div>
      )}
      
      <div
        className={cn(
          "space-y-2",
          orientation === 'horizontal' && "space-y-0 space-x-6 flex items-center"
        )}
      >
        {options.map((option) => (
          <Checkbox
            key={option.value}
            id={`${props.id}-${option.value}`}
            checked={value.includes(option.value)}
            onChange={handleChange(option.value)}
            label={option.label}
            disabled={option.disabled}
            error={error}
          />
        ))}
      </div>
      
      {error && (
        <p
          className="mt-1 text-sm text-red-500"
          role="alert"
        >
          {error}
        </p>
      )}
    </div>
  );
});

CheckboxGroup.displayName = 'CheckboxGroup';

/**
 * IndeterminateCheckbox Component
 * 
 * A checkbox that can display an indeterminate state.
 * Useful for parent/child checkbox relationships.
 */
const IndeterminateCheckbox = forwardRef(({
  indeterminate = false,
  ...props
}, ref) => {
  const internalRef = React.useRef(null);
  const resolvedRef = ref || internalRef;
  
  React.useEffect(() => {
    if (resolvedRef.current) {
      resolvedRef.current.indeterminate = indeterminate;
    }
  }, [resolvedRef, indeterminate]);
  
  return (
    <Checkbox
      ref={resolvedRef}
      {...props}
    />
  );
});

IndeterminateCheckbox.displayName = 'IndeterminateCheckbox';

export { Checkbox, CheckboxGroup, IndeterminateCheckbox }; 