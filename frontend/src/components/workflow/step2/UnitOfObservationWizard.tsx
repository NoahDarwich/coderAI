'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, Loader2, Sparkles, Info } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api/client';
import { useProject, useUpdateProject } from '@/lib/api/projects';
import {
  transformUnitOfObservation,
  type UnitOfObservation,
} from '@/lib/api/transforms';

interface UnitOfObservationWizardProps {
  projectId: string;
}

type RowsPerDocument = 'one' | 'multiple';

const ROWS_OPTIONS: { value: RowsPerDocument; label: string; description: string }[] = [
  {
    value: 'one',
    label: 'One row per document',
    description: 'Each document produces a single row. Most common — e.g., one article = one data point.',
  },
  {
    value: 'multiple',
    label: 'Multiple rows per document',
    description: 'Each document may produce several rows — e.g., one invoice with many line items.',
  },
];

const EXAMPLES: Record<RowsPerDocument, string[]> = {
  one: ['Each document', 'Each article', 'Each contract', 'Each report', 'Each email'],
  multiple: [
    'Each invoice line item',
    'Each person mentioned',
    'Each transaction',
    'Each paragraph',
    'Each event described',
  ],
};

interface WizardSuggestion {
  suggestion: {
    rows_per_document: 'single' | 'multiple';
    entity_identification_pattern?: string;
    label: string;
  };
  explanation: string;
}

// Map wizard "single" → project "one" (vocabulary mismatch between endpoints)
function mapSuggestionRows(raw: 'single' | 'multiple'): RowsPerDocument {
  return raw === 'single' ? 'one' : 'multiple';
}

export function UnitOfObservationWizard({ projectId }: UnitOfObservationWizardProps) {
  const router = useRouter();
  const { data: project } = useProject(projectId);
  const updateProject = useUpdateProject();

  // Form state
  const [whatEachRowRepresents, setWhatEachRowRepresents] = useState('');
  const [rowsPerDocument, setRowsPerDocument] = useState<RowsPerDocument>('one');
  const [entityPattern, setEntityPattern] = useState('');

  // AI suggestion state
  const [suggestion, setSuggestion] = useState<WizardSuggestion | null>(null);
  const [isSuggesting, setIsSuggesting] = useState(false);

  const [isSaving, setIsSaving] = useState(false);

  // Refs to prevent duplicate runs across re-renders / refetches
  const hasPrefilled = useRef(false);
  const hasFiredSuggestion = useRef(false);

  // Pre-fill from existing project data — only once on first load
  useEffect(() => {
    if (!project || hasPrefilled.current) return;
    const existing = transformUnitOfObservation(
      project.unitOfObservation as Record<string, unknown> | undefined,
    );
    if (existing) {
      hasPrefilled.current = true;
      setWhatEachRowRepresents(existing.whatEachRowRepresents);
      setRowsPerDocument(existing.rowsPerDocument);
      setEntityPattern(existing.entityIdentificationPattern ?? '');
    }
  }, [project]);

  // Auto-fire AI suggestion once on load
  useEffect(() => {
    if (!project || hasFiredSuggestion.current) return;
    hasFiredSuggestion.current = true;
    fetchSuggestion((project.domain ?? project.description ?? '').trim());
  }, [project]);

  async function fetchSuggestion(context: string) {
    if (!context) return;
    setIsSuggesting(true);
    try {
      const result = await apiClient.post<WizardSuggestion>(
        '/api/v1/wizard/suggest-unit-of-observation',
        { domain: context },
      );
      setSuggestion(result);
    } catch {
      // Suggestion is best-effort — silently skip on error
    } finally {
      setIsSuggesting(false);
    }
  }

  function applySuggestion() {
    if (!suggestion) return;
    const rows = mapSuggestionRows(suggestion.suggestion.rows_per_document);
    setRowsPerDocument(rows);
    setWhatEachRowRepresents(suggestion.suggestion.label);
    if (suggestion.suggestion.entity_identification_pattern) {
      setEntityPattern(suggestion.suggestion.entity_identification_pattern);
    }
    toast.info('AI suggestion applied', {
      description: suggestion.suggestion.label,
    });
  }

  const isValid =
    whatEachRowRepresents.trim().length > 0 &&
    (rowsPerDocument === 'one' || entityPattern.trim().length > 0);

  async function save(): Promise<void> {
    const uoo: UnitOfObservation = {
      whatEachRowRepresents: whatEachRowRepresents.trim(),
      rowsPerDocument,
      entityIdentificationPattern:
        rowsPerDocument === 'multiple' ? entityPattern.trim() : undefined,
    };
    await updateProject.mutateAsync({
      id: projectId,
      data: { unitOfObservation: uoo },
    });
  }

  async function handleContinue() {
    if (!isValid) return;
    setIsSaving(true);
    try {
      await save();
      router.push(`/projects/${projectId}/schema`);
    } catch (error) {
      toast.error('Failed to save', {
        description: error instanceof Error ? error.message : 'Unknown error',
      });
    } finally {
      setIsSaving(false);
    }
  }

  async function handleSaveAndExit() {
    setIsSaving(true);
    try {
      if (isValid) {
        await save();
      }
    } catch {
      // best-effort on exit
    } finally {
      setIsSaving(false);
      router.push('/projects');
    }
  }

  const examples = EXAMPLES[rowsPerDocument];

  return (
    <div className="space-y-6">
      {/* AI Suggestion Banner */}
      {(isSuggesting || suggestion) && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="pt-4">
            {isSuggesting ? (
              <div className="flex items-center gap-2 text-blue-700">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm">AI is analysing your project…</span>
              </div>
            ) : suggestion ? (
              <div className="space-y-2">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-2">
                    <Sparkles className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-sm font-medium text-blue-900">AI Suggestion</p>
                      <p className="text-sm text-blue-700 mt-0.5">{suggestion.explanation}</p>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    className="border-blue-300 text-blue-700 hover:bg-blue-100 flex-shrink-0"
                    onClick={applySuggestion}
                  >
                    Apply
                  </Button>
                </div>
                <div className="flex items-center gap-2 ml-6">
                  <Badge variant="outline" className="text-blue-700 border-blue-300 text-xs">
                    {suggestion.suggestion.label}
                  </Badge>
                </div>
              </div>
            ) : null}
          </CardContent>
        </Card>
      )}

      {/* Question 1 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">
            What does each row in your dataset represent?
          </CardTitle>
          <CardDescription>
            Describe the unit you are collecting — one per row in your final export.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="what-each-row">
              Each row represents… <span className="text-destructive">*</span>
            </Label>
            <Input
              id="what-each-row"
              placeholder='e.g., "Each document", "Each invoice line item", "Each person mentioned"'
              value={whatEachRowRepresents}
              onChange={(e) => setWhatEachRowRepresents(e.target.value)}
            />
          </div>

          {/* Examples */}
          <div className="flex flex-wrap gap-1.5">
            <span className="text-xs text-muted-foreground self-center">Examples:</span>
            {examples.map((ex) => (
              <Badge
                key={ex}
                variant="outline"
                className="text-xs cursor-pointer hover:bg-muted"
                onClick={() => setWhatEachRowRepresents(ex)}
              >
                {ex}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Question 2 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">
            How many rows do you expect per document?
          </CardTitle>
          <CardDescription>
            This determines whether the AI extracts once per document or identifies multiple entities first.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <RadioGroup
            value={rowsPerDocument}
            onValueChange={(v) => setRowsPerDocument(v as RowsPerDocument)}
            className="space-y-3"
          >
            {ROWS_OPTIONS.map((opt) => (
              <div
                key={opt.value}
                className={`flex items-start space-x-3 rounded-lg border p-4 cursor-pointer transition-colors ${
                  rowsPerDocument === opt.value
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-border hover:border-muted-foreground'
                }`}
                onClick={() => setRowsPerDocument(opt.value)}
              >
                <RadioGroupItem value={opt.value} id={opt.value} className="mt-0.5" />
                <div className="space-y-1">
                  <Label htmlFor={opt.value} className="cursor-pointer font-medium">
                    {opt.label}
                  </Label>
                  <p className="text-sm text-muted-foreground">{opt.description}</p>
                </div>
              </div>
            ))}
          </RadioGroup>
        </CardContent>
      </Card>

      {/* Question 3 — conditional */}
      {rowsPerDocument === 'multiple' && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">
              How should the system identify each entity?{' '}
              <span className="text-destructive">*</span>
            </CardTitle>
            <CardDescription>
              Describe how to find and separate individual records within a document.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="entity-pattern">Identification pattern</Label>
              <Textarea
                id="entity-pattern"
                placeholder={
                  'e.g., "Each numbered row in a table"\n' +
                  '"Each paragraph starting with a person\'s name"\n' +
                  '"Each section beginning with a date"'
                }
                rows={3}
                value={entityPattern}
                onChange={(e) => setEntityPattern(e.target.value)}
              />
            </div>
            <Alert className="bg-amber-50 border-amber-200">
              <Info className="h-4 w-4 text-amber-600" />
              <AlertDescription className="text-amber-800 text-sm">
                The AI will first scan each document to identify all matching entities, then extract
                your variables for each one separately.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}

      {/* Action buttons */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={handleSaveAndExit}
          disabled={isSaving}
        >
          Save & Exit
        </Button>
        <Button
          size="lg"
          onClick={handleContinue}
          disabled={!isValid || isSaving}
        >
          {isSaving ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Saving…
            </>
          ) : (
            <>
              Continue to Schema Definition
              <ArrowRight className="ml-2 h-4 w-4" />
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
