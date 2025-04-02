'use client';

import React from 'react';
import Link from 'next/link';
import { cn } from '../../../lib/utils';
import { Navbar, NavDropdownItem } from './Navbar';
import { Sidebar, SidebarSection, SidebarDivider } from './Sidebar';

export { Navbar, NavDropdownItem } from './Navbar';
export { Sidebar, SidebarSection, SidebarDivider } from './Sidebar';

// Re-export common navigation components
export function Breadcrumbs({
  items = [],
  className,
  separator = '/',
}) {
  return (
    <nav className={cn("flex", className)} aria-label="Breadcrumb">
      <ol className="inline-flex items-center space-x-1 md:space-x-2">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          
          return (
            <li key={item.href || index} className="inline-flex items-center">
              {index > 0 && (
                <span className="mx-2 text-moss-green">{separator}</span>
              )}
              
              {isLast ? (
                <span className="text-midnight-forest">{item.label}</span>
              ) : (
                <Link
                  href={item.href}
                  className="text-moss-green hover:text-spring-green"
                >
                  {item.label}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

export function TabNavigation({
  tabs = [],
  activeTab,
  onChange,
  className,
}) {
  return (
    <div className={cn("border-b border-moss-green/10", className)}>
      <nav className="-mb-px flex space-x-8">
        {tabs.map((tab) => (
          <button
            key={tab.value}
            onClick={() => onChange(tab.value)}
            className={cn(
              "whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm",
              activeTab === tab.value
                ? "border-spring-green text-midnight-forest"
                : "border-transparent text-moss-green hover:text-midnight-forest hover:border-moss-green"
            )}
            aria-current={activeTab === tab.value ? "page" : undefined}
          >
            {tab.label}
          </button>
        ))}
      </nav>
    </div>
  );
}

export function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  className,
}) {
  // Calculate page numbers to show
  const getPageNumbers = () => {
    const pages = [];
    const maxPagesToShow = 5;
    
    if (totalPages <= maxPagesToShow) {
      // Show all pages if total is less than max
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Always show first and last page
      // and 1 or 2 pages around current page
      const leftBound = Math.max(1, currentPage - 1);
      const rightBound = Math.min(totalPages, currentPage + 1);
      
      // First page
      pages.push(1);
      
      // Add ellipsis if needed
      if (leftBound > 2) {
        pages.push('...');
      }
      
      // Pages around current
      for (let i = leftBound; i <= rightBound; i++) {
        if (i !== 1 && i !== totalPages) {
          pages.push(i);
        }
      }
      
      // Add ellipsis if needed
      if (rightBound < totalPages - 1) {
        pages.push('...');
      }
      
      // Last page
      if (totalPages > 1) {
        pages.push(totalPages);
      }
    }
    
    return pages;
  };
  
  const pageNumbers = getPageNumbers();
  
  return (
    <nav
      className={cn("flex items-center justify-between", className)}
      aria-label="Pagination"
    >
      <div className="flex-1 flex justify-between sm:justify-end">
        <button
          onClick={() => onPageChange(Math.max(1, currentPage - 1))}
          disabled={currentPage === 1}
          className={cn(
            "relative inline-flex items-center px-4 py-2 border text-sm font-medium rounded-md",
            currentPage === 1
              ? "border-moss-green/10 text-moss-green/40 cursor-not-allowed"
              : "border-moss-green text-moss-green hover:bg-moss-green/10"
          )}
        >
          Previous
        </button>
        
        <div className="hidden md:flex mx-2 space-x-1">
          {pageNumbers.map((page, index) => (
            <React.Fragment key={index}>
              {page === '...' ? (
                <span className="px-4 py-2 text-sm text-moss-green">
                  {page}
                </span>
              ) : (
                <button
                  onClick={() => onPageChange(page)}
                  className={cn(
                    "px-4 py-2 text-sm font-medium rounded-md",
                    currentPage === page
                      ? "bg-spring-green text-midnight-forest"
                      : "text-moss-green hover:bg-moss-green/10"
                  )}
                  aria-current={currentPage === page ? "page" : undefined}
                >
                  {page}
                </button>
              )}
            </React.Fragment>
          ))}
        </div>
        
        <button
          onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
          disabled={currentPage === totalPages}
          className={cn(
            "relative inline-flex items-center px-4 py-2 ml-3 border text-sm font-medium rounded-md",
            currentPage === totalPages
              ? "border-moss-green/10 text-moss-green/40 cursor-not-allowed"
              : "border-moss-green text-moss-green hover:bg-moss-green/10"
          )}
        >
          Next
        </button>
      </div>
    </nav>
  );
} 