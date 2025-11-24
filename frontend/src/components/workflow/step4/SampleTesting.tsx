'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, XCircle, AlertCircle, Loader2, ArrowRight, RotateCcw } from 'lucide-react';
import { ExtractionResult, Variable } from '@/types';

interface SampleTestingProps {
  projectId: string;
  variables: Variable[];
  totalDocuments: number;
  onApprove: () => void;
  onRefineSchema: () => void;
}

export function SampleTesting({
  projectId,
  variables,
  totalDocuments,
  onApprove,
  onRefineSchema,
}: SampleTestingProps) {
  const [sampleSize, setSampleSize] = useState<number>(10);
  const [isProcessing, setIsProcessing] = useState(false);
  const [sampleResults, setSampleResults] = useState<ExtractionResult[]>([]);
  const [feedback, setFeedback] = useState<Record<string, 'correct' | 'incorrect'>>({});

  const handleRunSample = async () => {
    setIsProcessing(true);
    setSampleResults([]);
    setFeedback({});

    // Simulate processing delay
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Generate mock sample results
    const mockResults: ExtractionResult[] = Array.from({ length: sampleSize }, (_, i) => ({
      id: `sample-${i}`,
      projectId,
      documentId: `doc-${i}`,
      values: variables.map((variable) => {
        const confidence = Math.floor(Math.random() * 40) + 60; // 60-100
        let value: string | number | boolean | null = null;

        if (variable.type === 'text') {
          value = `Sample ${variable.name} ${i + 1}`;
        } else if (variable.type === 'number') {
          value = Math.floor(Math.random() * 100) + 1;
        } else if (variable.type === 'date') {
          value = `2024-0${Math.floor(Math.random() * 9) + 1}-15`;
        } else if (variable.type === 'category' && variable.classificationRules) {
          value = variable.classificationRules[Math.floor(Math.random() * variable.classificationRules.length)];
        } else if (variable.type === 'boolean') {
          value = Math.random() > 0.5;
        }

        return {
          variableId: variable.id,
          value,
          confidence,
          sourceText: `Sample text for document ${i + 1}...`,
        };
      }),
      completedAt: new Date().toISOString(),
    }));

    setSampleResults(mockResults);
    setIsProcessing(false);

    // Show success toast
    toast.success('Sample Processing Complete!', {
      description: `Tested ${sampleSize} documents. Review results and flag any errors.`,
    });
  };

  const handleFeedback = (resultId: string, variableId: string, correct: boolean) => {
    const key = `${resultId}-${variableId}`;
    setFeedback((prev) => ({
      ...prev,
      [key]: correct ? 'correct' : 'incorrect',
    }));
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

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Sample Testing</CardTitle>
          <CardDescription>
            Test extraction on a small sample of documents before processing all {totalDocuments} documents
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="sample-size">Sample Size</Label>
            <Select
              value={sampleSize.toString()}
              onValueChange={(value) => setSampleSize(parseInt(value))}
              disabled={isProcessing}
            >
              <SelectTrigger id="sample-size" className="w-full sm:w-[200px]">
                <SelectValue placeholder="Select sample size" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="5">5 documents</SelectItem>
                <SelectItem value="10">10 documents</SelectItem>
                <SelectItem value="15">15 documents</SelectItem>
                <SelectItem value="20">20 documents</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-sm text-muted-foreground">
              We recommend testing on 10-20 documents to validate extraction accuracy
            </p>
          </div>

          <Button
            onClick={handleRunSample}
            disabled={isProcessing || variables.length === 0}
            className="w-full sm:w-auto"
          >
            {isProcessing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing Sample...
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

      {/* Sample Results */}
      {sampleResults.length > 0 && (
        <>
          <Alert className="bg-blue-50 border-blue-200">
            <AlertCircle className="h-4 w-4 text-blue-600" />
            <AlertDescription className="text-blue-800">
              <span className="font-medium">Review sample results</span>
              {' '}- Check each extracted value and mark it as correct (✓) or incorrect (✗) to help improve accuracy.
            </AlertDescription>
          </Alert>

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Sample Results ({sampleResults.length} documents)</CardTitle>
                  <CardDescription>
                    Review and validate the extracted data
                  </CardDescription>
                </div>
                {hasFeedback && (
                  <Badge variant={accuracy >= 80 ? 'default' : 'destructive'} className="text-base px-4 py-2">
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
                    {sampleResults.map((result, idx) => (
                      <tr key={result.id} className="border-b hover:bg-muted/50">
                        <td className="p-3 font-medium">Doc {idx + 1}</td>
                        {result.values.map((value) => {
                          const feedbackKey = `${result.id}-${value.variableId}`;
                          const userFeedback = feedback[feedbackKey];

                          return (
                            <td key={value.variableId} className="p-3">
                              <div className="space-y-2">
                                <div className="flex items-center gap-2">
                                  <span className={getConfidenceColor(value.confidence)}>
                                    {getConfidenceIcon(value.confidence)}
                                  </span>
                                  <span className="font-mono text-sm">
                                    {String(value.value)}
                                  </span>
                                </div>
                                <div className="text-xs text-muted-foreground">
                                  {value.confidence}% confidence
                                </div>
                                <div className="flex gap-1">
                                  <Button
                                    size="sm"
                                    variant={userFeedback === 'correct' ? 'default' : 'outline'}
                                    className="h-7 px-2"
                                    onClick={() => handleFeedback(result.id, value.variableId, true)}
                                  >
                                    <CheckCircle2 className="h-3 w-3" />
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant={userFeedback === 'incorrect' ? 'destructive' : 'outline'}
                                    className="h-7 px-2"
                                    onClick={() => handleFeedback(result.id, value.variableId, false)}
                                  >
                                    <XCircle className="h-3 w-3" />
                                  </Button>
                                </div>
                              </div>
                            </td>
                          );
                        })}
                      </tr>
                    ))}
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
    </div>
  );
}
