/**
 * ExtractionPreview Component
 * Main component for viewing and managing extraction results
 */

'use client';

import { useState, useMemo } from 'react';
import { type ColumnDef } from '@tanstack/react-table';
import { ExtractionResult } from '@/lib/types/api';
import { DataTable, SortableHeader } from './DataTable';
import { ConfidenceIndicator } from './ConfidenceIndicator';
import { FlagButton } from './FlagButton';
import { ResultDetailModal } from './ResultDetailModal';
import { FilterControls, type FilterState } from './FilterControls';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Flag, FlagOff } from 'lucide-react';
import { toast } from 'sonner';

interface ExtractionPreviewProps {
  results: ExtractionResult[];
  onFlagResult: (resultId: string, flagged: boolean) => void;
  onBulkFlag?: (resultIds: string[], flagged: boolean) => void;
  isLoading?: boolean;
}

export function ExtractionPreview({
  results,
  onFlagResult,
  onBulkFlag,
  isLoading,
}: ExtractionPreviewProps) {
  const [selectedResult, setSelectedResult] = useState<ExtractionResult | null>(null);
  const [selectedRows, setSelectedRows] = useState<ExtractionResult[]>([]);
  const [filters, setFilters] = useState<FilterState>({
    search: '',
    minConfidence: 0,
    flaggedOnly: false,
    sortBy: 'document',
    sortOrder: 'asc',
  });

  // Calculate average confidence for each result
  const calculateAvgConfidence = (result: ExtractionResult): number => {
    const confidences = Object.values(result.data).map((d) => d.confidence);
    return Math.round(
      confidences.reduce((a, b) => a + b, 0) / confidences.length
    );
  };

  // Filter results
  const filteredResults = useMemo(() => {
    return results.filter((result) => {
      // Search filter
      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        const matchesDocument = result.documentName
          .toLowerCase()
          .includes(searchLower);
        const matchesData = Object.values(result.data).some((d) =>
          String(d.value).toLowerCase().includes(searchLower)
        );
        if (!matchesDocument && !matchesData) return false;
      }

      // Confidence filter
      const avgConfidence = calculateAvgConfidence(result);
      if (avgConfidence < filters.minConfidence) return false;

      // Flagged filter
      if (filters.flaggedOnly && !result.flagged) return false;

      return true;
    });
  }, [results, filters]);

  // Define columns
  const columns: ColumnDef<ExtractionResult>[] = [
    {
      accessorKey: 'documentName',
      header: ({ column }) => (
        <SortableHeader column={column}>Document</SortableHeader>
      ),
      cell: ({ row }) => (
        <div className="max-w-[200px]">
          <p className="font-medium truncate">{row.original.documentName}</p>
        </div>
      ),
    },
    {
      id: 'avgConfidence',
      header: ({ column }) => (
        <SortableHeader column={column}>Confidence</SortableHeader>
      ),
      accessorFn: (row) => calculateAvgConfidence(row),
      cell: ({ row }) => {
        const avgConfidence = calculateAvgConfidence(row.original);
        return (
          <ConfidenceIndicator confidence={avgConfidence} showLabel />
        );
      },
    },
    {
      id: 'variableCount',
      header: 'Variables',
      accessorFn: (row) => Object.keys(row.data).length,
      cell: ({ row }) => (
        <Badge variant="secondary">
          {Object.keys(row.original.data).length}
        </Badge>
      ),
    },
    {
      accessorKey: 'flagged',
      header: 'Flagged',
      cell: ({ row }) => (
        <FlagButton
          flagged={row.original.flagged}
          onToggle={() =>
            onFlagResult(row.original.id, !row.original.flagged)
          }
        />
      ),
    },
  ];

  const handleResetFilters = () => {
    setFilters({
      search: '',
      minConfidence: 0,
      flaggedOnly: false,
      sortBy: 'document',
      sortOrder: 'asc',
    });
  };

  const handleBulkFlag = (flagged: boolean) => {
    if (!onBulkFlag || selectedRows.length === 0) return;

    const ids = selectedRows.map((r) => r.id);
    onBulkFlag(ids, flagged);
    toast.success(
      `${ids.length} result${ids.length !== 1 ? 's' : ''} ${
        flagged ? 'flagged' : 'unflagged'
      }`
    );
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <FilterControls
        filters={filters}
        onFiltersChange={(newFilters) =>
          setFilters((prev) => ({ ...prev, ...newFilters }))
        }
        onReset={handleResetFilters}
      />

      {/* Bulk actions */}
      {selectedRows.length > 0 && onBulkFlag && (
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleBulkFlag(true)}
          >
            <Flag className="h-4 w-4 mr-2" />
            Flag Selected ({selectedRows.length})
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleBulkFlag(false)}
          >
            <FlagOff className="h-4 w-4 mr-2" />
            Unflag Selected ({selectedRows.length})
          </Button>
        </div>
      )}

      {/* Data table */}
      <DataTable
        columns={columns}
        data={filteredResults}
        onRowClick={(row) => setSelectedResult(row)}
        onSelectionChange={setSelectedRows}
        enableSelection={!!onBulkFlag}
      />

      {/* Detail modal */}
      <ResultDetailModal
        result={selectedResult}
        open={selectedResult !== null}
        onClose={() => setSelectedResult(null)}
        onToggleFlag={onFlagResult}
      />
    </div>
  );
}
