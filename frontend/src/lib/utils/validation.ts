/**
 * Validation Utilities
 * Form validation, file validation, and input sanitization
 */

import { z } from 'zod';
import {
  SUPPORTED_FILE_TYPES,
  DEFAULT_UPLOAD_CONFIG,
  type FileValidationResult
} from '../types/document';

/**
 * Email validation
 */
export const emailSchema = z.string().email('Invalid email address');

/**
 * Password validation (min 8 chars, at least one letter and one number)
 */
export const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[A-Za-z]/, 'Password must contain at least one letter')
  .regex(/[0-9]/, 'Password must contain at least one number');

/**
 * Project name validation
 */
export const projectNameSchema = z
  .string()
  .min(3, 'Project name must be at least 3 characters')
  .max(100, 'Project name must be less than 100 characters')
  .regex(/^[a-zA-Z0-9\s\-_]+$/, 'Project name can only contain letters, numbers, spaces, hyphens, and underscores');

/**
 * Project description validation
 */
export const projectDescriptionSchema = z
  .string()
  .max(500, 'Description must be less than 500 characters')
  .optional();

/**
 * Validate file type
 */
export function validateFileType(file: File): FileValidationResult {
  const supportedTypes = Object.keys(SUPPORTED_FILE_TYPES);

  if (!supportedTypes.includes(file.type)) {
    return {
      valid: false,
      error: `File type not supported. Supported types: PDF, DOCX, TXT`,
    };
  }

  return { valid: true };
}

/**
 * Validate file size
 */
export function validateFileSize(file: File, maxSize: number = DEFAULT_UPLOAD_CONFIG.maxFileSize): FileValidationResult {
  if (file.size > maxSize) {
    const maxSizeMB = (maxSize / (1024 * 1024)).toFixed(1);
    const fileSizeMB = (file.size / (1024 * 1024)).toFixed(1);
    return {
      valid: false,
      error: `File size (${fileSizeMB}MB) exceeds maximum allowed size (${maxSizeMB}MB)`,
    };
  }

  return { valid: true };
}

/**
 * Validate file (type and size)
 */
export function validateFile(file: File): FileValidationResult {
  // Check file type
  const typeValidation = validateFileType(file);
  if (!typeValidation.valid) {
    return typeValidation;
  }

  // Check file size
  const sizeValidation = validateFileSize(file);
  if (!sizeValidation.valid) {
    return sizeValidation;
  }

  return { valid: true };
}

/**
 * Validate multiple files
 */
export function validateFiles(
  files: File[],
  maxFiles: number = DEFAULT_UPLOAD_CONFIG.maxFiles
): FileValidationResult {
  if (files.length === 0) {
    return {
      valid: false,
      error: 'No files selected',
    };
  }

  if (files.length > maxFiles) {
    return {
      valid: false,
      error: `Too many files. Maximum ${maxFiles} files allowed`,
    };
  }

  // Validate each file
  for (const file of files) {
    const validation = validateFile(file);
    if (!validation.valid) {
      return {
        valid: false,
        error: `${file.name}: ${validation.error}`,
      };
    }
  }

  return { valid: true };
}

/**
 * Sanitize user input (remove potentially dangerous characters)
 */
export function sanitizeInput(input: string): string {
  return input
    .trim()
    .replace(/[<>]/g, '') // Remove < and >
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;');
}

/**
 * Validate confidence score (0-100)
 */
export function validateConfidence(confidence: number): boolean {
  return confidence >= 0 && confidence <= 100;
}

/**
 * Login form schema
 */
export const loginFormSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required'),
});

/**
 * Register form schema
 */
export const registerFormSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters').optional(),
  email: emailSchema,
  password: passwordSchema,
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

/**
 * Create project form schema
 */
export const createProjectFormSchema = z.object({
  name: projectNameSchema,
  description: projectDescriptionSchema,
});

/**
 * Export form types
 */
export type LoginFormData = z.infer<typeof loginFormSchema>;
export type RegisterFormData = z.infer<typeof registerFormSchema>;
export type CreateProjectFormData = z.infer<typeof createProjectFormSchema>;
