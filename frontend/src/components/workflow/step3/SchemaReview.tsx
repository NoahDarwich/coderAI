'use client';

import { useState } from 'react';
import { ArrowRight, Plus, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { SchemaTable } from './SchemaTable';
import { useSchemaWizardStore } from '@/store/schemaWizardStore';
import { useSaveSchema } from '@/lib/api/schema';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle2 } from 'lucide-react';
import type { SchemaVariable } from '@/lib/types/api';

interface SchemaReviewProps {
  projectId: string;
  onConfirm: () => void;
  onBackToWizard: () => void;
}

export function SchemaReview({ projectId, onConfirm, onBackToWizard }: SchemaReviewProps) {
  const { variables, deleteVariable, reorderVariables, clearDraft } = useSchemaWizardStore();
  const saveSchema = useSaveSchema(projectId);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [variableToDelete, setVariableToDelete] = useState<number | null>(null);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const handleEdit = () => {
    // Navigate back to wizard at the specific variable
    onBackToWizard();
  };

  const handleDeleteClick = (index: number) => {
    setVariableToDelete(index);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (variableToDelete !== null) {
      deleteVariable(variableToDelete);
      setDeleteDialogOpen(false);
      setVariableToDelete(null);
    }
  };

  const handleConfirmClick = () => {
    if (variables.length > 0) {
      setConfirmDialogOpen(true);
    }
  };

  const handleConfirmSchema = async () => {
    setIsSaving(true);

    try {
      // Transform variables to the format expected by the API
      const typeMap: Record<string, SchemaVariable['type']> = {
        'text': 'TEXT',
        'number': 'NUMBER',
        'date': 'DATE',
        'category': 'CATEGORY',
        'boolean': 'BOOLEAN',
      };

      const schemaVariables: SchemaVariable[] = variables.map((variable) => ({
        id: variable.id.startsWith('var-temp-') ? `var-${Math.random().toString(36).substring(2, 9)}` : variable.id,
        name: variable.name,
        type: typeMap[variable.type] || 'TEXT',
        instructions: variable.instructions,
        description: variable.instructions,
        prompt: variable.instructions,
        ...(variable.type === 'category' && variable.classificationRules ? {
          categories: variable.classificationRules,
        } : {}),
      }));

      // Save schema to backend
      await saveSchema.mutateAsync({
        conversationHistory: [],
        variables: schemaVariables,
        prompts: {},
      });

      // Clear the draft from local storage
      clearDraft();

      toast.success('Schema saved successfully!', {
        description: `${variables.length} variable${variables.length > 1 ? 's' : ''} saved to the backend.`,
      });

      setConfirmDialogOpen(false);
      setIsSaving(false);
      onConfirm();
    } catch (error) {
      console.error('Failed to save schema:', error);
      toast.error('Failed to save schema', {
        description: error instanceof Error ? error.message : 'An unknown error occurred',
      });
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Summary Alert */}
      {variables.length > 0 && (
        <Alert className="bg-blue-50 border-blue-200">
          <CheckCircle2 className="h-4 w-4 text-blue-600" />
          <AlertDescription className="text-blue-800">
            <span className="font-medium">Schema ready for review</span>
            {' '}- You have defined {variables.length} variable{variables.length > 1 ? 's' : ''}. Review them below and confirm to proceed.
          </AlertDescription>
        </Alert>
      )}

      {/* Schema Table */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle>Extraction Schema</CardTitle>
              <CardDescription>
                Review your variables, edit them, or reorder by dragging. Variables will be extracted in this order.
              </CardDescription>
            </div>
            <Button variant="outline" onClick={onBackToWizard}>
              <Plus className="w-4 h-4 mr-2" />
              Add Variable
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <SchemaTable
            variables={variables}
            onEdit={handleEdit}
            onDelete={handleDeleteClick}
            onReorder={reorderVariables}
          />
        </CardContent>
      </Card>

      {/* Table Preview */}
      <Card>
        <CardHeader>
          <CardTitle>Table Preview</CardTitle>
          <CardDescription>
            This is how your extracted data will be structured
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border rounded-lg overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Document
                  </th>
                  {variables.map((variable) => (
                    <th
                      key={variable.id}
                      className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {variable.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-4 py-3 text-sm text-gray-500 italic">
                    document_1.pdf
                  </td>
                  {variables.map((variable) => (
                    <td key={variable.id} className="px-4 py-3 text-sm text-gray-400 italic">
                      {variable.type === 'text' && 'extracted text...'}
                      {variable.type === 'number' && '123'}
                      {variable.type === 'date' && '2024-01-15'}
                      {variable.type === 'category' && variable.classificationRules?.[0] || 'category'}
                      {variable.type === 'boolean' && 'true'}
                    </td>
                  ))}
                </tr>
                <tr className="bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-500 italic">
                    document_2.pdf
                  </td>
                  {variables.map((variable) => (
                    <td key={variable.id} className="px-4 py-3 text-sm text-gray-400 italic">
                      ...
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Confirm Button */}
      <div className="flex justify-end">
        <Button
          size="lg"
          onClick={handleConfirmClick}
          disabled={variables.length === 0}
        >
          Confirm and Proceed to Processing
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Variable</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete &ldquo;{variableToDelete !== null ? variables[variableToDelete]?.name : ''}&rdquo;?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              className="bg-red-600 hover:bg-red-700"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Confirm Schema Dialog */}
      <AlertDialog open={confirmDialogOpen} onOpenChange={(open) => !isSaving && setConfirmDialogOpen(open)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirm Schema</AlertDialogTitle>
            <AlertDialogDescription>
              Are you ready to proceed with this schema? You have defined {variables.length} variable{variables.length > 1 ? 's' : ''}.
              The system will extract these variables from your documents in the order shown.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isSaving}>Review Again</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirmSchema} disabled={isSaving}>
              {isSaving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving Schema...
                </>
              ) : (
                'Confirm and Continue'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
