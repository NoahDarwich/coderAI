'use client';

import { ArrowLeft, ArrowRight, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface WizardNavigationProps {
  currentIndex: number;
  totalVariables: number;
  onPrevious?: () => void;
  onNext?: () => void;
  onAddAnother?: () => void;
  onFinish?: () => void;
  canGoNext: boolean;
  canGoPrevious: boolean;
  isLastVariable: boolean;
}

export function WizardNavigation({
  currentIndex,
  totalVariables,
  onPrevious,
  onNext,
  onAddAnother,
  onFinish,
  canGoNext,
  canGoPrevious,
  isLastVariable,
}: WizardNavigationProps) {
  return (
    <nav className="flex items-center justify-between pt-6 border-t" aria-label="Wizard navigation">
      {/* Left side - Previous button */}
      <div>
        {canGoPrevious && onPrevious && (
          <Button
            type="button"
            variant="outline"
            onClick={onPrevious}
            aria-label="Go to previous variable"
          >
            <ArrowLeft className="w-4 h-4 mr-2" aria-hidden="true" />
            Previous
          </Button>
        )}
      </div>

      {/* Center - Progress indicator */}
      <div className="text-sm text-gray-600" role="status" aria-live="polite">
        {totalVariables > 0 ? (
          <span>
            Variable {currentIndex + 1} of {totalVariables}
          </span>
        ) : (
          <span>Add your first variable</span>
        )}
      </div>

      {/* Right side - Next/Add/Finish buttons */}
      <div className="flex gap-2" role="group" aria-label="Navigation actions">
        {onAddAnother && (
          <Button
            type="button"
            variant="outline"
            onClick={onAddAnother}
            aria-label="Add another variable to schema"
          >
            <Plus className="w-4 h-4 mr-2" aria-hidden="true" />
            Add Another
          </Button>
        )}

        {!isLastVariable && canGoNext && onNext && (
          <Button
            type="button"
            onClick={onNext}
            aria-label="Go to next variable"
          >
            Next
            <ArrowRight className="w-4 h-4 ml-2" aria-hidden="true" />
          </Button>
        )}

        {isLastVariable && onFinish && (
          <Button
            type="button"
            onClick={onFinish}
            disabled={!canGoNext}
            aria-label="Finish defining variables and continue to review"
            aria-disabled={!canGoNext}
          >
            Continue to Review
            <ArrowRight className="w-4 h-4 ml-2" aria-hidden="true" />
          </Button>
        )}
      </div>
    </nav>
  );
}
