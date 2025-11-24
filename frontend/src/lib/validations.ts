import { z } from 'zod';

/**
 * Project creation validation
 */
export const projectSchema = z.object({
  name: z
    .string()
    .min(1, 'Project name is required')
    .max(100, 'Project name must be less than 100 characters'),
  scale: z.enum(['small', 'large'], {
    message: 'Please select a project scale',
  }),
});

export type ProjectFormData = z.infer<typeof projectSchema>;

/**
 * Variable definition validation
 */
export const variableSchema = z.object({
  name: z
    .string()
    .min(1, 'Variable name is required')
    .max(50, 'Variable name must be less than 50 characters'),
  type: z.enum(['text', 'number', 'date', 'category', 'boolean'], {
    message: 'Please select a variable type',
  }),
  instructions: z
    .string()
    .min(10, 'Instructions must be at least 10 characters')
    .max(500, 'Instructions must be less than 500 characters'),
  classificationRules: z.array(z.string()).optional(),
});

export type VariableFormData = z.infer<typeof variableSchema>;

/**
 * Conditional validation: classificationRules required for category type
 */
export const variableSchemaWithConditional = variableSchema.refine(
  (data) => {
    if (data.type === 'category') {
      return data.classificationRules && data.classificationRules.length >= 2;
    }
    return true;
  },
  {
    message: 'Category variables must have at least 2 classification rules',
    path: ['classificationRules'],
  }
);

/**
 * Document upload validation
 */
export const documentUploadSchema = z.object({
  files: z
    .array(
      z.object({
        name: z.string(),
        size: z.number().max(10485760, 'File size must be less than 10MB'),
        type: z.enum([
          'application/pdf',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          'text/plain',
        ], {
          message: 'Only PDF, DOCX, and TXT files are allowed',
        }),
      })
    )
    .min(1, 'At least one file is required'),
});

/**
 * Export configuration validation
 */
export const exportConfigSchema = z.object({
  format: z.enum(['csv']),
  structure: z.enum(['wide', 'long']),
  includeConfidence: z.boolean(),
  includeSourceText: z.boolean(),
  minConfidence: z.number().min(0).max(100).optional(),
});

export type ExportConfigFormData = z.infer<typeof exportConfigSchema>;

/**
 * Sample size validation
 */
export const sampleSizeSchema = z.object({
  sampleSize: z
    .number()
    .int('Sample size must be an integer')
    .min(10, 'Sample size must be at least 10')
    .max(20, 'Sample size must be at most 20'),
});

export type SampleSizeFormData = z.infer<typeof sampleSizeSchema>;
