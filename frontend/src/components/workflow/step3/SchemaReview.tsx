'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, Plus } from 'lucide-react';
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
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle2 } from 'lucide-react';

interface SchemaReviewProps {
  projectId: string;
  onConfirm: () => void;
  onBackToWizard: () => void;
}

export function SchemaReview({ projectId, onConfirm, onBackToWizard }: SchemaReviewProps) {
  const { variables, deleteVariable, reorderVariables } = useSchemaWizardStore();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [variableToDelete, setVariableToDelete] = useState<number | null>(null);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);

  const handleEdit = (index: number) => {
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

  const handleConfirmSchema = () => {
    setConfirmDialogOpen(false);
    onConfirm();
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
              Are you sure you want to delete "{variableToDelete !== null ? variables[variableToDelete]?.name : ''}"?
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
      <AlertDialog open={confirmDialogOpen} onOpenChange={setConfirmDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirm Schema</AlertDialogTitle>
            <AlertDialogDescription>
              Are you ready to proceed with this schema? You have defined {variables.length} variable{variables.length > 1 ? 's' : ''}.
              The system will extract these variables from your documents in the order shown.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Review Again</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirmSchema}>
              Confirm and Continue
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
