'use client';

import { useEffect, useRef } from 'react';
import { CheckCircle2, XCircle, AlertCircle, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ProcessingLog as ProcessingLogType } from '@/types';
import { cn } from '@/lib/utils';

interface ProcessingLogProps {
  logs: ProcessingLogType[];
  isProcessing: boolean;
}

const LEVEL_ICONS = {
  info: CheckCircle2,
  warning: AlertCircle,
  error: XCircle,
};

const LEVEL_COLORS = {
  info: 'text-blue-600',
  warning: 'text-yellow-600',
  error: 'text-red-600',
};

export function ProcessingLog({ logs, isProcessing }: ProcessingLogProps) {
  const logEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs.length]);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">Processing Log</CardTitle>
          {isProcessing && (
            <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
              <Loader2 className="w-3 h-3 mr-1 animate-spin" />
              Processing
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 max-h-96 overflow-y-auto">
          {logs.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-8">
              No logs yet. Processing will begin soon...
            </p>
          ) : (
            <div className="space-y-2 font-mono text-xs">
              {logs.map((log, index) => {
                const Icon = LEVEL_ICONS[log.level];
                return (
                  <div
                    key={index}
                    className={cn(
                      'flex items-start gap-2 p-2 rounded',
                      log.level === 'error' && 'bg-red-50',
                      log.level === 'warning' && 'bg-yellow-50'
                    )}
                  >
                    <Icon className={cn('w-4 h-4 flex-shrink-0 mt-0.5', LEVEL_COLORS[log.level])} />
                    <div className="flex-1 min-w-0">
                      <span className="text-gray-500">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                      {' '}
                      <span className="text-gray-900">{log.message}</span>
                      {log.documentId && (
                        <span className="text-gray-500 ml-2">
                          (Document: {log.documentId.substring(0, 8)}...)
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
              <div ref={logEndRef} />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
