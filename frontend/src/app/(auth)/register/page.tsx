import { RegisterForm } from '@/components/auth/RegisterForm';
import Link from 'next/link';

export default function RegisterPage() {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50">
          Create Account
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-2">
          Sign up to start automating your research
        </p>
      </div>

      <RegisterForm />

      <div className="mt-6 text-center text-sm">
        <p className="text-slate-600 dark:text-slate-400">
          Already have an account?{' '}
          <Link
            href="/auth/login"
            className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
          >
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
