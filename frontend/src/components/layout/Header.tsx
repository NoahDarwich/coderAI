/**
 * Header Component
 * Main navigation header for the application
 */

'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { FileText, Menu } from 'lucide-react';

interface HeaderProps {
  onMenuClick?: () => void;
  showMenuButton?: boolean;
}

export function Header({ onMenuClick, showMenuButton = false }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center">
        {/* Menu button for mobile */}
        {showMenuButton && onMenuClick && (
          <Button
            variant="ghost"
            size="icon"
            className="mr-2 md:hidden"
            onClick={onMenuClick}
          >
            <Menu className="h-5 w-5" />
            <span className="sr-only">Toggle menu</span>
          </Button>
        )}

        {/* Logo and brand */}
        <Link href="/" className="flex items-center space-x-2">
          <FileText className="h-6 w-6" />
          <span className="font-bold text-lg">Research Automation Tool</span>
        </Link>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Navigation items */}
        <nav className="flex items-center space-x-4">
          <Link href="/dashboard">
            <Button variant="ghost">Dashboard</Button>
          </Link>

          {/* User menu placeholder (Phase 2 - authentication) */}
          <div className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center">
              <span className="text-sm font-medium">U</span>
            </div>
          </div>
        </nav>
      </div>
    </header>
  );
}
