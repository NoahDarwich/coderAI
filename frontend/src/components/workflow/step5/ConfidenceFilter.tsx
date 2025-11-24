'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';

interface ConfidenceFilterProps {
  value: number;
  onChange: (value: number) => void;
}

export function ConfidenceFilter({ value, onChange }: ConfidenceFilterProps) {
  const [threshold, setThreshold] = useState(value);

  const handleChange = (values: number[]) => {
    const newValue = values[0];
    setThreshold(newValue);
    onChange(newValue);
  };

  const getConfidenceBadge = (value: number) => {
    if (value >= 85) {
      return <Badge className="bg-green-100 text-green-800 border-green-200">High Confidence (≥85%)</Badge>;
    } else if (value >= 70) {
      return <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200">Medium Confidence (70-84%)</Badge>;
    } else {
      return <Badge className="bg-red-100 text-red-800 border-red-200">Low Confidence (&lt;70%)</Badge>;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">Confidence Filter</CardTitle>
        <CardDescription className="text-xs">
          Filter results by minimum confidence score
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="confidence-slider" className="text-sm">
              Minimum Confidence
            </Label>
            <span className="text-sm font-semibold">{threshold}%</span>
          </div>
          <Slider
            id="confidence-slider"
            min={0}
            max={100}
            step={5}
            value={[threshold]}
            onValueChange={handleChange}
            className="w-full"
            aria-label="Minimum confidence threshold"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
        </div>

        <div className="pt-2">
          {getConfidenceBadge(threshold)}
        </div>

        <div className="text-xs text-muted-foreground space-y-1 pt-2 border-t">
          <p><span className="text-green-600">●</span> High: ≥85% confidence</p>
          <p><span className="text-yellow-600">●</span> Medium: 70-84% confidence</p>
          <p><span className="text-red-600">●</span> Low: &lt;70% confidence</p>
        </div>
      </CardContent>
    </Card>
  );
}
