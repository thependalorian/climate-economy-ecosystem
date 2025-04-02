/**
 * SelectableCard Component
 * 
 * A selectable card component for visually choosing options during onboarding.
 * Used for persona selection and other choice-based questions.
 */
'use client';

import React from 'react';
import { Check } from 'lucide-react';

const SelectableCard = ({
  selected = false,
  onClick,
  icon,
  title,
  description,
  disabled = false
}) => {
  return (
    <div
      className={`
        relative p-4 rounded-lg border-2 transition-all duration-200
        ${selected 
          ? 'border-spring-green bg-spring-green/10 shadow-md' 
          : 'border-gray-200 bg-white hover:border-gray-300'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}
      onClick={disabled ? undefined : onClick}
    >
      {/* Selection indicator */}
      {selected && (
        <div className="absolute top-3 right-3 bg-spring-green rounded-full p-1">
          <Check size={16} className="text-midnight-forest" />
        </div>
      )}
      
      <div className="flex items-start">
        {/* Icon container */}
        {icon && (
          <div className="bg-midnight-forest rounded-full p-3 mr-4 flex-shrink-0">
            {icon}
          </div>
        )}
        
        {/* Content */}
        <div>
          <h3 className="font-medium text-midnight-forest text-lg mb-1">{title}</h3>
          {description && <p className="text-gray-600 text-sm">{description}</p>}
        </div>
      </div>
    </div>
  );
};

export default SelectableCard; 