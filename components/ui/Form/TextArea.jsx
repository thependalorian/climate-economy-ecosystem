'use client';

import React, { forwardRef } from 'react';
import { cn } from '../../../lib/utils';
import { FormLabel, ErrorMessage } from '../Typography';

/**
 * TextArea Component
 * 
 * A form textarea component that follows ACT brand guidelines.
 * Supports auto-resizing, character count, and validation states.
 */
const TextArea = forwardRef(({
  label,
  error,
  required,
  className,
  textAreaClassName,
  labelClassName,
  helpText,
  maxLength,
  showCount = false,
  autoResize = false,
  minRows = 3,
  maxRows = 8,
  ...props
}, ref) => {
  const [characterCount, setCharacterCount] = React.useState(0);
  const textAreaRef = React.useRef(null);
  
  // Combine refs
  const combinedRef = (element) => {
    textAreaRef.current = element;
    if (typeof ref === 'function') {
      ref(element);
    } else if (ref) {
      ref.current = element;
    }
  };
  
  // Handle auto-resize
  const handleAutoResize = () => {
    if (!autoResize || !textAreaRef.current) return;
    
    const textarea = textAreaRef.current;
    const lineHeight = parseInt(getComputedStyle(textarea).lineHeight);
    const minHeight = minRows * lineHeight;
    const maxHeight = maxRows * lineHeight;
    
    // Reset height to auto to get the correct scrollHeight
    textarea.style.height = 'auto';
    
    // Calculate new height
    const newHeight = Math.min(
      Math.max(textarea.scrollHeight, minHeight),
      maxHeight
    );
    
    textarea.style.height = `${newHeight}px`;
  };
  
  // Update character count and handle auto-resize
  const handleInput = (e) => {
    if (showCount) {
      setCharacterCount(e.target.value.length);
    }
    if (autoResize) {
      handleAutoResize();
    }
    props.onChange?.(e);
  };
  
  // Base textarea styles
  const baseTextAreaStyles = "w-full px-3 py-2 bg-white border rounded-md font-inter text-midnight-forest placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-0 disabled:opacity-50 disabled:cursor-not-allowed resize-none";
  
  // Textarea state styles
  const stateStyles = error
    ? "border-red-500 focus:border-red-500 focus:ring-red-500"
    : "border-moss-green focus:border-spring-green focus:ring-spring-green";
  
  // Initialize auto-resize
  React.useEffect(() => {
    if (autoResize) {
      handleAutoResize();
    }
  }, [autoResize, props.value]);
  
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
        <textarea
          ref={combinedRef}
          className={cn(
            baseTextAreaStyles,
            stateStyles,
            textAreaClassName
          )}
          aria-invalid={error ? "true" : "false"}
          aria-describedby={
            error
              ? `${props.id}-error`
              : helpText
              ? `${props.id}-description`
              : undefined
          }
          onChange={handleInput}
          required={required}
          maxLength={maxLength}
          rows={minRows}
          {...props}
        />
        
        {(showCount || maxLength) && (
          <div className="absolute bottom-2 right-2 text-xs text-moss-green">
            {characterCount}
            {maxLength && `/${maxLength}`}
          </div>
        )}
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
        <p
          id={`${props.id}-description`}
          className="mt-1 text-sm text-moss-green"
        >
          {helpText}
        </p>
      )}
    </div>
  );
});

TextArea.displayName = 'TextArea';

export { TextArea }; 