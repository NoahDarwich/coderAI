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
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface VariableCardProps {
  variable: SchemaVariable;
  className?: string;
}

export function VariableCard({ variable, className }: VariableCardProps) {
  const getTypeIcon = (type: SchemaVariable['type']) => {
    switch (type) {
      case 'date':
        return <Calendar className="h-4 w-4" />;
      case 'location':
        return <MapPin className="h-4 w-4" />;
      case 'classification':
        return <List className="h-4 w-4" />;
      case 'entity':
        return <Tag className="h-4 w-4" />;
      case 'custom':
        return <Type className="h-4 w-4" />;
      default:
        return <Type className="h-4 w-4" />;
    }
  };

  const getTypeBadgeVariant = (type: SchemaVariable['type']) => {
    switch (type) {
      case 'date':
        return 'default';
      case 'location':
        return 'secondary';
      case 'classification':
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
            {variable.description}
          </p>

          {/* Prompt */}
          {variable.prompt && (
            <div className="text-xs text-muted-foreground bg-muted p-2 rounded">
              <strong>Extraction prompt:</strong> {variable.prompt}
            </div>
          )}

          {/* Categories (for classification type) */}
          {variable.type === 'classification' && variable.categories && (
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
