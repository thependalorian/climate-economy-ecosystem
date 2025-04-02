/**
 * Question Component
 * 
 * A reusable component for displaying questions during onboarding.
 * Supports different input types: text, textarea, select, radio, checkbox.
 */
'use client';

import React from 'react';

const Question = ({
  type = 'text',
  label,
  placeholder,
  value,
  onChange,
  options = [],
  required = false,
  helperText,
  error,
  checked,
}) => {
  const renderInput = () => {
    switch (type) {
      case 'text':
        return (
          <input
            type="text"
            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-spring-green focus:ring-1 focus:ring-spring-green"
            placeholder={placeholder}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            required={required}
          />
        );
        
      case 'textarea':
        return (
          <textarea
            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-spring-green focus:ring-1 focus:ring-spring-green min-h-[120px]"
            placeholder={placeholder}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            required={required}
          />
        );
        
      case 'select':
        return (
          <select
            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-spring-green focus:ring-1 focus:ring-spring-green"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            required={required}
          >
            <option value="" disabled>
              {placeholder || 'Select an option'}
            </option>
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );
        
      case 'radio':
        return (
          <div className="space-y-2">
            {options.map((option) => (
              <label key={option.value} className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="radio"
                  className="form-radio h-5 w-5 text-spring-green"
                  checked={value === option.value}
                  onChange={() => onChange(option.value)}
                  required={required}
                />
                <span>{option.label}</span>
              </label>
            ))}
          </div>
        );
        
      case 'checkbox':
        return (
          <label className="flex items-start space-x-3 cursor-pointer">
            <div className="flex items-center h-6">
              <input
                type="checkbox"
                className="form-checkbox h-5 w-5 text-spring-green rounded"
                checked={checked}
                onChange={(e) => onChange(e.target.checked)}
                required={required}
              />
            </div>
            <span>{label}</span>
          </label>
        );
        
      default:
        return null;
    }
  };

  return (
    <div className="mb-4">
      {type !== 'checkbox' && label && (
        <label className="block mb-2 font-medium text-gray-700">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      {renderInput()}
      
      {helperText && (
        <p className="mt-1 text-sm text-gray-500">{helperText}</p>
      )}
      
      {error && (
        <p className="mt-1 text-sm text-red-500">{error}</p>
      )}
    </div>
  );
};

export default Question; 