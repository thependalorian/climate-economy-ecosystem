/**
 * Tabs Component
 * A reusable tabs component that follows ACT brand guidelines
 * Location: /components/ui/tabs.jsx
 */

'use client';

const Tabs = ({ children, className = '' }) => {
  return (
    <div className={`font-inter ${className}`}>
      {children}
    </div>
  );
};

const TabsList = ({ children, className = '' }) => {
  return (
    <div className={`flex space-x-2 border-b border-spring-green ${className}`}>
      {children}
    </div>
  );
};

const TabsTrigger = ({ 
  children, 
  active = false, 
  onClick,
  className = '' 
}) => {
  return (
    <button
      className={`
        px-4 py-2 font-inter text-base transition-colors
        focus:outline-none focus:ring-2 focus:ring-spring-green focus:ring-offset-2
        ${active 
          ? 'text-midnight-forest border-b-2 border-spring-green bg-seafoam-blue' 
          : 'text-moss-green hover:text-spring-green'
        } 
        ${className}
      `}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

const TabsContent = ({ 
  children,
  active = false,
  className = '' 
}) => {
  if (!active) return null;
  
  return (
    <div className={`py-4 font-inter leading-body text-midnight-forest ${className}`}>
      {children}
    </div>
  );
};

export { Tabs, TabsList, TabsTrigger, TabsContent }; 