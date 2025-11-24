'use client';

import { useState } from 'react';
import { GripVertical, Edit, Trash2, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Variable } from '@/types';
import { cn } from '@/lib/utils';

interface SchemaTableProps {
  variables: Variable[];
  onEdit: (index: number) => void;
  onDelete: (index: number) => void;
  onReorder?: (startIndex: number, endIndex: number) => void;
}

const TYPE_COLORS = {
  text: 'bg-blue-100 text-blue-800',
  number: 'bg-green-100 text-green-800',
  date: 'bg-purple-100 text-purple-800',
  category: 'bg-yellow-100 text-yellow-800',
  boolean: 'bg-pink-100 text-pink-800',
};

const TYPE_LABELS = {
  text: 'Text',
  number: 'Number',
  date: 'Date',
  category: 'Category',
  boolean: 'Yes/No',
};

export function SchemaTable({ variables, onEdit, onDelete, onReorder }: SchemaTableProps) {
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);

  const toggleExpanded = (index: number) => {
    setExpandedRows((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const handleDragStart = (index: number) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (targetIndex: number) => {
    if (draggedIndex !== null && draggedIndex !== targetIndex && onReorder) {
      onReorder(draggedIndex, targetIndex);
    }
    setDraggedIndex(null);
  };

  if (variables.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <p className="text-gray-600 text-center">
            No variables defined yet
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="border rounded-lg overflow-hidden" role="region" aria-label="Schema variables table">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-12" aria-label="Drag handle column"></TableHead>
            <TableHead className="w-12">#</TableHead>
            <TableHead>Variable Name</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Instructions</TableHead>
            <TableHead className="w-32 text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {variables.map((variable, index) => {
            const isExpanded = expandedRows.has(index);
            const isDragging = draggedIndex === index;

            return (
              <TableRow
                key={variable.id}
                draggable={onReorder !== undefined}
                onDragStart={() => handleDragStart(index)}
                onDragOver={handleDragOver}
                onDrop={() => handleDrop(index)}
                className={cn(
                  'group',
                  isDragging && 'opacity-50',
                  onReorder && 'cursor-move'
                )}
                aria-label={`Variable ${index + 1}: ${variable.name}`}
              >
                {/* Drag Handle */}
                <TableCell>
                  {onReorder && (
                    <GripVertical
                      className="w-4 h-4 text-gray-400 group-hover:text-gray-600"
                      aria-label={`Drag to reorder ${variable.name}`}
                      role="img"
                    />
                  )}
                </TableCell>

                {/* Order Number */}
                <TableCell className="font-medium text-gray-500" aria-label={`Position ${index + 1}`}>
                  {index + 1}
                </TableCell>

                {/* Variable Name */}
                <TableCell className="font-medium">
                  {variable.name}
                </TableCell>

                {/* Type */}
                <TableCell>
                  <Badge variant="outline" className={cn('text-xs', TYPE_COLORS[variable.type])}>
                    {TYPE_LABELS[variable.type]}
                  </Badge>
                </TableCell>

                {/* Instructions (truncated with expand) */}
                <TableCell>
                  <div className="flex items-start gap-2">
                    <p className={cn(
                      'text-sm text-gray-600',
                      !isExpanded && 'line-clamp-2'
                    )}>
                      {variable.instructions}
                    </p>
                    {variable.instructions.length > 100 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleExpanded(index)}
                        className="flex-shrink-0"
                        aria-label={isExpanded ? `Collapse instructions for ${variable.name}` : `Expand instructions for ${variable.name}`}
                        aria-expanded={isExpanded}
                      >
                        {isExpanded ? (
                          <ChevronUp className="w-4 h-4" aria-hidden="true" />
                        ) : (
                          <ChevronDown className="w-4 h-4" aria-hidden="true" />
                        )}
                      </Button>
                    )}
                  </div>

                  {/* Classification Rules (if category type) */}
                  {variable.type === 'category' && variable.classificationRules && (
                    <div className="mt-2 flex flex-wrap gap-1" role="list" aria-label="Category options">
                      {variable.classificationRules.map((rule, i) => (
                        <Badge key={i} variant="secondary" className="text-xs" role="listitem">
                          {rule}
                        </Badge>
                      ))}
                    </div>
                  )}
                </TableCell>

                {/* Actions */}
                <TableCell className="text-right">
                  <div className="flex justify-end gap-1" role="group" aria-label={`Actions for ${variable.name}`}>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onEdit(index)}
                      aria-label={`Edit ${variable.name}`}
                    >
                      <Edit className="w-4 h-4" aria-hidden="true" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onDelete(index)}
                      aria-label={`Delete ${variable.name}`}
                    >
                      <Trash2 className="w-4 h-4 text-red-500" aria-hidden="true" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
