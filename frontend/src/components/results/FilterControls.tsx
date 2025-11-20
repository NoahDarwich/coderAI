/**
 * FilterControls Component
 * Filter and search controls for extraction results
 */

'use client';

import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Search, X, Flag } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface FilterState {
  search: string;
  minConfidence: number;
  flaggedOnly: boolean;
  sortBy: string;
  sortOrder: 'asc' | 'desc';
}

interface FilterControlsProps {
  filters: FilterState;
  onFiltersChange: (filters: Partial<FilterState>) => void;
  onReset: () => void;
  className?: string;
}

export function FilterControls({
  filters,
  onFiltersChange,
  onReset,
  className,
}: FilterControlsProps) {
  const hasActiveFilters =
    filters.search !== '' ||
    filters.minConfidence > 0 ||
    filters.flaggedOnly;

  return (
    <div className={cn('space-y-4', className)}>
      {/* Search and flagged filter */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search results..."
            value={filters.search}
            onChange={(e) => onFiltersChange({ search: e.target.value })}
            className="pl-9"
          />
        </div>

        {/* Flagged only toggle */}
        <Button
          variant={filters.flaggedOnly ? 'default' : 'outline'}
          onClick={() =>
            onFiltersChange({ flaggedOnly: !filters.flaggedOnly })
          }
          className={cn(
            filters.flaggedOnly && 'bg-orange-500 hover:bg-orange-600'
          )}
        >
          <Flag className={cn('h-4 w-4 mr-2', filters.flaggedOnly && 'fill-current')} />
          Flagged Only
        </Button>

        {/* Reset filters */}
        {hasActiveFilters && (
          <Button variant="ghost" onClick={onReset}>
            <X className="h-4 w-4 mr-2" />
            Clear
          </Button>
        )}
      </div>

      {/* Confidence filter */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium">
            Minimum Confidence: {filters.minConfidence}%
          </label>
        </div>
        <Slider
          value={[filters.minConfidence]}
          onValueChange={([value]) => onFiltersChange({ minConfidence: value })}
          max={100}
          step={5}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>0%</span>
          <span>50%</span>
          <span>100%</span>
        </div>
      </div>

      {/* Sort controls */}
      <div className="flex gap-3">
        <Select
          value={filters.sortBy}
          onValueChange={(value) => onFiltersChange({ sortBy: value })}
        >
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="document">Document Name</SelectItem>
            <SelectItem value="confidence">Confidence</SelectItem>
            <SelectItem value="date">Extraction Date</SelectItem>
          </SelectContent>
        </Select>

        <Select
          value={filters.sortOrder}
          onValueChange={(value: 'asc' | 'desc') =>
            onFiltersChange({ sortOrder: value })
          }
        >
          <SelectTrigger className="w-[150px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="asc">Ascending</SelectItem>
            <SelectItem value="desc">Descending</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
