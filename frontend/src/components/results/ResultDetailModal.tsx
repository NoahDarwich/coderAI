/**
 * ResultDetailModal Component
 * Modal showing detailed view of extraction result
 */

'use client';

import { ExtractionResult } from '@/lib/types/api';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { ConfidenceBadge } from './ConfidenceBadge';
import { SourceTextView } from './SourceTextView';
import { FlagButton } from './FlagButton';
import { formatDate } from '@/lib/utils/formatting';
import { FileText } from 'lucide-react';

interface ResultDetailModalProps {
  result: ExtractionResult | null;
  open: boolean;
  onClose: () => void;
  onToggleFlag?: (resultId: string, flagged: boolean) => void;
}

export function ResultDetailModal({
  result,
  open,
  onClose,
  onToggleFlag,
}: ResultDetailModalProps) {
  if (!result) return null;

  const variables = Object.entries(result.data);

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <DialogTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                {result.documentName}
              </DialogTitle>
              <DialogDescription>
                Extracted on {formatDate(result.extractedAt)}
              </DialogDescription>
            </div>

            {onToggleFlag && (
              <FlagButton
                flagged={result.flagged}
                onToggle={() => onToggleFlag(result.id, !result.flagged)}
                size="sm"
              />
            )}
          </div>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          {/* Extracted variables */}
          {variables.map(([key, data]) => (
            <div key={key} className="space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold capitalize">
                  {key.replace(/_/g, ' ')}
                </h4>
                <ConfidenceBadge confidence={data.confidence} />
              </div>

              {/* Value */}
              <div className="p-3 rounded-lg bg-muted">
                <p className="text-sm font-medium">
                  {data.value !== null ? String(data.value) : 'No value'}
                </p>
              </div>

              {/* Source text */}
              {data.sourceText && (
                <SourceTextView
                  sourceText={data.sourceText}
                  label="Source quote"
                />
              )}
            </div>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}
