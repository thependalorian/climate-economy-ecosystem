/*
  Select Component
  Provides composable select subcomponents using DaisyUI styles.
  Location: /components/ui/select.jsx
*/

"use client"

import React from 'react';
import { cn } from '../../lib/utils';

export function SelectTrigger({ children, className, ...props }) {
  return (
    <button className={cn('btn', className)} {...props}>
      {children}
    </button>
  );
}

export function SelectValue({ children, className, ...props }) {
  return <span className={cn('select-value', className)} {...props}>{children}</span>;
}

export function SelectContent({ children, className, ...props }) {
  return (
    <div className={cn('select-content', className)} {...props}>
      {children}
    </div>
  );
}

export function SelectItem({ children, className, ...props }) {
  return (
    <button className={cn('select-item', className)} {...props}>
      {children}
    </button>
  );
} 