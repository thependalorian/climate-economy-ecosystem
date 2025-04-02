/**
 * Card Component
 * A reusable card component that follows ACT brand guidelines
 * Location: /components/ui/card.jsx
 */

'use client';

import { cn } from '../../lib/utils';

const Card = ({ className, children, variant = 'default', shadow = true, hover = false }) => {
  const variants = {
    default: 'bg-white border-2 border-spring-green/20',
    primary: 'bg-white border-2 border-spring-green',
    secondary: 'bg-sand-gray border-2 border-moss-green/50',
    highlight: 'bg-seafoam-blue border-2 border-spring-green/50',
    outline: 'bg-transparent border-2 border-spring-green/30',
  };

  const shadowClasses = shadow ? 'shadow-act' : '';
  const hoverClasses = hover ? 'hover:shadow-act-lg transition-shadow' : '';

  return (
    <div className={cn(
      'rounded-lg',
      variants[variant],
      shadowClasses,
      hoverClasses,
      className
    )}>
      {children}
    </div>
  );
};

const CardHeader = ({ className, children }) => {
  return (
    <div className={cn('p-5 border-b border-spring-green/10', className)}>
      {children}
    </div>
  );
};

const CardTitle = ({ className, children }) => {
  return (
    <h3 className={cn('font-heading text-xl tracking-tight leading-tight text-midnight-forest font-semibold', className)}>
      {children}
    </h3>
  );
};

const CardDescription = ({ className, children }) => {
  return (
    <p className={cn('text-sm font-normal text-moss-green mt-1', className)}>
      {children}
    </p>
  );
};

const CardContent = ({ className, children }) => {
  return (
    <div className={cn('p-5 font-inter text-midnight-forest', className)}>
      {children}
    </div>
  );
};

const CardFooter = ({ className, children }) => {
  return (
    <div className={cn('p-5 border-t border-spring-green/10 bg-sand-gray/10', className)}>
      {children}
    </div>
  );
};

export { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter }; 