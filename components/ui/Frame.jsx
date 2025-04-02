'use client';

import React from 'react';
import { cn } from '../../lib/utils';

/**
 * Frame Component
 * 
 * A key visual element of the ACT brand identity. The Frame component creates
 * a distinctive border around content with optional brackets and arrows.
 * The frame thickness adjusts based on viewport size and content area.
 */
export function Frame({
  children,
  className,
  thickness = 2,
  variant = 'default',
  showBrackets = false,
  showArrows = false,
  padding = 'default',
  ...props
}) {
  // Calculate responsive thickness
  const responsiveThickness = {
    sm: Math.max(1, thickness - 1),
    md: thickness,
    lg: Math.min(thickness + 1, thickness * 1.5),
  };
  
  // Padding variations
  const paddingStyles = {
    none: '',
    small: 'p-3 md:p-4',
    default: 'p-4 md:p-6',
    large: 'p-6 md:p-8',
  };
  
  // Variant styles
  const variants = {
    default: 'border-spring-green bg-white',
    highlight: 'border-spring-green bg-seafoam-blue',
    subtle: 'border-moss-green bg-white',
  };
  
  // Base frame styles
  const frameStyles = cn(
    'relative border rounded-lg transition-all',
    variants[variant],
    paddingStyles[padding],
    className
  );
  
  // Bracket styles (if enabled)
  const bracketStyles = showBrackets ? {
    before: `before:content-[''] before:absolute before:top-0 before:left-0 before:w-4 before:h-4 before:border-l before:border-t before:border-spring-green`,
    after: `after:content-[''] after:absolute after:bottom-0 after:right-0 after:w-4 after:h-4 after:border-r after:border-b after:border-spring-green`,
  } : {};
  
  // Arrow styles (if enabled)
  const arrowStyles = showArrows ? {
    topRight: `before:content-[''] before:absolute before:top-0 before:right-0 before:w-4 before:h-4 before:border-t before:border-r before:border-spring-green before:transform before:rotate-45`,
    bottomLeft: `after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-4 after:h-4 after:border-b after:border-l after:border-spring-green after:transform after:rotate-45`,
  } : {};
  
  return (
    <div
      className={cn(
        frameStyles,
        bracketStyles.before,
        bracketStyles.after,
        arrowStyles.topRight,
        arrowStyles.bottomLeft
      )}
      style={{
        borderWidth: `${thickness}px`,
        '--frame-thickness-sm': `${responsiveThickness.sm}px`,
        '--frame-thickness-md': `${responsiveThickness.md}px`,
        '--frame-thickness-lg': `${responsiveThickness.lg}px`,
      }}
      {...props}
    >
      {children}
    </div>
  );
}

/**
 * ContentFrame Component
 * 
 * A specialized version of the Frame component that includes a title
 * and optional description. Commonly used for content sections.
 */
export function ContentFrame({
  title,
  description,
  children,
  className,
  titleClassName,
  descriptionClassName,
  ...props
}) {
  return (
    <Frame
      className={cn('space-y-4', className)}
      {...props}
    >
      <div className="space-y-2">
        {title && (
          <h3 className={cn(
            "font-heading text-xl tracking-tightest text-midnight-forest",
            titleClassName
          )}>
            {title}
          </h3>
        )}
        {description && (
          <p className={cn(
            "font-inter text-moss-green",
            descriptionClassName
          )}>
            {description}
          </p>
        )}
      </div>
      {children}
    </Frame>
  );
}

/**
 * CardFrame Component
 * 
 * A Frame variant specifically designed for card layouts.
 * Includes hover states and optional interaction styles.
 */
export function CardFrame({
  children,
  className,
  interactive = false,
  elevated = false,
  ...props
}) {
  return (
    <Frame
      className={cn(
        elevated && 'shadow-md',
        interactive && 'hover:shadow-lg hover:border-spring-green-90 transition-all cursor-pointer',
        className
      )}
      {...props}
    >
      {children}
    </Frame>
  );
}

/**
 * ImageFrame Component
 * 
 * A Frame variant designed to wrap images with the ACT brand styling.
 * Supports both local and remote images with proper optimization.
 */
export function ImageFrame({
  src,
  alt,
  className,
  imageClassName,
  width,
  height,
  ...props
}) {
  return (
    <Frame
      className={cn('p-0 overflow-hidden', className)}
      {...props}
    >
      <img
        src={src}
        alt={alt}
        width={width}
        height={height}
        className={cn(
          'w-full h-full object-cover',
          imageClassName
        )}
      />
    </Frame>
  );
} 