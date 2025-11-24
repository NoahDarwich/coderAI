'use client';

import { ArrowRight, Play, CheckCircle2, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { ProcessingLog } from './ProcessingLog';
import { ProcessingJob } from '@/types';

interface FullProcessingProps {
  job: ProcessingJob | null;
  onStart: () => void;
  onContinue: () => void;
  isProcessing: boolean;
  canStart: boolean;
}

export function FullProcessing({
  job,
  onStart,
  onContinue,
  isProcessing,
  canStart,
}: FullProcessingProps) {
  const isComplete = job?.status === 'completed';
  const isFailed = job?.status === 'failed';

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Full Processing</CardTitle>
          <CardDescription>
            Process all documents with the approved schema
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!job && (
            <div className="text-center py-8">
              <p className="text-gray-600 mb-4">
                Ready to process all {canStart ? 'your' : ''} documents
              </p>
              <Button
                size="lg"
                onClick={onStart}
                disabled={!canStart || isProcessing}
                aria-label="Start processing all documents with extraction schema"
              >
                <Play className="w-4 h-4 mr-2" aria-hidden="true" />
                Start Full Processing
              </Button>
            </div>
          )}

          {job && (
            <>
              {/* Progress Bar */}
              <div className="space-y-2" role="region" aria-label="Processing progress">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600" aria-live="polite">
                    Processing {job.processedDocuments} of {job.totalDocuments} documents
                  </span>
                  <span className="font-medium" aria-label={`${job.progress} percent complete`}>{job.progress}%</span>
                </div>
                <Progress value={job.progress} className="h-2" aria-label="Processing progress bar" />
              </div>

              {/* Status Message */}
              {isComplete && (
                <div className="flex items-center gap-2 text-green-700 bg-green-50 p-4 rounded-lg" role="alert" aria-live="polite">
                  <CheckCircle2 className="w-5 h-5" aria-hidden="true" />
                  <div>
                    <p className="font-medium">Processing Complete!</p>
                    <p className="text-sm">
                      Successfully processed {job.totalDocuments} documents
                    </p>
                  </div>
                </div>
              )}

              {isFailed && (
                <div className="flex items-center gap-2 text-red-700 bg-red-50 p-4 rounded-lg">
                  <XCircle className="w-5 h-5" />
                  <div>
                    <p className="font-medium">Processing Failed</p>
                    <p className="text-sm">
                      An error occurred during processing. Check the logs for details.
                    </p>
                  </div>
                </div>
              )}

              {/* Continue Button */}
              {isComplete && (
                <div className="flex justify-end pt-4">
                  <Button size="lg" onClick={onContinue}>
                    View Results
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Processing Log */}
      {job && (
        <ProcessingLog logs={job.logs} isProcessing={isProcessing} />
      )}
    </div>
  );
}
