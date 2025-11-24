'use client';

import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2, Sparkles, Plus, X } from 'lucide-react';
import { variableSchemaWithConditional, type VariableFormData } from '@/lib/validations';
import { Variable, VariableType } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface VariableFormProps {
  onSubmit: (data: VariableFormData) => void;
  onCancel?: () => void;
  defaultValues?: Partial<Variable>;
  isEditing?: boolean;
}

const VARIABLE_TYPES: { value: VariableType; label: string; description: string }[] = [
  { value: 'text', label: 'Text', description: 'Free-form text (names, descriptions)' },
  { value: 'number', label: 'Number', description: 'Numeric values (counts, amounts)' },
  { value: 'date', label: 'Date', description: 'Date or timestamp' },
  { value: 'category', label: 'Category', description: 'Classification into predefined categories' },
  { value: 'boolean', label: 'Yes/No', description: 'True or false values' },
];

// Mock AI suggestions
const generateSuggestions = (variableName: string, variableType: VariableType): string => {
  const suggestions: Record<VariableType, string> = {
    text: `Extract the ${variableName.toLowerCase()} exactly as it appears in the document. Look for this information in the main body text or metadata sections.`,
    number: `Find and extract numeric values related to ${variableName.toLowerCase()}. If multiple values are present, use the most prominent or clearly stated number.`,
    date: `Identify and extract the date for ${variableName.toLowerCase()}. Accept formats like MM/DD/YYYY, DD-MM-YYYY, or written formats like "January 15, 2024".`,
    category: `Classify ${variableName.toLowerCase()} based on the content. Analyze the context and assign the most appropriate category from the provided options.`,
    boolean: `Determine if ${variableName.toLowerCase()} is true or false based on the document content. Look for explicit statements or strong indicators.`,
  };
  return suggestions[variableType] || '';
};

export function VariableForm({
  onSubmit,
  onCancel,
  defaultValues,
  isEditing = false,
}: VariableFormProps) {
  const [categories, setCategories] = useState<string[]>(defaultValues?.classificationRules || []);
  const [newCategory, setNewCategory] = useState('');
  const [showSuggestion, setShowSuggestion] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setValue,
    watch,
  } = useForm<VariableFormData>({
    resolver: zodResolver(variableSchemaWithConditional),
    defaultValues: {
      name: defaultValues?.name || '',
      type: defaultValues?.type || undefined,
      instructions: defaultValues?.instructions || '',
      classificationRules: defaultValues?.classificationRules || [],
    },
  });

  const selectedType = watch('type');
  const variableName = watch('name');
  const instructions = watch('instructions');

  // Update categories when form type changes to category
  useEffect(() => {
    if (selectedType === 'category') {
      setValue('classificationRules', categories);
    }
  }, [selectedType, categories, setValue]);

  const handleFormSubmit = (data: VariableFormData) => {
    onSubmit(data);
  };

  const handleGenerateSuggestion = () => {
    if (variableName && selectedType) {
      const suggestion = generateSuggestions(variableName, selectedType);
      setValue('instructions', suggestion);
      setShowSuggestion(true);
    }
  };

  const addCategory = () => {
    if (newCategory.trim() && !categories.includes(newCategory.trim())) {
      const updated = [...categories, newCategory.trim()];
      setCategories(updated);
      setValue('classificationRules', updated);
      setNewCategory('');
    }
  };

  const removeCategory = (index: number) => {
    const updated = categories.filter((_, i) => i !== index);
    setCategories(updated);
    setValue('classificationRules', updated);
  };

  return (
    <form
      onSubmit={handleSubmit(handleFormSubmit)}
      className="space-y-6"
      aria-label="Variable definition form"
    >
      {/* Variable Name */}
      <div className="space-y-2">
        <Label htmlFor="name">
          Variable Name <span className="text-red-500" aria-label="required">*</span>
        </Label>
        <Input
          id="name"
          placeholder="e.g., Date of Event, Location, Number of Participants"
          {...register('name')}
          className={cn(errors.name && 'border-red-500')}
          aria-required="true"
          aria-invalid={!!errors.name}
          aria-describedby={errors.name ? 'name-error name-help' : 'name-help'}
        />
        {errors.name && (
          <p id="name-error" className="text-sm text-red-600" role="alert">
            {errors.name.message}
          </p>
        )}
        <p id="name-help" className="text-sm text-gray-500">
          Give your variable a clear, descriptive name
        </p>
      </div>

      {/* Variable Type */}
      <div className="space-y-2">
        <Label htmlFor="type">
          Variable Type <span className="text-red-500" aria-label="required">*</span>
        </Label>
        <Select
          value={selectedType}
          onValueChange={(value) => setValue('type', value as VariableType)}
        >
          <SelectTrigger
            id="type"
            className={cn(errors.type && 'border-red-500')}
            aria-required="true"
            aria-invalid={!!errors.type}
            aria-describedby={errors.type ? 'type-error' : undefined}
          >
            <SelectValue placeholder="Select a variable type" />
          </SelectTrigger>
          <SelectContent>
            {VARIABLE_TYPES.map((type) => (
              <SelectItem key={type.value} value={type.value}>
                <div>
                  <div className="font-medium">{type.label}</div>
                  <div className="text-xs text-gray-500">{type.description}</div>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.type && (
          <p id="type-error" className="text-sm text-red-600" role="alert">
            {errors.type.message}
          </p>
        )}
      </div>

      {/* Classification Rules (for category type) */}
      {selectedType === 'category' && (
        <div className="space-y-2" role="group" aria-labelledby="categories-label">
          <Label id="categories-label">
            Classification Categories <span className="text-red-500" aria-label="required">*</span>
          </Label>
          <div className="space-y-2">
            <div className="flex gap-2">
              <Input
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                placeholder="Add a category (e.g., Policy, Research, News)"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addCategory();
                  }
                }}
                aria-label="New category name"
              />
              <Button
                type="button"
                onClick={addCategory}
                variant="outline"
                aria-label="Add category to list"
              >
                <Plus className="w-4 h-4 mr-1" aria-hidden="true" />
                Add
              </Button>
            </div>

            {categories.length > 0 && (
              <div className="flex flex-wrap gap-2" role="list" aria-label="Selected categories">
                {categories.map((category, index) => (
                  <Badge key={index} variant="secondary" className="text-sm py-1" role="listitem">
                    {category}
                    <button
                      type="button"
                      onClick={() => removeCategory(index)}
                      className="ml-2 hover:text-red-600"
                      aria-label={`Remove ${category} category`}
                    >
                      <X className="w-3 h-3" aria-hidden="true" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}

            {errors.classificationRules && (
              <p className="text-sm text-red-600">{errors.classificationRules.message}</p>
            )}

            <p className="text-sm text-gray-500">
              Add 2-10 categories for classification. Press Enter or click Add.
            </p>
          </div>
        </div>
      )}

      {/* Extraction Instructions */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label htmlFor="instructions">
            Extraction Instructions <span className="text-red-500">*</span>
          </Label>
          {variableName && selectedType && (
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleGenerateSuggestion}
            >
              <Sparkles className="w-3 h-3 mr-1" />
              AI Suggestion
            </Button>
          )}
        </div>
        <Textarea
          id="instructions"
          placeholder="Describe how to extract this variable from documents. Be specific about what to look for and how to handle edge cases."
          rows={5}
          {...register('instructions')}
          className={cn(errors.instructions && 'border-red-500')}
          aria-describedby="instructions-error"
        />
        {errors.instructions && (
          <p id="instructions-error" className="text-sm text-red-600">
            {errors.instructions.message}
          </p>
        )}
        {showSuggestion && instructions && (
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="pt-4">
              <p className="text-sm text-blue-900">
                <Sparkles className="w-4 h-4 inline mr-1" />
                AI generated suggestion applied! You can edit it as needed.
              </p>
            </CardContent>
          </Card>
        )}
        <p className="text-sm text-gray-500">
          Provide clear instructions for extracting this variable (10-500 characters)
        </p>
      </div>

      {/* Form Actions */}
      <div className="flex justify-end gap-3 pt-4">
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              {isEditing ? 'Updating...' : 'Adding...'}
            </>
          ) : isEditing ? (
            'Update Variable'
          ) : (
            'Add Variable'
          )}
        </Button>
      </div>
    </form>
  );
}
