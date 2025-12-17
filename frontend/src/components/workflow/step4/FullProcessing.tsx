'use client';

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { ArrowRight, Play, CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ProcessingLog } from './ProcessingLog';
import { useCreateJob, useJobStatus } from '@/lib/api/processing';
import type { Document } from '@/lib/types/api';

interface FullProcessingProps {
  projectId: string;
  documents: Document[];
  onContinue: () => void;
}

export function FullProcessing({
  projectId,
  documents,
  onContinue,
}: FullProcessingProps) {
  const [jobId, setJobId] = useState<string | null>(null);

  // API hooks
  const createJob = useCreateJob(projectId);
  const { data: job, isLoading: jobLoading } = useJobStatus(jobId, !!jobId);

  const isProcessing = job?.status === 'processing' || job?.status === 'pending';
  const isComplete = job?.status === 'completed';
  const isFailed = job?.status === 'failed';

  // Show success toast when complete
  useEffect(() => {
    if (isComplete) {
      toast.success('Processing Complete!', {
        description: `Successfully processed ${job.totalDocuments} documents. View results now.`,
        action: {
          label: 'View Results',
          onClick: onContinue,
        },
      });
    }
  }, [isComplete, job?.totalDocuments, onContinue]);

  // Show error toast when failed
  useEffect(() => {
    if (isFailed) {
      toast.error('Processing Failed', {
        description: 'An error occurred during processing. Check the logs for details.',
      });
    }
  }, [isFailed]);

  const handleStart = async () => {
    if (documents.length === 0) {
      toast.error('No documents available', {
        description: 'Please upload documents before starting full processing.',
      });
      return;
    }

    try {
      // Get all document IDs
      const allDocIds = documents.map(d => d.id);

      // Create FULL job
      const createdJob = await createJob.mutateAsync({
        jobType: 'FULL',
        documentIds: allDocIds,
      });

      setJobId(createdJob.id);

      toast.info('Full processing started', {
        description: `Processing ${allDocIds.length} documents...`,
      });
    } catch (error) {
      console.error('Failed to start full processing:', error);
      toast.error('Failed to start processing', {
        description: error instanceof Error ? error.message : 'Unknown error occurred',
      });
    }
  };

  const canStart = documents.length > 0 && !jobId;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Full Processing</CardTitle>
          <CardDescription>
            Process all {documents.length} documents with the approved schema
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {documents.length === 0 && (
            <Alert variant="destructive">
              <AlertDescription>
                No documents uploaded. Please upload documents before starting full processing.
              </AlertDescription>
            </Alert>
          )}

          {!job && (
            <div className="text-center py-8">
              <p className="text-gray-600 mb-4">
                Ready to process all {documents.length} documents
              </p>
              <Button
                size="lg"
                onClick={handleStart}
                disabled={!canStart || createJob.isPending}
                aria-label="Start processing all documents with extraction schema"
              >
                {createJob.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Starting...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" aria-hidden="true" />
                    Start Full Processing
                  </>
                )}
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
                  <span className="font-medium" aria-label={`${job.progress} percent complete`}>
                    {job.progress}%
                  </span>
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
                <div className="flex items-center gap-2 text-red-700 bg-red-50 p-4 rounded-lg" role="alert">
                  <XCircle className="w-5 h-5" />
                  <div>
                    <p className="font-medium">Processing Failed</p>
                    <p className="text-sm">
                      An error occurred during processing. Check the logs for details.
                    </p>
                  </div>
                </div>
              )}

              {isProcessing && (
                <Alert className="bg-blue-50 border-blue-200">
                  <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                  <AlertDescription className="text-blue-800">
                    <span className="font-medium">Processing in progress...</span>
                    {' '}This may take several minutes depending on the number of documents.
                  </AlertDescription>
                </Alert>
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
      {job && job.logs && job.logs.length > 0 && (
        <ProcessingLog logs={job.logs} isProcessing={isProcessing} />
      )}
    </div>
  );
}
