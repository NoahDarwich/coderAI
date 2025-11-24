'use client';

import { useState } from 'react';
import { Download, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { ExtractionResult, Variable, ExportConfig } from '@/types';
import { downloadBlob } from '@/lib/utils';

interface ExportModalProps {
  results: ExtractionResult[];
  variables: Variable[];
  documentNames: Record<string, string>;
}

export function ExportModal({ results, variables, documentNames }: ExportModalProps) {
  const [open, setOpen] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [config, setConfig] = useState<ExportConfig>({
    format: 'csv',
    structure: 'wide',
    includeConfidence: true,
    includeSourceText: false,
  });

  const generateCSV = () => {
    if (config.structure === 'wide') {
      // Wide format: one row per document
      const headers = ['Document', ...variables.map((v) => v.name)];
      if (config.includeConfidence) {
        variables.forEach((v) => headers.push(`${v.name} (Confidence)`));
      }

      const rows = results.map((result) => {
        const row: string[] = [documentNames[result.documentId] || 'Unknown'];

        // Add values
        variables.forEach((variable) => {
          const value = result.values.find((v) => v.variableId === variable.id);
          row.push(value?.value !== null && value?.value !== undefined ? String(value.value) : '');
        });

        // Add confidence scores
        if (config.includeConfidence) {
          variables.forEach((variable) => {
            const value = result.values.find((v) => v.variableId === variable.id);
            row.push(value?.confidence !== undefined ? String(value.confidence) : '');
          });
        }

        return row;
      });

      const csvContent = [headers, ...rows]
        .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(','))
        .join('\n');

      return csvContent;
    } else {
      // Long format: one row per extracted value
      const headers = ['Document', 'Variable', 'Value'];
      if (config.includeConfidence) {
        headers.push('Confidence');
      }
      if (config.includeSourceText) {
        headers.push('Source Text');
      }

      const rows: string[][] = [];

      results.forEach((result) => {
        const docName = documentNames[result.documentId] || 'Unknown';

        result.values.forEach((value) => {
          const variable = variables.find((v) => v.id === value.variableId);
          if (!variable) return;

          const row = [
            docName,
            variable.name,
            value.value !== null && value.value !== undefined ? String(value.value) : '',
          ];

          if (config.includeConfidence) {
            row.push(String(value.confidence || ''));
          }

          if (config.includeSourceText) {
            row.push(value.sourceText || '');
          }

          rows.push(row);
        });
      });

      const csvContent = [headers, ...rows]
        .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(','))
        .join('\n');

      return csvContent;
    }
  };

  const handleExport = async () => {
    setIsExporting(true);
    try {
      // Simulate processing time
      await new Promise((resolve) => setTimeout(resolve, 1000));

      const csvContent = generateCSV();
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const fileName = `extraction_results_${new Date().toISOString().split('T')[0]}.csv`;

      downloadBlob(blob, fileName);
      setOpen(false);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Download className="w-4 h-4 mr-2" />
          Export Data
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Export Results</DialogTitle>
          <DialogDescription>
            Configure export settings and download your extracted data
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Format Selection */}
          <div className="space-y-3">
            <Label>Export Format</Label>
            <RadioGroup
              value={config.format}
              onValueChange={(value) => setConfig({ ...config, format: value as 'csv' })}
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="csv" id="csv" />
                <Label htmlFor="csv" className="font-normal cursor-pointer">
                  CSV (Comma-Separated Values)
                </Label>
              </div>
            </RadioGroup>
            <p className="text-xs text-gray-500">
              Excel, Google Sheets, and most data tools support CSV
            </p>
          </div>

          {/* Structure Selection */}
          <div className="space-y-3">
            <Label>Data Structure</Label>
            <RadioGroup
              value={config.structure}
              onValueChange={(value) =>
                setConfig({ ...config, structure: value as 'wide' | 'long' })
              }
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="wide" id="wide" />
                <Label htmlFor="wide" className="font-normal cursor-pointer">
                  Wide (one row per document)
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="long" id="long" />
                <Label htmlFor="long" className="font-normal cursor-pointer">
                  Long (one row per value)
                </Label>
              </div>
            </RadioGroup>
          </div>

          {/* Options */}
          <div className="space-y-3">
            <Label>Include Additional Data</Label>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="confidence"
                  checked={config.includeConfidence}
                  onCheckedChange={(checked) =>
                    setConfig({ ...config, includeConfidence: checked as boolean })
                  }
                />
                <Label htmlFor="confidence" className="font-normal cursor-pointer">
                  Confidence scores
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="sourceText"
                  checked={config.includeSourceText}
                  onCheckedChange={(checked) =>
                    setConfig({ ...config, includeSourceText: checked as boolean })
                  }
                />
                <Label htmlFor="sourceText" className="font-normal cursor-pointer">
                  Source text excerpts
                </Label>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleExport} disabled={isExporting}>
            {isExporting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Exporting...
              </>
            ) : (
              <>
                <Download className="w-4 h-4 mr-2" />
                Export
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
