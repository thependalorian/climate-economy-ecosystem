'use client';

import React, { forwardRef } from 'react';
import { cn } from '../../../lib/utils';
import { FormLabel, ErrorMessage } from '../Typography';
import { ChevronDown } from 'lucide-react';

/**
 * Select Component
 * 
 * A form select component that follows ACT brand guidelines.
 * Supports single selection with custom styling and states.
 */
const Select = forwardRef(({
  label,
  error,
  required,
  className,
  selectClassName,
  labelClassName,
  helpText,
  options = [],
  placeholder = 'Select an option',
  ...props
}, ref) => {
  // Base select styles
  const baseSelectStyles = "w-full px-3 py-2 bg-white border rounded-md font-inter text-midnight-forest appearance-none focus:outline-none focus:ring-2 focus:ring-offset-0 disabled:opacity-50 disabled:cursor-not-allowed";
  
  // Select state styles
  const stateStyles = error
    ? "border-red-500 focus:border-red-500 focus:ring-red-500"
    : "border-moss-green focus:border-spring-green focus:ring-spring-green";
  
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
        <select
          ref={ref}
          className={cn(
            baseSelectStyles,
            stateStyles,
            "pr-10", // Space for the chevron
            selectClassName
          )}
          aria-invalid={error ? "true" : "false"}
          aria-describedby={error ? `${props.id}-error` : undefined}
          required={required}
          {...props}
        >
          <option value="" disabled>
            {placeholder}
          </option>
          {options.map((option) => (
            <option
              key={option.value}
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
            </option>
          ))}
        </select>
        
        <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
          <ChevronDown
            className="w-5 h-5 text-moss-green"
            aria-hidden="true"
          />
        </div>
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

Select.displayName = 'Select';

/**
 * MultiSelect Component
 * 
 * A form select component that supports multiple selections.
 * Includes custom styling and chip display for selected items.
 */
const MultiSelect = forwardRef(({
  label,
  error,
  required,
  className,
  selectClassName,
  labelClassName,
  helpText,
  options = [],
  placeholder = 'Select options',
  selectedValues = [],
  onSelectionChange,
  ...props
}, ref) => {
  // Base styles from single select
  const baseSelectStyles = "w-full px-3 py-2 bg-white border rounded-md font-inter text-midnight-forest focus:outline-none focus:ring-2 focus:ring-offset-0 disabled:opacity-50 disabled:cursor-not-allowed";
  
  const stateStyles = error
    ? "border-red-500 focus:border-red-500 focus:ring-red-500"
    : "border-moss-green focus:border-spring-green focus:ring-spring-green";
  
  // Handle selection changes
  const handleChange = (e) => {
    const values = Array.from(e.target.selectedOptions, option => option.value);
    onSelectionChange?.(values);
  };
  
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
        <select
          ref={ref}
          multiple
          className={cn(
            baseSelectStyles,
            stateStyles,
            "pr-10",
            selectClassName
          )}
          aria-invalid={error ? "true" : "false"}
          aria-describedby={error ? `${props.id}-error` : undefined}
          required={required}
          onChange={handleChange}
          value={selectedValues}
          {...props}
        >
          {options.map((option) => (
            <option
              key={option.value}
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
            </option>
          ))}
        </select>
        
        <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
          <ChevronDown
            className="w-5 h-5 text-moss-green"
            aria-hidden="true"
          />
        </div>
      </div>
      
      {/* Selected items display */}
      {selectedValues.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-2">
          {selectedValues.map((value) => {
            const option = options.find(opt => opt.value === value);
            return (
              <span
                key={value}
                className="inline-flex items-center px-2 py-1 rounded-full text-sm bg-spring-green text-midnight-forest"
              >
                {option?.label || value}
              </span>
            );
          })}
        </div>
      )}
      
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

MultiSelect.displayName = 'MultiSelect';

export { Select, MultiSelect }; 