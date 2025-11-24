'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2 } from 'lucide-react';
import { projectSchema, type ProjectFormData } from '@/lib/validations';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface ProjectSetupFormProps {
  onSubmit: (data: ProjectFormData) => Promise<void>;
  defaultValues?: Partial<ProjectFormData>;
  isLoading?: boolean;
}

export function ProjectSetupForm({
  onSubmit,
  defaultValues,
  isLoading = false,
}: ProjectSetupFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: defaultValues || {
      name: '',
      scale: undefined,
    },
  });

  const selectedScale = watch('scale');

  const handleFormSubmit = async (data: ProjectFormData) => {
    setIsSubmitting(true);
    try {
      await onSubmit(data);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit(handleFormSubmit)}
      className="space-y-6"
      aria-label="Project setup form"
    >
      {/* Project Name */}
      <div className="space-y-2">
        <Label htmlFor="name">
          Project Name <span className="text-red-500" aria-label="required">*</span>
        </Label>
        <Input
          id="name"
          placeholder="e.g., Customer Survey Analysis"
          {...register('name')}
          className={cn(errors.name && 'border-red-500 focus-visible:ring-red-500')}
          disabled={isLoading || isSubmitting}
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
          Choose a descriptive name for your research project
        </p>
      </div>

      {/* Project Scale */}
      <div className="space-y-3" role="group" aria-labelledby="scale-label">
        <Label id="scale-label">
          Project Scale <span className="text-red-500" aria-label="required">*</span>
        </Label>
        <RadioGroup
          value={selectedScale}
          onValueChange={(value) => setValue('scale', value as 'small' | 'large')}
          disabled={isLoading || isSubmitting}
          aria-required="true"
          aria-invalid={!!errors.scale && !selectedScale}
          aria-describedby={errors.scale ? 'scale-error' : undefined}
        >
          <Card
            className={cn(
              'cursor-pointer transition-all',
              selectedScale === 'small' && 'border-blue-600 bg-blue-50',
              errors.scale && !selectedScale && 'border-red-500'
            )}
            onClick={() => !isLoading && !isSubmitting && setValue('scale', 'small')}
            onKeyDown={(e) => {
              if ((e.key === 'Enter' || e.key === ' ') && !isLoading && !isSubmitting) {
                e.preventDefault();
                setValue('scale', 'small');
              }
            }}
            tabIndex={0}
            role="button"
            aria-pressed={selectedScale === 'small'}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start space-x-3">
                <RadioGroupItem value="small" id="small" className="mt-1" aria-label="Small project: Up to 50 documents" />
                <div className="flex-1">
                  <CardTitle className="text-base">Small Project</CardTitle>
                  <CardDescription className="mt-1">
                    Up to 50 documents
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <ul className="text-sm text-gray-600 space-y-1 ml-7">
                <li>• Perfect for pilot studies or small datasets</li>
                <li>• Faster processing times</li>
                <li>• Ideal for testing your extraction schema</li>
              </ul>
            </CardContent>
          </Card>

          <Card
            className={cn(
              'cursor-pointer transition-all',
              selectedScale === 'large' && 'border-blue-600 bg-blue-50',
              errors.scale && !selectedScale && 'border-red-500'
            )}
            onClick={() => !isLoading && !isSubmitting && setValue('scale', 'large')}
            onKeyDown={(e) => {
              if ((e.key === 'Enter' || e.key === ' ') && !isLoading && !isSubmitting) {
                e.preventDefault();
                setValue('scale', 'large');
              }
            }}
            tabIndex={0}
            role="button"
            aria-pressed={selectedScale === 'large'}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start space-x-3">
                <RadioGroupItem value="large" id="large" className="mt-1" aria-label="Large project: 50+ documents" />
                <div className="flex-1">
                  <CardTitle className="text-base">Large Project</CardTitle>
                  <CardDescription className="mt-1">
                    50+ documents
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <ul className="text-sm text-gray-600 space-y-1 ml-7">
                <li>• For comprehensive research projects</li>
                <li>• Process hundreds or thousands of documents</li>
                <li>• Advanced batch processing capabilities</li>
              </ul>
            </CardContent>
          </Card>
        </RadioGroup>

        {errors.scale && (
          <p id="scale-error" className="text-sm text-red-600" role="alert">
            {errors.scale.message}
          </p>
        )}
      </div>

      {/* Submit Button */}
      <div className="flex justify-end pt-4">
        <Button
          type="submit"
          disabled={isLoading || isSubmitting}
          className="min-w-[150px]"
          aria-label="Create project and proceed to document upload"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Creating...
            </>
          ) : (
            'Create Project'
          )}
        </Button>
      </div>
    </form>
  );
}
