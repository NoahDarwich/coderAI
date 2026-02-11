/**
 * VariableCard Component
 * Displays a schema variable with its details
 */

'use client';

import { SchemaVariable } from '@/lib/types/api';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Calendar,
  MapPin,
  Tag,
  Type,
  List,
  Hash,
  ToggleLeft,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface VariableCardProps {
  variable: SchemaVariable;
  className?: string;
}

export function VariableCard({ variable, className }: VariableCardProps) {
  const getTypeIcon = (type: SchemaVariable['type']) => {
    switch (type) {
      case 'DATE':
        return <Calendar className="h-4 w-4" />;
      case 'LOCATION':
        return <MapPin className="h-4 w-4" />;
      case 'CATEGORY':
        return <List className="h-4 w-4" />;
      case 'NUMBER':
        return <Hash className="h-4 w-4" />;
      case 'BOOLEAN':
        return <ToggleLeft className="h-4 w-4" />;
      case 'TEXT':
      default:
        return <Type className="h-4 w-4" />;
    }
  };

  const getTypeBadgeVariant = (type: SchemaVariable['type']) => {
    switch (type) {
      case 'DATE':
        return 'default';
      case 'LOCATION':
        return 'secondary';
      case 'CATEGORY':
        return 'outline';
      default:
        return 'outline';
    }
  };

  return (
    <Card className={cn('p-4', className)}>
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className="flex-shrink-0 mt-1 p-2 rounded-lg bg-primary/10 text-primary">
          {getTypeIcon(variable.type)}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Name and type */}
          <div className="flex items-center gap-2 mb-1">
            <h4 className="text-sm font-semibold">
              {variable.name.replace(/_/g, ' ')}
            </h4>
            <Badge variant={getTypeBadgeVariant(variable.type)} className="text-xs">
              {variable.type}
            </Badge>
          </div>

          {/* Description */}
          <p className="text-sm text-muted-foreground mb-2">
            {variable.instructions || variable.description}
          </p>

          {/* Prompt */}
          {variable.prompt && (
            <div className="text-xs text-muted-foreground bg-muted p-2 rounded">
              <strong>Extraction prompt:</strong> {variable.prompt}
            </div>
          )}

          {/* Categories (for CATEGORY type) */}
          {variable.type === 'CATEGORY' && variable.categories && (
            <div className="mt-2">
              <p className="text-xs font-medium text-muted-foreground mb-1">
                Categories:
              </p>
              <div className="flex flex-wrap gap-1">
                {variable.categories.map((category) => (
                  <Badge
                    key={category}
                    variant="outline"
                    className="text-xs"
                  >
                    {category}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}
