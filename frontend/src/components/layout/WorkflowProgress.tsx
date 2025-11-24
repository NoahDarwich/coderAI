'use client';

import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';

interface WorkflowStep {
  number: number;
  label: string;
  description: string;
}

const WORKFLOW_STEPS: WorkflowStep[] = [
  { number: 1, label: 'Setup', description: 'Create project & upload documents' },
  { number: 2, label: 'Define', description: 'Define extraction variables' },
  { number: 3, label: 'Review', description: 'Review & finalize schema' },
  { number: 4, label: 'Process', description: 'Extract data from documents' },
  { number: 5, label: 'Export', description: 'Review results & export' },
];

interface WorkflowProgressProps {
  currentStep: number;
  className?: string;
}

export function WorkflowProgress({ currentStep, className }: WorkflowProgressProps) {
  return (
    <div className={cn('w-full', className)}>
      {/* Mobile: Compact view */}
      <div className="md:hidden">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            Step {currentStep} of {WORKFLOW_STEPS.length}
          </span>
          <span className="text-xs text-gray-500">
            {WORKFLOW_STEPS[currentStep - 1]?.label}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${(currentStep / WORKFLOW_STEPS.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Desktop: Full step indicator */}
      <div className="hidden md:block">
        <nav aria-label="Progress">
          <ol className="flex items-center justify-between">
            {WORKFLOW_STEPS.map((step, index) => {
              const isCompleted = step.number < currentStep;
              const isCurrent = step.number === currentStep;
              const isUpcoming = step.number > currentStep;

              return (
                <li key={step.number} className="relative flex-1">
                  {/* Connector line */}
                  {index !== WORKFLOW_STEPS.length - 1 && (
                    <div
                      className={cn(
                        'absolute top-5 left-1/2 w-full h-0.5 -z-10',
                        isCompleted ? 'bg-blue-600' : 'bg-gray-300'
                      )}
                      style={{ left: 'calc(50% + 20px)' }}
                    />
                  )}

                  {/* Step indicator */}
                  <div className="flex flex-col items-center group">
                    <div
                      className={cn(
                        'flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all duration-200',
                        isCompleted && 'bg-blue-600 border-blue-600 text-white',
                        isCurrent && 'bg-white border-blue-600 text-blue-600 shadow-lg',
                        isUpcoming && 'bg-white border-gray-300 text-gray-400'
                      )}
                    >
                      {isCompleted ? (
                        <Check className="w-5 h-5" />
                      ) : (
                        <span className="text-sm font-semibold">{step.number}</span>
                      )}
                    </div>

                    {/* Step label */}
                    <div className="mt-2 text-center max-w-[120px]">
                      <p
                        className={cn(
                          'text-sm font-medium transition-colors',
                          isCurrent && 'text-blue-600',
                          isCompleted && 'text-gray-700',
                          isUpcoming && 'text-gray-400'
                        )}
                      >
                        {step.label}
                      </p>
                      <p
                        className={cn(
                          'text-xs mt-1 transition-colors',
                          isCurrent && 'text-gray-600',
                          isCompleted && 'text-gray-500',
                          isUpcoming && 'text-gray-400'
                        )}
                      >
                        {step.description}
                      </p>
                    </div>
                  </div>
                </li>
              );
            })}
          </ol>
        </nav>
      </div>
    </div>
  );
}
