/**
 * Results Page
 * View and manage extraction results with filtering and export
 */

'use client';

import { useParams, useRouter } from 'next/navigation';
import { useExtractionResults, useFlagResult, useBulkFlagResults } from '@/lib/api/extraction';
import { ExtractionPreview } from '@/components/results/ExtractionPreview';
import { Button } from '@/components/ui/button';
import { Table2, Download, ArrowRight } from 'lucide-react';
import { toast } from 'sonner';

export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  // Fetch results
  const { data: results = [], isLoading } = useExtractionResults(projectId);

  // Flag mutations
  const flagMutation = useFlagResult(projectId);
  const bulkFlagMutation = useBulkFlagResults(projectId);

  const handleFlagResult = async (resultId: string, flagged: boolean) => {
    try {
      await flagMutation.mutateAsync({ resultId, flagged });
      toast.success(flagged ? 'Result flagged for review' : 'Result unflagged');
    } catch (error) {
      toast.error('Failed to update flag status');
    }
  };

  const handleBulkFlag = async (resultIds: string[], flagged: boolean) => {
    try {
      await bulkFlagMutation.mutateAsync({ resultIds, flagged });
    } catch (error) {
      toast.error('Failed to update flag status');
    }
  };

  const hasResults = results.length > 0;

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Table2 className="h-6 w-6" />
            Extraction Results
          </h2>
          <p className="text-muted-foreground mt-1">
            Review extracted data, sort by confidence, and flag items for review
          </p>
        </div>

        {hasResults && (
          <Button
            onClick={() => router.push(`/projects/${projectId}/export`)}
          >
            Export Data
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Results summary */}
      {hasResults && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-lg border bg-card">
            <p className="text-sm text-muted-foreground">Total Results</p>
            <p className="text-2xl font-bold">{results.length}</p>
          </div>
          <div className="p-4 rounded-lg border bg-card">
            <p className="text-sm text-muted-foreground">Flagged for Review</p>
            <p className="text-2xl font-bold">
              {results.filter((r) => r.flagged).length}
            </p>
          </div>
          <div className="p-4 rounded-lg border bg-card">
            <p className="text-sm text-muted-foreground">Avg. Confidence</p>
            <p className="text-2xl font-bold">
              {Math.round(
                results.reduce((acc, r) => {
                  const confidences = Object.values(r.data).map(
                    (d) => d.confidence
                  );
                  const avg =
                    confidences.reduce((a, b) => a + b, 0) / confidences.length;
                  return acc + avg;
                }, 0) / results.length
              )}
              %
            </p>
          </div>
        </div>
      )}

      {/* Results table */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
            <p className="text-muted-foreground">Loading results...</p>
          </div>
        </div>
      ) : hasResults ? (
        <ExtractionPreview
          results={results}
          onFlagResult={handleFlagResult}
          onBulkFlag={handleBulkFlag}
        />
      ) : (
        <div className="text-center py-12 border-2 border-dashed rounded-lg">
          <Table2 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No results yet</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Process your documents to see extraction results here
          </p>
          <Button
            onClick={() => router.push(`/projects/${projectId}/process`)}
          >
            Start Processing
          </Button>
        </div>
      )}

      {/* Next step CTA */}
      {hasResults && (
        <div className="flex justify-end pt-4 border-t">
          <Button
            size="lg"
            onClick={() => router.push(`/projects/${projectId}/export`)}
          >
            <Download className="mr-2 h-4 w-4" />
            Export Results
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
