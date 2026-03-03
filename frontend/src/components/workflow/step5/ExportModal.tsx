'use client';

import { useState } from 'react';
import { Download, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
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
import { apiClient } from '@/lib/api/client';

type ExportFormat = 'CSV_WIDE' | 'CSV_LONG' | 'EXCEL' | 'JSON';

interface ExportModalProps {
  projectId: string;
  projectName?: string;
}

export function ExportModal({ projectId, projectName }: ExportModalProps) {
  const [open, setOpen] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [format, setFormat] = useState<ExportFormat>('CSV_WIDE');
  const [includeConfidence, setIncludeConfidence] = useState(true);
  const [includeSourceText, setIncludeSourceText] = useState(false);

  const FORMAT_LABELS: Record<ExportFormat, { label: string; description: string }> = {
    CSV_WIDE: { label: 'CSV — Wide', description: 'One row per document, one column per variable' },
    CSV_LONG: { label: 'CSV — Long', description: 'One row per extracted value' },
    EXCEL: { label: 'Excel (.xlsx)', description: 'Formatted spreadsheet with codebook sheet' },
    JSON: { label: 'JSON', description: 'Machine-readable structured format' },
  };

  const handleExport = async () => {
    setIsExporting(true);
    try {
      // Step 1: create export on backend
      const response = await apiClient.post<{
        download_url: string;
        filename: string;
        size_bytes: number;
      }>(`/api/v1/projects/${projectId}/export`, {
        format,
        include_confidence: includeConfidence,
        include_source_text: includeSourceText,
      });

      // Step 2: download the generated file
      await apiClient.download(response.download_url, response.filename);

      toast.success('Export ready', {
        description: `${response.filename} downloaded (${Math.round(response.size_bytes / 1024)} KB)`,
      });
      setOpen(false);
    } catch (error) {
      console.error('Export failed:', error);
      toast.error('Export failed', {
        description: error instanceof Error ? error.message : 'Please try again.',
      });
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
            {projectName ? `Export extraction results for "${projectName}"` : 'Configure and download your extracted data'}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Format Selection */}
          <div className="space-y-3">
            <Label>Export Format</Label>
            <RadioGroup
              value={format}
              onValueChange={(v) => setFormat(v as ExportFormat)}
              className="space-y-2"
            >
              {(Object.keys(FORMAT_LABELS) as ExportFormat[]).map((f) => (
                <div key={f} className="flex items-start space-x-2">
                  <RadioGroupItem value={f} id={f} className="mt-0.5" />
                  <Label htmlFor={f} className="font-normal cursor-pointer space-y-0.5">
                    <span className="font-medium">{FORMAT_LABELS[f].label}</span>
                    <p className="text-xs text-muted-foreground">{FORMAT_LABELS[f].description}</p>
                  </Label>
                </div>
              ))}
            </RadioGroup>
          </div>

          {/* Options */}
          <div className="space-y-3">
            <Label>Include Additional Columns</Label>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="confidence"
                  checked={includeConfidence}
                  onCheckedChange={(checked) => setIncludeConfidence(checked as boolean)}
                />
                <Label htmlFor="confidence" className="font-normal cursor-pointer">
                  Confidence scores
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="sourceText"
                  checked={includeSourceText}
                  onCheckedChange={(checked) => setIncludeSourceText(checked as boolean)}
                />
                <Label htmlFor="sourceText" className="font-normal cursor-pointer">
                  Source text excerpts
                </Label>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)} disabled={isExporting}>
            Cancel
          </Button>
          <Button onClick={handleExport} disabled={isExporting}>
            {isExporting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Generating…
              </>
            ) : (
              <>
                <Download className="w-4 h-4 mr-2" />
                Download
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
