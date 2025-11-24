'use client';

import { useState, useMemo } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
  SortingState,
  ColumnDef,
} from '@tanstack/react-table';
import { ArrowUpDown, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { ExtractionResult, Variable } from '@/types';
import { getConfidenceEmoji, cn } from '@/lib/utils';
import { SourceTextModal } from './SourceTextModal';

interface ResultsTableProps {
  results: ExtractionResult[];
  variables: Variable[];
  documentNames: Record<string, string>;
}

interface FlattenedResult {
  documentId: string;
  documentName: string;
  [key: string]: any;
}

export function ResultsTable({ results, variables, documentNames }: ResultsTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState('');
  const [sourceTextModal, setSourceTextModal] = useState<{
    open: boolean;
    variableName: string;
    value: string | number | boolean | null;
    confidence: number;
    sourceText: string;
    documentName: string;
  }>({
    open: false,
    variableName: '',
    value: null,
    confidence: 0,
    sourceText: '',
    documentName: '',
  });

  // Flatten results for table display
  const flattenedData = useMemo(() => {
    return results.map((result) => {
      const row: FlattenedResult = {
        documentId: result.documentId,
        documentName: documentNames[result.documentId] || 'Unknown Document',
      };

      result.values.forEach((value) => {
        const variable = variables.find((v) => v.id === value.variableId);
        if (variable) {
          row[variable.name] = value.value;
          row[`${variable.name}_confidence`] = value.confidence;
          row[`${variable.name}_sourceText`] = value.sourceText;
        }
      });

      return row;
    });
  }, [results, variables, documentNames]);

  // Generate columns dynamically from variables
  const columns = useMemo<ColumnDef<FlattenedResult>[]>(() => {
    const cols: ColumnDef<FlattenedResult>[] = [
      {
        accessorKey: 'documentName',
        header: ({ column }) => (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            className="font-semibold"
          >
            Document
            <ArrowUpDown className="ml-2 h-3 w-3" />
          </Button>
        ),
        cell: ({ row }) => (
          <div className="font-medium text-sm">
            {row.getValue('documentName')}
          </div>
        ),
      },
    ];

    variables.forEach((variable) => {
      cols.push({
        accessorKey: variable.name,
        header: ({ column }) => (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            className="font-semibold"
          >
            {variable.name}
            <ArrowUpDown className="ml-2 h-3 w-3" />
          </Button>
        ),
        cell: ({ row }) => {
          const value = row.getValue(variable.name) as string | number | boolean | null;
          const confidence = row.original[`${variable.name}_confidence`] as number;
          const sourceText = row.original[`${variable.name}_sourceText`] as string;
          const documentName = row.getValue('documentName') as string;
          const emoji = getConfidenceEmoji(confidence);

          return (
            <div
              className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-2 rounded transition-colors"
              onClick={() => setSourceTextModal({
                open: true,
                variableName: variable.name,
                value,
                confidence,
                sourceText,
                documentName,
              })}
              title="Click to view source text"
            >
              <span className="text-sm">
                {value !== null && value !== undefined ? String(value) : '-'}
              </span>
              {confidence && (
                <Badge variant="outline" className="text-xs">
                  {emoji} {confidence}%
                </Badge>
              )}
            </div>
          );
        },
      });
    });

    return cols;
  }, [variables]);

  const table = useReactTable({
    data: flattenedData,
    columns,
    state: {
      sorting,
      globalFilter,
    },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search all fields..."
            value={globalFilter}
            onChange={(e) => setGlobalFilter(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="text-sm text-gray-600">
          {table.getFilteredRowModel().rows.length} of {flattenedData.length} results
        </div>
      </div>

      {/* Table */}
      <div className="border rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              {table.getHeaderGroups().map((headerGroup) => (
                <TableRow key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  ))}
                </TableRow>
              ))}
            </TableHeader>
            <TableBody>
              {table.getRowModel().rows.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={columns.length}
                    className="h-24 text-center text-gray-500"
                  >
                    No results found
                  </TableCell>
                </TableRow>
              ) : (
                table.getRowModel().rows.map((row) => (
                  <TableRow key={row.id}>
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id}>
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* Summary */}
      <div className="flex items-center justify-between text-sm text-gray-600">
        <div>
          Showing {table.getFilteredRowModel().rows.length} of {flattenedData.length} documents
        </div>
        <div>
          {variables.length} variables extracted
        </div>
      </div>

      {/* Source Text Modal */}
      <SourceTextModal
        open={sourceTextModal.open}
        onClose={() => setSourceTextModal({ ...sourceTextModal, open: false })}
        variableName={sourceTextModal.variableName}
        value={sourceTextModal.value}
        confidence={sourceTextModal.confidence}
        sourceText={sourceTextModal.sourceText}
        documentName={sourceTextModal.documentName}
      />
    </div>
  );
}
