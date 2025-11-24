/**
 * Results Page - Step 5: View and export extraction results
 */

'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ResultsTable } from '@/components/workflow/step5/ResultsTable';
import { ExportModal } from '@/components/workflow/step5/ExportModal';
import { ConfidenceFilter } from '@/components/workflow/step5/ConfidenceFilter';
import { WorkflowProgress } from '@/components/layout/WorkflowProgress';
import { useSchemaWizardStore } from '@/store/schemaWizardStore';
import { ExtractionResult } from '@/types';
import { generateId } from '@/lib/utils';
import { mockDocuments } from '@/mocks/mockDocuments';

export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const { variables } = useSchemaWizardStore();

  const [mounted, setMounted] = useState(false);
  const [results, setResults] = useState<ExtractionResult[]>([]);
  const [filteredResults, setFilteredResults] = useState<ExtractionResult[]>([]);
  const [documentNames, setDocumentNames] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Filter results by confidence threshold
  useEffect(() => {
    if (results.length === 0) {
      setFilteredResults([]);
      return;
    }

    const filtered = results.filter((result) => {
      // Check if all values meet the threshold
      return result.values.every((value) => value.confidence >= confidenceThreshold);
    });

    setFilteredResults(filtered);
  }, [results, confidenceThreshold]);

  // Load results
  useEffect(() => {
    if (!mounted) return;

    const loadResults = async () => {
      setIsLoading(true);
      try {
        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 1000));

        // Get documents for this project
        const projectDocs = mockDocuments.filter((doc) => doc.projectId === projectId);

        // Generate mock results
        const mockResults: ExtractionResult[] = projectDocs.map((doc) => ({
          id: generateId(),
          projectId,
          documentId: doc.id,
          values: variables.map((variable) => {
            // Generate mock extracted values
            let value: string | number | boolean | null = null;
            let confidence = Math.floor(Math.random() * 30) + 70; // 70-100

            if (variable.type === 'text') {
              value = `Sample ${variable.name.toLowerCase()} from ${doc.fileName}`;
            } else if (variable.type === 'number') {
              value = Math.floor(Math.random() * 1000) + 1;
            } else if (variable.type === 'date') {
              value = '2024-01-15';
            } else if (variable.type === 'category' && variable.classificationRules) {
              value = variable.classificationRules[Math.floor(Math.random() * variable.classificationRules.length)];
            } else if (variable.type === 'boolean') {
              value = Math.random() > 0.5;
            }

            return {
              variableId: variable.id,
              value,
              confidence,
              sourceText: `This is a sample text excerpt from ${doc.fileName} that was used to extract ${variable.name}...`,
            };
          }),
          completedAt: new Date().toISOString(),
        }));

        setResults(mockResults);

        // Create document name mapping
        const names: Record<string, string> = {};
        projectDocs.forEach((doc) => {
          names[doc.id] = doc.fileName;
        });
        setDocumentNames(names);
      } finally {
        setIsLoading(false);
      }
    };

    loadResults();
  }, [projectId, variables, mounted]);

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
          {!isLoading && results.length > 0 && (
            <ExportModal
              results={results}
              variables={variables}
              documentNames={documentNames}
            />
          )}
        </div>

        <WorkflowProgress currentStep={5} />
      </div>

      {/* Success Alert */}
      {!isLoading && results.length > 0 && (
        <Alert className="bg-green-50 border-green-200 mb-6">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            <span className="font-medium">Processing complete!</span>
            {' '}- Successfully extracted {variables.length} variables from {results.length} documents.
          </AlertDescription>
        </Alert>
      )}

      {/* Filters and Results */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
        {/* Confidence Filter Sidebar */}
        {!isLoading && results.length > 0 && (
          <div className="lg:col-span-1">
            <ConfidenceFilter
              value={confidenceThreshold}
              onChange={setConfidenceThreshold}
            />
          </div>
        )}

        {/* Results Table */}
        <div className={!isLoading && results.length > 0 ? "lg:col-span-3" : "lg:col-span-4"}>
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Extracted Data</CardTitle>
                  <CardDescription>
                    Search, sort, and review your extraction results
                  </CardDescription>
                </div>
                {!isLoading && filteredResults.length < results.length && (
                  <div className="text-sm text-gray-600">
                    Showing {filteredResults.length} of {results.length} results
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-pulse space-y-4 w-full">
                    <div className="h-10 bg-gray-200 rounded" />
                    <div className="h-64 bg-gray-200 rounded" />
                  </div>
                </div>
              ) : results.length === 0 ? (
                <div className="text-center py-12 text-gray-600">
                  No results available. Please process documents first.
                </div>
              ) : filteredResults.length === 0 ? (
                <div className="text-center py-12 text-gray-600">
                  No results match the current confidence threshold. Try lowering the filter.
                </div>
              ) : (
                <ResultsTable
                  results={filteredResults}
                  variables={variables}
                  documentNames={documentNames}
                />
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Summary Stats */}
      {!isLoading && results.length > 0 && (
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
