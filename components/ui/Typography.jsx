'use client';

import React from 'react';
import { cn } from '../../lib/utils';

/**
 * Typography Components
 * 
 * A collection of typography components that implement the ACT brand guidelines.
 * These components ensure consistent text styling across the application.
 */

export function Heading({ 
  level = 1, 
  children, 
  className, 
  ...props 
}) {
  const baseStyles = "font-heading tracking-tightest text-midnight-forest";
  const sizes = {
    1: "text-4xl md:text-5xl leading-title",
    2: "text-3xl md:text-4xl leading-title",
    3: "text-2xl md:text-3xl leading-title",
    4: "text-xl md:text-2xl leading-title",
    5: "text-lg md:text-xl leading-title",
    6: "text-base md:text-lg leading-title",
  };

  const Component = `h${level}`;
  
  return (
    <Component 
      className={cn(baseStyles, sizes[level], className)}
      {...props}
    >
      {children}
    </Component>
  );
}

export function Text({ 
  variant = 'body', 
  children, 
  className, 
  ...props 
}) {
  const styles = {
    body: "font-inter text-base leading-body text-midnight-forest",
    large: "font-inter text-lg leading-body text-midnight-forest",
    small: "font-inter text-sm leading-body text-midnight-forest",
    caption: "font-inter text-sm leading-normal text-moss-green",
  };

  return (
    <p 
      className={cn(styles[variant], className)}
      {...props}
    >
      {children}
    </p>
  );
}

export function Link({ 
  href, 
  children, 
  className, 
  underline = true,
  external = false,
  ...props 
}) {
  const baseStyles = "font-inter text-moss-green transition-colors hover:text-spring-green";
  const underlineStyles = underline ? "hover:underline" : "";
  
  const linkProps = external ? {
    target: "_blank",
    rel: "noopener noreferrer"
  } : {};

  return (
    <a 
      href={href}
      className={cn(baseStyles, underlineStyles, className)}
      {...linkProps}
      {...props}
    >
      {children}
    </a>
  );
}

export function Label({
  children,
  className,
  required,
  ...props
}) {
  return (
    <label
      className={cn(
        "font-inter text-sm font-medium text-midnight-forest",
        className
      )}
      {...props}
    >
      {children}
      {required && (
        <span className="text-red-500 ml-1" aria-hidden="true">*</span>
      )}
    </label>
  );
}

export function Caption({
  children,
  className,
  ...props
}) {
  return (
    <span
      className={cn(
        "font-inter text-xs leading-normal text-moss-green",
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}

// Helper component for section titles
export function SectionTitle({
  children,
  className,
  description,
  ...props
}) {
  return (
    <div className={cn("space-y-1", className)} {...props}>
      <Heading level={2}>{children}</Heading>
      {description && (
        <Text variant="large" className="text-moss-green">
          {description}
        </Text>
      )}
    </div>
  );
}

// Helper component for form field labels
export function FormLabel({
  children,
  className,
  required,
  error,
  ...props
}) {
  return (
    <Label
      className={cn(
        "block mb-2",
        error && "text-red-500",
        className
      )}
      required={required}
      {...props}
    >
      {children}
    </Label>
  );
}

// Helper component for error messages
export function ErrorMessage({
  children,
  className,
  ...props
}) {
  return (
    <Text
      variant="small"
      className={cn(
        "text-red-500 mt-1",
        className
      )}
      {...props}
    >
      {children}
    </Text>
  );
}

// Helper component for success messages
export function SuccessMessage({
  children,
  className,
  ...props
}) {
  return (
    <Text
      variant="small"
      className={cn(
        "text-green-600 mt-1",
        className
      )}
      {...props}
    >
      {children}
    </Text>
  );
} 