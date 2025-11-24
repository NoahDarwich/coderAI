'use client';

import { useEffect, useState } from 'react';
import { VariableForm } from './VariableForm';
import { WizardNavigation } from './WizardNavigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle2, ListTree } from 'lucide-react';
import { Variable } from '@/types';
import { VariableFormData } from '@/lib/validations';
import { useSchemaWizardStore } from '@/store/schemaWizardStore';

interface SchemaWizardProps {
  projectId: string;
  onComplete: () => void;
}

export function SchemaWizard({ projectId, onComplete }: SchemaWizardProps) {
  const {
    variables,
    currentVariableIndex,
    addVariable,
    updateVariable,
    setCurrentIndex,
    setProjectId,
    loadDraft,
  } = useSchemaWizardStore();

  const [isAddingNew, setIsAddingNew] = useState(variables.length === 0);

  useEffect(() => {
    // Load draft for this project
    loadDraft(projectId);
    setProjectId(projectId);
  }, [projectId, loadDraft, setProjectId]);

  const handleAddVariable = (data: VariableFormData) => {
    addVariable({
      name: data.name,
      type: data.type,
      instructions: data.instructions,
      classificationRules: data.classificationRules,
    });
    setIsAddingNew(false);
  };

  const handleUpdateVariable = (data: VariableFormData) => {
    updateVariable(currentVariableIndex, {
      name: data.name,
      type: data.type,
      instructions: data.instructions,
      classificationRules: data.classificationRules,
    });
  };

  const handlePrevious = () => {
    if (currentVariableIndex > 0) {
      setCurrentIndex(currentVariableIndex - 1);
      setIsAddingNew(false);
    }
  };

  const handleNext = () => {
    if (currentVariableIndex < variables.length - 1) {
      setCurrentIndex(currentVariableIndex + 1);
      setIsAddingNew(false);
    }
  };

  const handleAddAnother = () => {
    setIsAddingNew(true);
  };

  const handleFinish = () => {
    if (variables.length > 0) {
      onComplete();
    }
  };

  const currentVariable = !isAddingNew && variables[currentVariableIndex];
  const canGoNext = variables.length > 0 && currentVariableIndex < variables.length - 1;
  const canGoPrevious = currentVariableIndex > 0 && !isAddingNew;
  const isLastVariable = !isAddingNew && currentVariableIndex === variables.length - 1;

  return (
    <div className="space-y-6">
      {/* Progress Summary */}
      {variables.length > 0 && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            <span className="font-medium">{variables.length} variable{variables.length > 1 ? 's' : ''} defined</span>
            {' '}- You can add more or proceed to review
          </AlertDescription>
        </Alert>
      )}

      {/* Variable List Preview */}
      {variables.length > 0 && !isAddingNew && (
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <ListTree className="w-5 h-5 text-gray-600" />
              <CardTitle className="text-base">Defined Variables</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {variables.map((variable, index) => (
                <Badge
                  key={variable.id}
                  variant={index === currentVariableIndex ? 'default' : 'outline'}
                  className="cursor-pointer"
                  onClick={() => {
                    setCurrentIndex(index);
                    setIsAddingNew(false);
                  }}
                >
                  {index + 1}. {variable.name}
                </Badge>
              ))}
              {isAddingNew && (
                <Badge variant="default">
                  {variables.length + 1}. New Variable
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Variable Form */}
      <Card>
        <CardHeader>
          <CardTitle>
            {isAddingNew
              ? `Variable ${variables.length + 1}: Add New Variable`
              : `Variable ${currentVariableIndex + 1}: ${currentVariable ? currentVariable.name || 'Edit Variable' : ''}`}
          </CardTitle>
          <CardDescription>
            {isAddingNew
              ? 'Define a new variable to extract from your documents'
              : 'Edit this variable or navigate to another'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isAddingNew ? (
            <VariableForm
              onSubmit={handleAddVariable}
              onCancel={variables.length > 0 ? () => setIsAddingNew(false) : undefined}
            />
          ) : currentVariable ? (
            <VariableForm
              onSubmit={handleUpdateVariable}
              defaultValues={currentVariable}
              isEditing
            />
          ) : null}
        </CardContent>
      </Card>

      {/* Wizard Navigation */}
      {!isAddingNew && (
        <Card>
          <CardContent className="pt-6">
            <WizardNavigation
              currentIndex={currentVariableIndex}
              totalVariables={variables.length}
              onPrevious={canGoPrevious ? handlePrevious : undefined}
              onNext={canGoNext ? handleNext : undefined}
              onAddAnother={handleAddAnother}
              onFinish={handleFinish}
              canGoNext={canGoNext || isLastVariable}
              canGoPrevious={canGoPrevious}
              isLastVariable={isLastVariable}
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
