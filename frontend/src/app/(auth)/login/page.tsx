import { Suspense } from 'react';
import { LoginForm } from '@/components/auth/LoginForm';
import Link from 'next/link';

export default function LoginPage() {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50">
          Welcome Back
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-2">
          Sign in to your account to continue
        </p>
      </div>

      <Suspense fallback={<div className="h-48" />}>
        <LoginForm />
      </Suspense>

      <div className="mt-6 text-center text-sm">
        <p className="text-slate-600 dark:text-slate-400">
          Don&apos;t have an account?{' '}
          <Link
            href="/auth/register"
            className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
          >
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
