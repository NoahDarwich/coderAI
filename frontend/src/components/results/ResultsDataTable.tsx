/**
 * Results Data Table Component
 * Displays extraction results in a table format with confidence scores
 */

'use client';

import { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Download, Info } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface ExtractionDataPoint {
  value: string | null;
  confidence: number; // 0-100
  source_text?: string | null;
}

interface DocumentResult {
  document_id: string;
  document_name: string;
  data: Record<string, ExtractionDataPoint>;
  average_confidence: number;
  flagged: boolean;
  extracted_at?: string;
}

interface ResultsDataTableProps {
  results: DocumentResult[];
  variables: string[]; // Variable names in order
}

export function ResultsDataTable({ results, variables }: ResultsDataTableProps) {
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
    if (confidence >= 60) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
    return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
  };

  const exportToCSV = () => {
    // Create CSV header
    const headers = ['Document', ...variables, 'Avg Confidence'];
    const csvRows = [headers.join(',')];

    // Add data rows
    for (const result of results) {
      const row = [
        `"${result.document_name}"`,
        ...variables.map((varName) => {
          const dataPoint = result.data[varName];
          const value = dataPoint?.value || '';
          // Escape quotes in values
          return `"${String(value).replace(/"/g, '""')}"`;
        }),
        result.average_confidence.toString(),
      ];
      csvRows.push(row.join(','));
    }

    // Download
    const csvContent = csvRows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `extraction-results-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (results.length === 0) {
    return (
      <div className="text-center py-12 border rounded-lg bg-muted/50">
        <p className="text-muted-foreground text-lg mb-2">No results yet</p>
        <p className="text-sm text-muted-foreground">
          Process some documents to see extractions here
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold">
            Extraction Results ({results.length} document{results.length !== 1 ? 's' : ''})
          </h3>
          <p className="text-sm text-muted-foreground">
            Extracted data with AI confidence scores
          </p>
        </div>
        <Button onClick={exportToCSV} variant="outline" size="sm">
          <Download className="mr-2 h-4 w-4" />
          Export CSV
        </Button>
      </div>

      <div className="border rounded-lg overflow-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[200px] sticky left-0 bg-background">
                Document
              </TableHead>
              {variables.map((varName) => (
                <TableHead key={varName} className="min-w-[150px]">
                  {varName}
                </TableHead>
              ))}
              <TableHead className="text-right min-w-[120px]">
                Avg Confidence
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {results.map((result) => (
              <TableRow key={result.document_id}>
                <TableCell className="font-medium sticky left-0 bg-background">
                  {result.document_name}
                </TableCell>
                {variables.map((varName) => {
                  const dataPoint = result.data[varName];
                  return (
                    <TableCell key={`${result.document_id}-${varName}`}>
                      {dataPoint ? (
                        <div className="space-y-1">
                          <div className="text-sm">
                            {dataPoint.value || (
                              <span className="text-muted-foreground italic">
                                Not found
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge
                              variant="secondary"
                              className={`${getConfidenceColor(dataPoint.confidence)} text-xs`}
                            >
                              {dataPoint.confidence}%
                            </Badge>
                            {dataPoint.source_text && (
                              <TooltipProvider>
                                <Tooltip>
                                  <TooltipTrigger asChild>
                                    <Info className="h-3 w-3 text-muted-foreground cursor-help" />
                                  </TooltipTrigger>
                                  <TooltipContent className="max-w-xs">
                                    <p className="text-xs">
                                      <strong>Source:</strong> {dataPoint.source_text}
                                    </p>
                                  </TooltipContent>
                                </Tooltip>
                              </TooltipProvider>
                            )}
                          </div>
                        </div>
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </TableCell>
                  );
                })}
                <TableCell className="text-right">
                  <Badge className={getConfidenceColor(result.average_confidence)}>
                    {result.average_confidence}%
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center gap-4 text-sm text-muted-foreground">
        <div className="flex items-center gap-2">
          <Badge className={getConfidenceColor(90)}>High</Badge>
          <span>80-100%</span>
        </div>
        <div className="flex items-center gap-2">
          <Badge className={getConfidenceColor(70)}>Medium</Badge>
          <span>60-79%</span>
        </div>
        <div className="flex items-center gap-2">
          <Badge className={getConfidenceColor(40)}>Low</Badge>
          <span>0-59%</span>
        </div>
      </div>
    </div>
  );
}
