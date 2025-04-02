import { cn } from '../../../lib/utils';
export { Input } from './Input';
export { Select, MultiSelect } from './Select';
export { Checkbox, CheckboxGroup, IndeterminateCheckbox } from './Checkbox';
export { Radio, RadioGroup, RadioCard, RadioCardGroup } from './Radio';
export { TextArea } from './TextArea';

// Form layout components
export function FormGroup({ children, className }) {
  return (
    <div className={cn("space-y-6", className)}>
      {children}
    </div>
  );
}

export function FormRow({ children, className }) {
  return (
    <div className={cn("grid grid-cols-1 gap-6 sm:grid-cols-2", className)}>
      {children}
    </div>
  );
}

export function FormSection({ title, description, children, className }) {
  return (
    <div className={cn("space-y-6", className)}>
      {(title || description) && (
        <div className="space-y-1">
          {title && (
            <h3 className="font-heading text-lg tracking-tightest text-midnight-forest">
              {title}
            </h3>
          )}
          {description && (
            <p className="text-sm text-moss-green">
              {description}
            </p>
          )}
        </div>
      )}
      {children}
    </div>
  );
}

export function FormActions({ children, className }) {
  return (
    <div className={cn("flex items-center justify-end space-x-4 mt-8", className)}>
      {children}
    </div>
  );
} 