'use client';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { FileText } from 'lucide-react';
import { getConfidenceEmoji } from '@/lib/utils';

interface SourceTextModalProps {
  open: boolean;
  onClose: () => void;
  variableName: string;
  value: string | number | boolean | null;
  confidence: number;
  sourceText: string;
  documentName: string;
}

export function SourceTextModal({
  open,
  onClose,
  variableName,
  value,
  confidence,
  sourceText,
  documentName,
}: SourceTextModalProps) {
  const emoji = getConfidenceEmoji(confidence);

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Source Text
          </DialogTitle>
          <DialogDescription>
            View the source text used to extract this value
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Document Info */}
          <div className="bg-gray-50 rounded-lg p-4 space-y-2">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs text-gray-500 mb-1">Document</div>
                <div className="font-medium text-sm">{documentName}</div>
              </div>
              <Badge variant="outline" className="ml-auto">
                {emoji} {confidence}%
              </Badge>
            </div>
          </div>

          {/* Extracted Value */}
          <div>
            <div className="text-xs text-gray-500 mb-1">Variable: {variableName}</div>
            <div className="font-semibold text-lg">
              {value !== null && value !== undefined ? String(value) : '-'}
            </div>
          </div>

          {/* Source Text */}
          <div>
            <div className="text-xs text-gray-500 mb-2">Source Text</div>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                {sourceText}
              </p>
            </div>
          </div>

          {/* Confidence Explanation */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="text-xs font-medium text-blue-900 mb-1">
              Confidence Score
            </div>
            <div className="text-xs text-blue-700">
              {confidence >= 90
                ? 'High confidence - The AI is very certain this extraction is correct.'
                : confidence >= 70
                ? 'Medium confidence - The AI is reasonably confident about this extraction.'
                : 'Low confidence - The AI found this value but is less certain about accuracy.'}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
