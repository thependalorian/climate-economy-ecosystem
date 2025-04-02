'use client';

import { useState, useRef, useEffect, forwardRef } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '../../lib/utils';

/**
 * Popover Component
 * A reusable popover component that follows ACT brand guidelines
 * Location: /components/ui/popover.jsx
 */

const Popover = ({ 
  children, 
  content, 
  placement = 'bottom', 
  className = '',
  trigger = 'click', // 'click' or 'hover'
  open: controlledOpen,
  onOpenChange,
  align = 'center' // 'start', 'center', 'end'
}) => {
  const [open, setOpen] = useState(false);
  const triggerRef = useRef(null);
  const contentRef = useRef(null);
  const [position, setPosition] = useState({ top: 0, left: 0 });

  // Determine if we're in controlled or uncontrolled mode
  const isControlled = controlledOpen !== undefined;
  const isOpen = isControlled ? controlledOpen : open;

  // Update position when open changes
  useEffect(() => {
    if (isOpen && triggerRef.current) {
      updatePosition();
    }
  }, [isOpen]);

  // Update position function
  const updatePosition = () => {
    if (!triggerRef.current) return;
    
    const triggerRect = triggerRef.current.getBoundingClientRect();
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const scrollLeft = window.scrollX || document.documentElement.scrollLeft;
    
    let top, left;
    
    switch (placement) {
      case 'top':
        top = triggerRect.top + scrollTop - (contentRef.current?.offsetHeight || 0) - 8;
        break;
      case 'bottom':
        top = triggerRect.bottom + scrollTop + 8;
        break;
      case 'left':
        top = triggerRect.top + scrollTop + (triggerRect.height / 2) - (contentRef.current?.offsetHeight || 0) / 2;
        left = triggerRect.left + scrollLeft - (contentRef.current?.offsetWidth || 0) - 8;
        break;
      case 'right':
        top = triggerRect.top + scrollTop + (triggerRect.height / 2) - (contentRef.current?.offsetHeight || 0) / 2;
        left = triggerRect.right + scrollLeft + 8;
        break;
      default:
        top = triggerRect.bottom + scrollTop + 8;
    }
    
    // Handle alignment for top and bottom placements
    if (placement === 'top' || placement === 'bottom') {
      switch (align) {
        case 'start':
          left = triggerRect.left + scrollLeft;
          break;
        case 'end':
          left = triggerRect.right + scrollLeft - (contentRef.current?.offsetWidth || 0);
          break;
        default: // center
          left = triggerRect.left + scrollLeft + (triggerRect.width / 2) - (contentRef.current?.offsetWidth || 0) / 2;
      }
    }
    
    setPosition({ top, left });
  };

  // Toggle open state
  const toggleOpen = () => {
    const newOpenState = !isOpen;
    if (!isControlled) {
      setOpen(newOpenState);
    }
    if (onOpenChange) {
      onOpenChange(newOpenState);
    }
  };

  // Handle click outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        isOpen &&
        !triggerRef.current?.contains(event.target) &&
        !contentRef.current?.contains(event.target)
      ) {
        if (!isControlled) {
          setOpen(false);
        }
        if (onOpenChange) {
          onOpenChange(false);
        }
      }
    };

    const handleEscape = (event) => {
      if (isOpen && event.key === 'Escape') {
        if (!isControlled) {
          setOpen(false);
        }
        if (onOpenChange) {
          onOpenChange(false);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, isControlled, onOpenChange]);

  // Setup event handlers based on trigger type
  const triggerProps = {};
  if (trigger === 'click') {
    triggerProps.onClick = toggleOpen;
  } else if (trigger === 'hover') {
    triggerProps.onMouseEnter = () => {
      if (!isControlled) {
        setOpen(true);
      }
      if (onOpenChange) {
        onOpenChange(true);
      }
    };
    triggerProps.onMouseLeave = () => {
      if (!isControlled) {
        setOpen(false);
      }
      if (onOpenChange) {
        onOpenChange(false);
      }
    };
  }

  return (
    <>
      <div
        ref={triggerRef}
        className={cn("inline-block", className)}
        {...triggerProps}
      >
        {children}
      </div>
      {isOpen && typeof window !== 'undefined' && createPortal(
        <div
          ref={contentRef}
          style={{
            position: 'absolute',
            top: `${position.top}px`,
            left: `${position.left}px`,
            zIndex: 50,
          }}
          className={cn(
            "bg-white border border-sand-gray rounded-md shadow-md",
            "animate-in fade-in-50 zoom-in-95 duration-200"
          )}
        >
          {content}
        </div>,
        document.body
      )}
    </>
  );
};

// Using forwardRef to properly handle refs
const PopoverTrigger = forwardRef(({ children, className = '', ...props }, ref) => {
  return (
    <div ref={ref} className={className} {...props}>
      {children}
    </div>
  );
});
PopoverTrigger.displayName = 'PopoverTrigger';

// Using forwardRef to properly handle refs
const PopoverContent = forwardRef(({ children, className = '', ...props }, ref) => {
  return (
    <div 
      ref={ref} 
      className={cn(
        "p-4 bg-white rounded-md shadow-md border border-sand-gray",
        "text-midnight-forest font-inter",
        className
      )} 
      {...props}
    >
      {children}
    </div>
  );
});
PopoverContent.displayName = 'PopoverContent';

export { Popover, PopoverTrigger, PopoverContent }; 