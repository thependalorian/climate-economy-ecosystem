'use client';

import React from 'react';
import { cn } from '../../../lib/utils';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

/**
 * Alert Component
 * 
 * An alert component that follows ACT brand guidelines.
 * Supports different variants, dismissible state, and custom actions.
 */
export function Alert({
  variant = 'info',
  title,
  description,
  icon,
  action,
  onClose,
  className,
  dismissible = true,
}) {
  // Variant-specific styles and icons
  const variants = {
    success: {
      defaultIcon: <CheckCircle className="h-5 w-5" />,
      styles: "bg-green-50 text-green-800 border-green-200",
      iconColor: "text-green-500",
      closeButtonStyles: "hover:bg-green-100 focus:ring-green-500",
    },
    error: {
      defaultIcon: <AlertCircle className="h-5 w-5" />,
      styles: "bg-red-50 text-red-800 border-red-200",
      iconColor: "text-red-500",
      closeButtonStyles: "hover:bg-red-100 focus:ring-red-500",
    },
    warning: {
      defaultIcon: <AlertTriangle className="h-5 w-5" />,
      styles: "bg-yellow-50 text-yellow-800 border-yellow-200",
      iconColor: "text-yellow-500",
      closeButtonStyles: "hover:bg-yellow-100 focus:ring-yellow-500",
    },
    info: {
      defaultIcon: <Info className="h-5 w-5" />,
      styles: "bg-seafoam-blue text-midnight-forest border-spring-green",
      iconColor: "text-spring-green",
      closeButtonStyles: "hover:bg-spring-green/10 focus:ring-spring-green",
    },
  };

  const {
    defaultIcon,
    styles,
    iconColor,
    closeButtonStyles,
  } = variants[variant];

  return (
    <div
      className={cn(
        "rounded-lg border p-4",
        styles,
        className
      )}
      role="alert"
    >
      <div className="flex">
        {/* Icon */}
        {(icon || defaultIcon) && (
          <div className={cn("flex-shrink-0", iconColor)}>
            {icon || defaultIcon}
          </div>
        )}

        {/* Content */}
        <div className={cn("flex-1", icon || defaultIcon ? "ml-3" : "")}>
          {/* Title */}
          {title && (
            <h3 className="text-sm font-medium">
              {title}
            </h3>
          )}

          {/* Description */}
          {description && (
            <div className={cn(
              "text-sm opacity-90",
              title ? "mt-2" : ""
            )}>
              {description}
            </div>
          )}

          {/* Action */}
          {action && (
            <div className="mt-4">
              {action}
            </div>
          )}
        </div>

        {/* Close Button */}
        {dismissible && onClose && (
          <div className="ml-4 flex-shrink-0 flex">
            <button
              type="button"
              className={cn(
                "inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2",
                "transition-colors",
                closeButtonStyles
              )}
              onClick={onClose}
            >
              <span className="sr-only">Dismiss</span>
              <X className="h-5 w-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * AlertTitle Component
 * 
 * A styled title component for use within alerts.
 */
export function AlertTitle({
  children,
  className,
}) {
  return (
    <h3 className={cn(
      "text-sm font-medium",
      className
    )}>
      {children}
    </h3>
  );
}

/**
 * AlertDescription Component
 * 
 * A styled description component for use within alerts.
 */
export function AlertDescription({
  children,
  className,
}) {
  return (
    <div className={cn(
      "mt-2 text-sm opacity-90",
      className
    )}>
      {children}
    </div>
  );
}

/**
 * AlertActions Component
 * 
 * A container for alert actions with proper spacing.
 */
export function AlertActions({
  children,
  className,
}) {
  return (
    <div className={cn(
      "mt-4 flex space-x-4",
      className
    )}>
      {children}
    </div>
  );
}

/**
 * InlineAlert Component
 * 
 * A simpler, inline version of the alert for form validation and inline messages.
 */
export function InlineAlert({
  variant = 'info',
  children,
  className,
  icon,
}) {
  // Variant-specific styles and icons
  const variants = {
    success: {
      defaultIcon: <CheckCircle className="h-4 w-4" />,
      styles: "text-green-800",
      iconColor: "text-green-500",
    },
    error: {
      defaultIcon: <AlertCircle className="h-4 w-4" />,
      styles: "text-red-800",
      iconColor: "text-red-500",
    },
    warning: {
      defaultIcon: <AlertTriangle className="h-4 w-4" />,
      styles: "text-yellow-800",
      iconColor: "text-yellow-500",
    },
    info: {
      defaultIcon: <Info className="h-4 w-4" />,
      styles: "text-midnight-forest",
      iconColor: "text-spring-green",
    },
  };

  const {
    defaultIcon,
    styles,
    iconColor,
  } = variants[variant];

  return (
    <div
      className={cn(
        "flex items-start text-sm",
        styles,
        className
      )}
      role="alert"
    >
      {(icon || defaultIcon) && (
        <span className={cn("flex-shrink-0 mr-2", iconColor)}>
          {icon || defaultIcon}
        </span>
      )}
      <span>{children}</span>
    </div>
  );
} 