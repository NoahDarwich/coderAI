'use client';

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { Minus, Plus, Pin, CheckCircle2, XCircle, AlertCircle, Loader2, ArrowRight, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { useCreateJob, useJobStatus, useJobResults } from '@/lib/api/processing';
import { usePostFeedback, useAddGoldenExample } from '@/lib/api/extraction';
import type { BackendExtraction } from '@/lib/api/transforms';
import type { Document } from '@/lib/types/api';
import type { SchemaVariable } from '@/lib/types/api';

interface SampleTestingProps {
  projectId: string;
  documents: Document[];
  variables: SchemaVariable[];
  totalDocuments: number;
  onApprove: () => void;
  onRefineSchema: () => void;
}

export function SampleTesting({
  projectId,
  documents,
  variables,
  totalDocuments,
  onApprove,
  onRefineSchema,
}: SampleTestingProps) {
  const [sampleSize, setSampleSize] = useState<number>(Math.min(10, documents.length));
  const [sampleSizeRaw, setSampleSizeRaw] = useState<string>(String(Math.min(10, documents.length) || 1));
  const [jobId, setJobId] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<Record<string, 'correct' | 'incorrect'>>({});
  const [pinTarget, setPinTarget] = useState<{
    extraction: BackendExtraction;
    variableId: string;
    variableName: string;
    documentName: string;
  } | null>(null);

  // API hooks
  const postFeedback = usePostFeedback();
  const addGoldenExample = useAddGoldenExample();

  // Keep default in sync with document count on first load
  useEffect(() => {
    if (documents.length > 0) {
      setSampleSize((prev) => {
        const clamped = Math.min(prev, documents.length);
        setSampleSizeRaw(String(clamped));
        return clamped;
      });
    }
  }, [documents.length]);

  const createJob = useCreateJob(projectId);
  const { data: job, isLoading: jobLoading } = useJobStatus(jobId, !!jobId);
  const { data: results, isLoading: resultsLoading } = useJobResults(
    jobId,
    job?.status === 'completed'
  );

  const isProcessing = job?.status === 'processing' || job?.status === 'pending';
  const isComplete = job?.status === 'completed';
  const hasFailed = job?.status === 'failed';

  // Reset job when sample size changes (only when idle)
  useEffect(() => {
    if (!isProcessing && !isComplete) {
      setJobId(null);
      setFeedback({});
    }
  }, [sampleSize, isProcessing, isComplete]);

  const handleRunSample = async () => {
    if (documents.length === 0) {
      toast.error('No documents available', {
        description: 'Please upload documents before running sample test.',
      });
      return;
    }

    if (variables.length === 0) {
      toast.error('No variables defined', {
        description: 'Please define variables in your schema first.',
      });
      return;
    }

    try {
      const actualSampleSize = Math.min(sampleSize, documents.length);
      const sampleDocIds = documents.slice(0, actualSampleSize).map((d) => d.id);

      const createdJob = await createJob.mutateAsync({
        jobType: 'SAMPLE',
        documentIds: sampleDocIds,
      });

      setJobId(createdJob.id);
      setFeedback({});

      toast.info('Sample processing started', {
        description: `Processing ${actualSampleSize} of ${documents.length} documents…`,
      });
    } catch (error) {
      console.error('Failed to start sample processing:', error);
      toast.error('Failed to start processing', {
        description: error instanceof Error ? error.message : 'Unknown error occurred',
      });
    }
  };

  // Show success toast when complete
  useEffect(() => {
    if (isComplete && results) {
      toast.success('Sample Processing Complete!', {
        description: `Processed ${results.extractions.length} extractions. Review results below.`,
      });
    }
  }, [isComplete, results]);

  // Show error toast when failed
  useEffect(() => {
    if (hasFailed) {
      toast.error('Processing Failed', {
        description: 'An error occurred during processing. Check the logs for details.',
      });
    }
  }, [hasFailed]);

  const handleFeedback = (extractionId: string, correct: boolean) => {
    const newValue = correct ? 'correct' : 'incorrect';
    if (feedback[extractionId] !== newValue) {
      setFeedback((prev) => ({ ...prev, [extractionId]: newValue }));
      postFeedback.mutate({
        extractionId,
        feedbackType: correct ? 'CORRECT' : 'INCORRECT',
      });
    }
  };

  const handlePinClick = (
    extraction: BackendExtraction,
    variableId: string,
    variableName: string,
    documentName: string,
  ) => {
    setPinTarget({ extraction, variableId, variableName, documentName });
  };

  const handleConfirmPin = (useInPrompt: boolean) => {
    if (!pinTarget) return;
    addGoldenExample.mutate({
      variableId: pinTarget.variableId,
      sourceText: pinTarget.extraction.source_text ?? String(pinTarget.extraction.value ?? ''),
      value: pinTarget.extraction.value,
      documentName: pinTarget.documentName,
      useInPrompt,
    });
    setPinTarget(null);
    toast.success('Example pinned', {
      description: useInPrompt
        ? `"${pinTarget.variableName}" will use this as a few-shot example.`
        : 'Saved for reference.',
    });
  };

  const maxSample = documents.length || 1;

  const clampSampleSize = (v: number) => Math.min(Math.max(1, v), maxSample);

  const changeSampleSize = (delta: number) => {
    setSampleSize((prev) => {
      const next = clampSampleSize(prev + delta);
      setSampleSizeRaw(String(next));
      return next;
    });
  };

  const handleSampleSizeInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSampleSizeRaw(e.target.value);
  };

  const handleSampleSizeBlur = () => {
    const v = parseInt(sampleSizeRaw, 10);
    const clamped = isNaN(v) ? sampleSize : clampSampleSize(v);
    setSampleSize(clamped);
    setSampleSizeRaw(String(clamped));
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 85) return 'text-green-600';
    if (confidence >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceIcon = (confidence: number) => {
    if (confidence >= 85) return '🟢';
    if (confidence >= 70) return '🟡';
    return '🔴';
  };

  const calculateAccuracy = () => {
    const total = Object.keys(feedback).length;
    if (total === 0) return 0;
    const correct = Object.values(feedback).filter((f) => f === 'correct').length;
    return Math.round((correct / total) * 100);
  };

  const accuracy = calculateAccuracy();
  const hasFeedback = Object.keys(feedback).length > 0;

  // Group extractions by document
  const extractionsByDocument =
    results?.extractions.reduce(
      (acc, extraction) => {
        if (!acc[extraction.document_id]) {
          acc[extraction.document_id] = [];
        }
        acc[extraction.document_id].push(extraction);
        return acc;
      },
      {} as Record<string, typeof results.extractions>
    ) || {};

  const documentIds = Object.keys(extractionsByDocument);
  const isDisabled = isProcessing || createJob.isPending;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Sample Testing</CardTitle>
          <CardDescription>
            Test extraction on a small sample of documents before processing all{' '}
            {totalDocuments} documents
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Sample size stepper */}
          <div className="space-y-2">
            <Label>Sample Size</Label>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="icon"
                onClick={() => changeSampleSize(-1)}
                disabled={isDisabled || sampleSize <= 1}
                aria-label="Decrease sample size"
              >
                <Minus className="h-4 w-4" />
              </Button>
              <Input
                type="number"
                min={1}
                max={maxSample}
                value={sampleSizeRaw}
                onChange={handleSampleSizeInput}
                onBlur={handleSampleSizeBlur}
                disabled={isDisabled}
                className="w-20 text-center [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                aria-label="Sample size"
              />
              <Button
                variant="outline"
                size="icon"
                onClick={() => changeSampleSize(1)}
                disabled={isDisabled || sampleSize >= maxSample}
                aria-label="Increase sample size"
              >
                <Plus className="h-4 w-4" />
              </Button>
              <span className="text-sm text-muted-foreground">
                of {documents.length} document{documents.length !== 1 ? 's' : ''}
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              We recommend testing on 10–20 documents to validate extraction accuracy
            </p>
          </div>

          {documents.length === 0 && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                No documents uploaded. Please upload documents before running sample test.
              </AlertDescription>
            </Alert>
          )}

          {variables.length === 0 && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                No variables defined. Please define variables in your schema first.
              </AlertDescription>
            </Alert>
          )}

          <Button
            onClick={handleRunSample}
            disabled={isDisabled || variables.length === 0 || documents.length === 0}
            className="w-full sm:w-auto"
          >
            {isDisabled ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing Sample…
              </>
            ) : (
              <>
                <RotateCcw className="mr-2 h-4 w-4" />
                Run Sample Test
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Processing Progress */}
      {job && isProcessing && (
        <Card>
          <CardHeader>
            <CardTitle>Processing…</CardTitle>
            <CardDescription>Extracting data from sample documents</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">
                  Processing {job.processedDocuments} of {job.totalDocuments} documents
                </span>
                <span className="font-medium">{job.progress}%</span>
              </div>
              <Progress value={job.progress} className="h-2" />
            </div>

            {job.logs && job.logs.length > 0 && (
              <div className="text-sm space-y-1 max-h-32 overflow-y-auto">
                {job.logs.slice(-5).map((log, idx) => (
                  <div key={idx} className="text-gray-600">
                    {log.message}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Sample Results */}
      {isComplete && results && documentIds.length > 0 && (
        <>
          <Alert className="bg-blue-50 border-blue-200">
            <AlertCircle className="h-4 w-4 text-blue-600" />
            <AlertDescription className="text-blue-800">
              <span className="font-medium">Review sample results</span>
              {' '}— Check each extracted value and mark it as correct (✓) or incorrect (✗) to
              help improve accuracy.
            </AlertDescription>
          </Alert>

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Sample Results ({documentIds.length} documents)</CardTitle>
                  <CardDescription>Review and validate the extracted data</CardDescription>
                </div>
                {hasFeedback && (
                  <Badge
                    variant={accuracy >= 80 ? 'default' : 'destructive'}
                    className="text-base px-4 py-2"
                  >
                    {accuracy}% accuracy
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-3 font-medium">Document</th>
                      {variables.map((variable) => (
                        <th key={variable.id} className="text-left p-3 font-medium">
                          {variable.name}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {documentIds.map((docId, idx) => {
                      const docExtractions = extractionsByDocument[docId];
                      const document = documents.find((d) => d.id === docId);

                      return (
                        <tr key={docId} className="border-b hover:bg-muted/50">
                          <td className="p-3 font-medium">
                            {document?.filename || `Doc ${idx + 1}`}
                          </td>
                          {variables.map((variable) => {
                            const extraction = docExtractions.find(
                              (e) => e.variable_id === variable.id
                            );
                            const userFeedback = extraction
                              ? feedback[extraction.id]
                              : undefined;

                            if (!extraction) {
                              return (
                                <td key={variable.id} className="p-3">
                                  <span className="text-gray-400">N/A</span>
                                </td>
                              );
                            }

                            return (
                              <td key={variable.id} className="p-3">
                                <div className="space-y-2">
                                  <div className="flex items-center gap-2">
                                    <span className={getConfidenceColor(extraction.confidence)}>
                                      {getConfidenceIcon(extraction.confidence)}
                                    </span>
                                    <span className="font-mono text-sm">
                                      {String(extraction.value || 'null')}
                                    </span>
                                  </div>
                                  <div className="text-xs text-muted-foreground">
                                    {extraction.confidence}% confidence
                                  </div>
                                  {extraction.source_text && (
                                    <div className="text-xs text-muted-foreground italic">
                                      "{extraction.source_text.substring(0, 50)}…"
                                    </div>
                                  )}
                                  <div className="flex gap-1">
                                    <Button
                                      size="sm"
                                      variant={
                                        userFeedback === 'correct' ? 'default' : 'outline'
                                      }
                                      className="h-7 px-2"
                                      title="Mark as correct"
                                      onClick={() => handleFeedback(extraction.id, true)}
                                    >
                                      <CheckCircle2 className="h-3 w-3" />
                                    </Button>
                                    <Button
                                      size="sm"
                                      variant={
                                        userFeedback === 'incorrect'
                                          ? 'destructive'
                                          : 'outline'
                                      }
                                      className="h-7 px-2"
                                      title="Mark as incorrect"
                                      onClick={() => handleFeedback(extraction.id, false)}
                                    >
                                      <XCircle className="h-3 w-3" />
                                    </Button>
                                    {extraction.value !== null && extraction.value !== undefined && (
                                      <Button
                                        size="sm"
                                        variant="outline"
                                        className="h-7 px-2"
                                        title="Pin as example"
                                        onClick={() =>
                                          handlePinClick(
                                            extraction,
                                            variable.id,
                                            variable.name,
                                            document?.filename ?? document?.name ?? `Doc ${idx + 1}`,
                                          )
                                        }
                                      >
                                        <Pin className="h-3 w-3" />
                                      </Button>
                                    )}
                                  </div>
                                </div>
                              </td>
                            );
                          })}
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-between">
            <Button variant="outline" onClick={onRefineSchema}>
              <RotateCcw className="mr-2 h-4 w-4" />
              Refine Schema
            </Button>
            <Button onClick={onApprove} disabled={!hasFeedback || accuracy < 50}>
              Approve for Full Processing
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </>
      )}

      {/* Failed State */}
      {hasFailed && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>
            Processing failed. Please check your configuration and try again.
          </AlertDescription>
        </Alert>
      )}

      {/* Pin Example Dialog */}
      <AlertDialog open={pinTarget !== null} onOpenChange={(open) => !open && setPinTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Pin this example?</AlertDialogTitle>
            <AlertDialogDescription>
              Pin this extraction result for{' '}
              <span className="font-medium">{pinTarget?.variableName}</span> as a few-shot example.
              Future LLM prompts can use it to improve extraction accuracy.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className="flex-col sm:flex-row gap-2">
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => handleConfirmPin(false)}
              className="bg-secondary text-secondary-foreground hover:bg-secondary/80"
            >
              Save for Reference
            </AlertDialogAction>
            <AlertDialogAction onClick={() => handleConfirmPin(true)}>
              Use in Future Prompts
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
