'use client';

import React, { forwardRef } from 'react';
import { cn } from '../../../lib/utils';

/**
 * Radio Component
 * 
 * A form radio component that follows ACT brand guidelines.
 * Supports custom styling and states.
 */
const Radio = forwardRef(({
  label,
  error,
  className,
  radioClassName,
  labelClassName,
  helpText,
  ...props
}, ref) => {
  // Base radio styles
  const baseRadioStyles = "h-5 w-5 rounded-full border focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";
  
  // Radio state styles
  const stateStyles = error
    ? "border-red-500 focus:border-red-500 focus:ring-red-500"
    : "border-moss-green text-spring-green focus:border-spring-green focus:ring-spring-green";
  
  return (
    <div className={cn("flex items-start", className)}>
      <div className="flex items-center h-5">
        <input
          ref={ref}
          type="radio"
          className={cn(
            baseRadioStyles,
            stateStyles,
            radioClassName
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

Radio.displayName = 'Radio';

/**
 * RadioGroup Component
 * 
 * A group of radio buttons with shared styling and state management.
 */
const RadioGroup = forwardRef(({
  label,
  error,
  required,
  className,
  options = [],
  value,
  onChange,
  orientation = 'vertical',
  description,
  ...props
}, ref) => {
  return (
    <div
      role="radiogroup"
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
      
      {description && (
        <p className="text-sm text-moss-green mb-3">
          {description}
        </p>
      )}
      
      <div
        className={cn(
          "space-y-2",
          orientation === 'horizontal' && "space-y-0 space-x-6 flex items-center"
        )}
      >
        {options.map((option) => (
          <Radio
            key={option.value}
            id={`${props.id}-${option.value}`}
            name={props.name || props.id}
            value={option.value}
            checked={value === option.value}
            onChange={(e) => onChange?.(e.target.value)}
            label={option.label}
            disabled={option.disabled}
            error={error}
            helpText={option.helpText}
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

RadioGroup.displayName = 'RadioGroup';

/**
 * RadioCard Component
 * 
 * A card-style radio button for more visual selection options.
 */
const RadioCard = forwardRef(({
  label,
  description,
  icon,
  className,
  checked,
  ...props
}, ref) => {
  return (
    <label className={cn(
      "relative block rounded-lg border p-4 cursor-pointer focus-within:ring-2 focus-within:ring-spring-green",
      checked
        ? "bg-seafoam-blue border-spring-green"
        : "border-moss-green hover:bg-seafoam-blue/10",
      className
    )}>
      <input
        ref={ref}
        type="radio"
        className="sr-only"
        checked={checked}
        {...props}
      />
      
      <div className="flex items-start">
        {icon && (
          <div className="flex-shrink-0 mr-3">
            {icon}
          </div>
        )}
        
        <div>
          <p className={cn(
            "font-inter font-medium",
            checked ? "text-midnight-forest" : "text-moss-green"
          )}>
            {label}
          </p>
          
          {description && (
            <p className={cn(
              "text-sm",
              checked ? "text-midnight-forest" : "text-moss-green"
            )}>
              {description}
            </p>
          )}
        </div>
        
        <div className={cn(
          "absolute top-4 right-4 flex h-5 w-5 items-center justify-center rounded-full border",
          checked
            ? "border-spring-green bg-spring-green"
            : "border-moss-green"
        )}>
          <div
            className={cn(
              "h-2.5 w-2.5 rounded-full bg-white",
              !checked && "hidden"
            )}
          />
        </div>
      </div>
    </label>
  );
});

RadioCard.displayName = 'RadioCard';

/**
 * RadioCardGroup Component
 * 
 * A group of card-style radio buttons.
 */
const RadioCardGroup = forwardRef(({
  label,
  error,
  required,
  className,
  options = [],
  value,
  onChange,
  columns = 1,
  ...props
}, ref) => {
  return (
    <div
      role="radiogroup"
      aria-labelledby={`${props.id}-group-label`}
      className={className}
    >
      {label && (
        <div
          id={`${props.id}-group-label`}
          className={cn(
            "font-inter text-sm font-medium text-midnight-forest mb-4",
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
          "grid gap-4",
          columns === 1 && "grid-cols-1",
          columns === 2 && "grid-cols-1 sm:grid-cols-2",
          columns === 3 && "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"
        )}
      >
        {options.map((option) => (
          <RadioCard
            key={option.value}
            id={`${props.id}-${option.value}`}
            name={props.name || props.id}
            value={option.value}
            checked={value === option.value}
            onChange={(e) => onChange?.(e.target.value)}
            label={option.label}
            description={option.description}
            icon={option.icon}
            disabled={option.disabled}
          />
        ))}
      </div>
      
      {error && (
        <p
          className="mt-2 text-sm text-red-500"
          role="alert"
        >
          {error}
        </p>
      )}
    </div>
  );
});

RadioCardGroup.displayName = 'RadioCardGroup';

export { Radio, RadioGroup, RadioCard, RadioCardGroup }; 