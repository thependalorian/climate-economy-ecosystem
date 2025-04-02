'use client';

import React from 'react';
import { cn } from '../../../lib/utils';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X, ChevronDown } from 'lucide-react';
import { Button } from '../Button';

/**
 * Navbar Component
 * 
 * Main navigation component that follows ACT brand guidelines.
 * Supports responsive design, dropdown menus, and user authentication state.
 */
export function Navbar({
  logo,
  items = [],
  userMenu,
  className,
}) {
  const [isOpen, setIsOpen] = React.useState(false);
  const pathname = usePathname();

  return (
    <nav className={cn(
      "bg-white border-b border-moss-green/10",
      className
    )}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo and main nav */}
          <div className="flex">
            {/* Logo */}
            <div className="flex-shrink-0 flex items-center">
              {logo}
            </div>

            {/* Desktop Navigation */}
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {items.map((item) => (
                <NavItem
                  key={item.href}
                  {...item}
                  active={pathname === item.href}
                />
              ))}
            </div>
          </div>

          {/* User menu and mobile menu button */}
          <div className="flex items-center">
            {/* User Menu (Desktop) */}
            {userMenu && (
              <div className="hidden sm:ml-6 sm:flex sm:items-center">
                {userMenu}
              </div>
            )}

            {/* Mobile menu button */}
            <div className="flex items-center sm:hidden">
              <Button
                variant="tertiary"
                size="sm"
                onClick={() => setIsOpen(!isOpen)}
                aria-expanded={isOpen}
                icon={isOpen ? <X /> : <Menu />}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isOpen && (
        <div className="sm:hidden">
          <div className="pt-2 pb-3 space-y-1">
            {items.map((item) => (
              <MobileNavItem
                key={item.href}
                {...item}
                active={pathname === item.href}
              />
            ))}
          </div>
          {/* User Menu (Mobile) */}
          {userMenu && (
            <div className="pt-4 pb-3 border-t border-moss-green/10">
              {userMenu}
            </div>
          )}
        </div>
      )}
    </nav>
  );
}

/**
 * NavItem Component
 * 
 * Individual navigation item for desktop view.
 */
function NavItem({
  href,
  label,
  active,
  children,
}) {
  const [isOpen, setIsOpen] = React.useState(false);
  const dropdownRef = React.useRef(null);

  // Close dropdown when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (children) {
    return (
      <div className="relative" ref={dropdownRef}>
        <button
          className={cn(
            "inline-flex items-center px-1 pt-1 text-sm font-medium border-b-2 transition-colors",
            active
              ? "border-spring-green text-midnight-forest"
              : "border-transparent text-moss-green hover:border-moss-green hover:text-midnight-forest"
          )}
          onClick={() => setIsOpen(!isOpen)}
        >
          {label}
          <ChevronDown
            className={cn(
              "ml-1 h-4 w-4 transition-transform",
              isOpen && "transform rotate-180"
            )}
          />
        </button>

        {isOpen && (
          <div className="absolute z-10 left-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5">
            <div className="py-1" role="menu">
              {children}
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <Link
      href={href}
      className={cn(
        "inline-flex items-center px-1 pt-1 text-sm font-medium border-b-2 transition-colors",
        active
          ? "border-spring-green text-midnight-forest"
          : "border-transparent text-moss-green hover:border-moss-green hover:text-midnight-forest"
      )}
    >
      {label}
    </Link>
  );
}

/**
 * MobileNavItem Component
 * 
 * Individual navigation item for mobile view.
 */
function MobileNavItem({
  href,
  label,
  active,
  children,
}) {
  const [isOpen, setIsOpen] = React.useState(false);

  if (children) {
    return (
      <div>
        <button
          className={cn(
            "w-full flex items-center justify-between px-4 py-2 text-sm font-medium transition-colors",
            active
              ? "bg-spring-green/10 text-midnight-forest"
              : "text-moss-green hover:bg-moss-green/10 hover:text-midnight-forest"
          )}
          onClick={() => setIsOpen(!isOpen)}
        >
          {label}
          <ChevronDown
            className={cn(
              "ml-1 h-4 w-4 transition-transform",
              isOpen && "transform rotate-180"
            )}
          />
        </button>

        {isOpen && (
          <div className="pl-4">
            {children}
          </div>
        )}
      </div>
    );
  }

  return (
    <Link
      href={href}
      className={cn(
        "block px-4 py-2 text-sm font-medium transition-colors",
        active
          ? "bg-spring-green/10 text-midnight-forest"
          : "text-moss-green hover:bg-moss-green/10 hover:text-midnight-forest"
      )}
    >
      {label}
    </Link>
  );
}

/**
 * NavDropdownItem Component
 * 
 * Individual item within a dropdown menu.
 */
export function NavDropdownItem({
  href,
  label,
  icon,
  onClick,
}) {
  const content = (
    <>
      {icon && (
        <span className="mr-2 h-4 w-4 text-moss-green">
          {icon}
        </span>
      )}
      {label}
    </>
  );

  if (onClick) {
    return (
      <button
        className="w-full text-left px-4 py-2 text-sm text-moss-green hover:bg-spring-green/10 hover:text-midnight-forest"
        onClick={onClick}
        role="menuitem"
      >
        {content}
      </button>
    );
  }

  return (
    <Link
      href={href}
      className="block px-4 py-2 text-sm text-moss-green hover:bg-spring-green/10 hover:text-midnight-forest"
      role="menuitem"
    >
      {content}
    </Link>
  );
} 