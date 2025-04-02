'use client';

import React from 'react';
import { cn } from '../../../lib/utils';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ChevronRight, ChevronDown } from 'lucide-react';

/**
 * Sidebar Component
 * 
 * A vertical navigation component that follows ACT brand guidelines.
 * Supports nested navigation, collapsible sections, and responsive design.
 */
export function Sidebar({
  items = [],
  collapsed = false,
  onCollapse,
  className,
}) {
  return (
    <div
      className={cn(
        "flex flex-col h-full bg-white border-r border-moss-green/10",
        collapsed ? "w-16" : "w-64",
        "transition-all duration-200",
        className
      )}
    >
      <div className="flex-1 overflow-y-auto">
        <nav className="px-2 py-4 space-y-1">
          {items.map((item, index) => (
            <SidebarItem
              key={item.href || index}
              collapsed={collapsed}
              {...item}
            />
          ))}
        </nav>
      </div>

      {onCollapse && (
        <div className="p-4 border-t border-moss-green/10">
          <button
            onClick={onCollapse}
            className="w-full flex items-center justify-center p-2 text-moss-green hover:text-midnight-forest hover:bg-spring-green/10 rounded-md transition-colors"
          >
            <ChevronRight
              className={cn(
                "h-5 w-5 transition-transform",
                collapsed ? "" : "transform rotate-180"
              )}
            />
          </button>
        </div>
      )}
    </div>
  );
}

/**
 * SidebarItem Component
 * 
 * Individual navigation item within the sidebar.
 */
function SidebarItem({
  href,
  label,
  icon,
  badge,
  children,
  collapsed,
}) {
  const [isOpen, setIsOpen] = React.useState(false);
  const pathname = usePathname();
  const active = pathname === href;
  const hasChildren = children && children.length > 0;

  // Base styles for items
  const baseStyles = "flex items-center w-full px-3 py-2 text-sm font-medium rounded-md transition-colors";
  const activeStyles = "bg-spring-green/10 text-midnight-forest";
  const inactiveStyles = "text-moss-green hover:bg-moss-green/10 hover:text-midnight-forest";

  if (hasChildren) {
    return (
      <div>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            baseStyles,
            active ? activeStyles : inactiveStyles
          )}
        >
          {icon && (
            <span className="flex-shrink-0">
              {icon}
            </span>
          )}
          {!collapsed && (
            <>
              <span className="flex-1 ml-3">{label}</span>
              <ChevronDown
                className={cn(
                  "flex-shrink-0 h-4 w-4 transition-transform",
                  isOpen && "transform rotate-180"
                )}
              />
            </>
          )}
        </button>

        {!collapsed && isOpen && (
          <div className="mt-1 pl-4 space-y-1">
            {children.map((child, index) => (
              <Link
                key={child.href || index}
                href={child.href}
                className={cn(
                  "block px-3 py-2 text-sm font-medium rounded-md transition-colors",
                  pathname === child.href
                    ? "bg-spring-green/10 text-midnight-forest"
                    : "text-moss-green hover:bg-moss-green/10 hover:text-midnight-forest"
                )}
              >
                {child.label}
              </Link>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <Link
      href={href}
      className={cn(
        baseStyles,
        active ? activeStyles : inactiveStyles
      )}
    >
      {icon && (
        <span className="flex-shrink-0">
          {icon}
        </span>
      )}
      {!collapsed && (
        <>
          <span className="flex-1 ml-3">{label}</span>
          {badge && (
            <span className={cn(
              "ml-2 px-2 py-0.5 text-xs font-medium rounded-full",
              typeof badge === 'number'
                ? "bg-spring-green text-midnight-forest"
                : "bg-moss-green/10 text-moss-green"
            )}>
              {badge}
            </span>
          )}
        </>
      )}
    </Link>
  );
}

/**
 * SidebarSection Component
 * 
 * A grouping component for sidebar items with an optional title.
 */
export function SidebarSection({
  title,
  children,
  collapsed,
  className,
}) {
  return (
    <div
      className={cn(
        "py-4",
        className
      )}
    >
      {title && !collapsed && (
        <h3 className="px-3 mb-2 text-xs font-semibold text-moss-green uppercase tracking-wider">
          {title}
        </h3>
      )}
      <div className="space-y-1">
        {children}
      </div>
    </div>
  );
}

/**
 * SidebarDivider Component
 * 
 * A visual separator between sidebar sections.
 */
export function SidebarDivider({
  className,
}) {
  return (
    <div
      className={cn(
        "mx-2 border-t border-moss-green/10",
        className
      )}
    />
  );
} 