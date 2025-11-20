import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// TODO(Phase 2): Replace with JWT token validation
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Public routes that don't require authentication
  const publicRoutes = ['/', '/auth/login', '/auth/register'];
  const isPublicRoute = publicRoutes.some((route) => pathname.startsWith(route));

  if (isPublicRoute) {
    return NextResponse.next();
  }

  // Check if user is authenticated (Phase 1: check localStorage via cookie)
  const authCookie = request.cookies.get('auth-storage');

  // In Phase 1, we'll be lenient - if no auth, redirect to login
  // Phase 2: Validate JWT token here
  if (!authCookie) {
    const loginUrl = new URL('/auth/login', request.url);
    loginUrl.searchParams.set('from', pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};
