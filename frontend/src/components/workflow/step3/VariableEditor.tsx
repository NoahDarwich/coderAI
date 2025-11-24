'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Variable } from '@/types';

interface VariableEditorProps {
  variable: Variable | null;
  open: boolean;
  onClose: () => void;
  onSave: (variable: Variable) => void;
}

export function VariableEditor({ variable, open, onClose, onSave }: VariableEditorProps) {
  const [name, setName] = useState('');
  const [type, setType] = useState<Variable['type']>('text');
  const [instructions, setInstructions] = useState('');
  const [classificationRules, setClassificationRules] = useState('');

  // Reset form when variable changes
  useEffect(() => {
    if (variable) {
      setName(variable.name);
      setType(variable.type);
      setInstructions(variable.instructions || '');
      setClassificationRules(variable.classificationRules?.join(', ') || '');
    }
  }, [variable]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!variable) return;

    const updatedVariable: Variable = {
      ...variable,
      name,
      type,
      instructions: instructions,
      classificationRules: type === 'category' && classificationRules
        ? classificationRules.split(',').map((rule) => rule.trim()).filter(Boolean)
        : undefined,
    };

    onSave(updatedVariable);
    handleClose();
  };

  const handleClose = () => {
    setName('');
    setType('text');
    setInstructions('');
    setClassificationRules('');
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Edit Variable</DialogTitle>
          <DialogDescription>
            Modify the variable definition and extraction rules.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="variable-name">Variable Name</Label>
            <Input
              id="variable-name"
              placeholder="e.g., Event Date"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
            <p className="text-sm text-muted-foreground">
              A descriptive name for this data field
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="variable-type">Data Type</Label>
            <Select value={type} onValueChange={(value) => setType(value as Variable['type'])}>
              <SelectTrigger id="variable-type">
                <SelectValue placeholder="Select data type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="text">Text</SelectItem>
                <SelectItem value="number">Number</SelectItem>
                <SelectItem value="date">Date</SelectItem>
                <SelectItem value="category">Category</SelectItem>
                <SelectItem value="boolean">Boolean (Yes/No)</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-sm text-muted-foreground">
              The type of data to extract
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="instructions">Extraction Instructions</Label>
            <Textarea
              id="instructions"
              placeholder="Tell the AI how to extract this data..."
              className="min-h-[100px]"
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
            />
            <p className="text-sm text-muted-foreground">
              Provide context to help the AI accurately extract this field
            </p>
          </div>

          {type === 'category' && (
            <div className="space-y-2">
              <Label htmlFor="classification-rules">Category Options</Label>
              <Input
                id="classification-rules"
                placeholder="e.g., Protest, Rally, March, Strike"
                value={classificationRules}
                onChange={(e) => setClassificationRules(e.target.value)}
              />
              <p className="text-sm text-muted-foreground">
                Comma-separated list of possible categories
              </p>
            </div>
          )}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button type="submit">
              Save Changes
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
