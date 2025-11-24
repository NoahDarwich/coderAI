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
    <div className="flex items-center justify-between pt-6 border-t">
      {/* Left side - Previous button */}
      <div>
        {canGoPrevious && onPrevious && (
          <Button
            type="button"
            variant="outline"
            onClick={onPrevious}
            aria-label="Go to previous variable"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Previous
          </Button>
        )}
      </div>

      {/* Center - Progress indicator */}
      <div className="text-sm text-gray-600">
        {totalVariables > 0 ? (
          <span>
            Variable {currentIndex + 1} of {totalVariables}
          </span>
        ) : (
          <span>Add your first variable</span>
        )}
      </div>

      {/* Right side - Next/Add/Finish buttons */}
      <div className="flex gap-2">
        {onAddAnother && (
          <Button
            type="button"
            variant="outline"
            onClick={onAddAnother}
            aria-label="Add another variable"
          >
            <Plus className="w-4 h-4 mr-2" />
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
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        )}

        {isLastVariable && onFinish && (
          <Button
            type="button"
            onClick={onFinish}
            disabled={!canGoNext}
            aria-label="Finish defining variables"
          >
            Continue to Review
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        )}
      </div>
    </div>
  );
}
