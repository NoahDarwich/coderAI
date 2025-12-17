/**
 * Results Page - Step 5: View and export extraction results
 */

'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, CheckCircle2, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ResultsDataTable } from '@/components/results/ResultsDataTable';
import { WorkflowProgress } from '@/components/layout/WorkflowProgress';
import { apiClient } from '@/lib/api/client';

interface DocumentResult {
  document_id: string;
  document_name: string;
  data: Record<string, any>;
  average_confidence: number;
  flagged: boolean;
}

export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const [mounted, setMounted] = useState(false);
  const [results, setResults] = useState<DocumentResult[]>([]);
  const [variables, setVariables] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Load results from API
  useEffect(() => {
    if (!mounted) return;

    const loadResults = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const useMockData = process.env.NEXT_PUBLIC_USE_MOCK_DATA === 'true';

        if (useMockData) {
          // Mock data mode
          await new Promise((resolve) => setTimeout(resolve, 1000));
          setResults([]);
          setVariables([]);
        } else {
          // Real API calls

          // Fetch project results
          const resultsResponse = await apiClient.get(
            `/api/v1/projects/${projectId}/results`
          ) as any;

          if (resultsResponse && resultsResponse.documents) {
            setResults(resultsResponse.documents);

            // Fetch variables to get correct order
            const variablesResponse = await apiClient.get(
              `/api/v1/projects/${projectId}/variables`
            ) as any[];

            if (variablesResponse && Array.isArray(variablesResponse)) {
              const orderedNames = variablesResponse
                .sort((a, b) => (a.order || 0) - (b.order || 0))
                .map((v: any) => v.name);
              setVariables(orderedNames);
            }
          }
        }
      } catch (err) {
        console.error('Failed to load results:', err);
        setError('Failed to load results. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    loadResults();
  }, [projectId, mounted]);

  if (!mounted) {
    return null;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Button
        variant="ghost"
        onClick={() => router.push(`/projects/${projectId}`)}
        className="mb-6"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Project
      </Button>

      <div className="mb-8">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Extraction Results
            </h1>
            <p className="text-gray-600">
              Review extracted data and export to CSV
            </p>
          </div>
          <div className="flex gap-2">
            {!isLoading && results.length > 0 && (
              <ExportModal
                results={results}
                variables={variables}
                documentNames={documentNames}
              />
            )}
            <Button
              variant="outline"
              onClick={() => router.push('/projects')}
              aria-label="Save and return to dashboard"
            >
              Save & Exit
            </Button>
          </div>
        </div>

        <WorkflowProgress currentStep={5} />
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Success Alert */}
      {!isLoading && !error && results.length > 0 && (
        <Alert className="bg-green-50 border-green-200 mb-6">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            <span className="font-medium">Processing complete!</span>
            {' '}- Successfully extracted {variables.length} variables from {results.length} documents.
          </AlertDescription>
        </Alert>
      )}

      {/* Results Section */}
      <Card>
        <CardHeader>
          <CardTitle>Extracted Data</CardTitle>
          <CardDescription>
            View, analyze, and export your extraction results
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground mb-4" />
              <p className="text-muted-foreground">Loading results...</p>
            </div>
          ) : error ? (
            <div className="text-center py-12 text-destructive">
              {error}
            </div>
          ) : results.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground text-lg mb-2">
                No results available yet
              </p>
              <p className="text-sm text-muted-foreground">
                Process some documents to see extraction results here
              </p>
              <Button
                className="mt-4"
                onClick={() => router.push(`/projects/${projectId}/processing`)}
              >
                Go to Processing
              </Button>
            </div>
          ) : (
            <ResultsDataTable results={results} variables={variables} />
          )}
        </CardContent>
      </Card>

      {/* Summary Stats */}
      {!isLoading && !error && results.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Documents Processed</CardDescription>
              <CardTitle className="text-2xl">{results.length}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Variables Extracted</CardDescription>
              <CardTitle className="text-2xl">{variables.length}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Total Data Points</CardDescription>
              <CardTitle className="text-2xl">{results.length * variables.length}</CardTitle>
            </CardHeader>
          </Card>
        </div>
      )}
    </div>
  );
}
