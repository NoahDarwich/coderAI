import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowRight, CheckCircle } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-16">
        {/* Hero Section */}
        <div className="flex flex-col items-center justify-center text-center space-y-8 py-16">
          <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
            Research Automation Tool
          </h1>
          <p className="text-xl md:text-2xl text-slate-600 dark:text-slate-400 max-w-3xl">
            Extract structured data from your research documents using AI-powered conversational schema builder
          </p>
          <Link href="/dashboard">
            <Button size="lg" className="mt-4">
              Get Started <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>

        {/* Features Section */}
        <div className="grid md:grid-cols-3 gap-8 mt-16 max-w-6xl mx-auto">
          <div className="bg-white dark:bg-slate-800 p-6 rounded-lg shadow-sm">
            <CheckCircle className="h-10 w-10 text-green-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2 text-slate-900 dark:text-slate-50">
              Upload Documents
            </h3>
            <p className="text-slate-600 dark:text-slate-400">
              Support for PDF, DOCX, and TXT files. Drag and drop your research documents with ease.
            </p>
          </div>

          <div className="bg-white dark:bg-slate-800 p-6 rounded-lg shadow-sm">
            <CheckCircle className="h-10 w-10 text-green-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2 text-slate-900 dark:text-slate-50">
              Define Schema with AI
            </h3>
            <p className="text-slate-600 dark:text-slate-400">
              Natural conversation with AI to define what data to extract. No complex configurations needed.
            </p>
          </div>

          <div className="bg-white dark:bg-slate-800 p-6 rounded-lg shadow-sm">
            <CheckCircle className="h-10 w-10 text-green-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2 text-slate-900 dark:text-slate-50">
              Export Results
            </h3>
            <p className="text-slate-600 dark:text-slate-400">
              View extraction results with confidence scores. Export to CSV in wide or long format.
            </p>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-16 text-center">
          <p className="text-slate-600 dark:text-slate-400 mb-4">
            Ready to automate your research workflow?
          </p>
          <Link href="/auth/login">
            <Button variant="outline" size="lg">
              Sign In
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
