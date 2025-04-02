/**
 * StepProgress Component
 * 
 * Displays a progress bar for multi-step forms with numbered indicators
 * for each step and highlights the current step.
 */
'use client';

import React from 'react';
import { Check } from 'lucide-react';

const StepProgress = ({ currentStep, totalSteps }) => {
  // Create an array of step numbers
  const steps = Array.from({ length: totalSteps }, (_, i) => i + 1);
  
  // Calculate progress percentage
  const progressPercentage = ((currentStep - 1) / (totalSteps - 1)) * 100;
  
  return (
    <div className="relative">
      {/* Progress bar */}
      <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className="h-full bg-spring-green transition-all duration-500 ease-in-out"
          style={{ width: `${progressPercentage}%` }}
        ></div>
      </div>
      
      {/* Step indicators */}
      <div className="flex justify-between mt-[-10px]">
        {steps.map((step) => (
          <div key={step} className="relative">
            <div 
              className={`
                w-6 h-6 rounded-full flex items-center justify-center 
                transition-all duration-300 z-10 relative
                ${step === currentStep 
                  ? 'bg-spring-green text-midnight-forest border-2 border-spring-green' 
                  : step < currentStep 
                    ? 'bg-spring-green text-midnight-forest'
                    : 'bg-white text-gray-400 border-2 border-gray-300'}
              `}
            >
              <span className="text-xs font-bold">{step}</span>
            </div>
            
            {/* Step label (optional) */}
            <span className={`
              absolute top-8 left-1/2 transform -translate-x-1/2 text-xs whitespace-nowrap
              ${step === currentStep ? 'text-midnight-forest font-medium' : 'text-gray-500'}
            `}>
              Step {step}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StepProgress; 