/**
 * HTTP API Client
 *
 * Centralized HTTP client for making API requests to the backend.
 * Supports both real backend API and mock data based on environment configuration.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '30000', 10);
const USE_MOCK_DATA = process.env.NEXT_PUBLIC_USE_MOCK_DATA === 'true';

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public statusText: string,
    public data?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

interface RequestOptions extends RequestInit {
  timeout?: number;
  skipAuth?: boolean;
}

/**
 * Read the access token from Zustand's persisted localStorage
 */
function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem('auth-storage');
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    return parsed?.state?.accessToken ?? null;
  } catch {
    return null;
  }
}

/**
 * Read the refresh token from Zustand's persisted localStorage
 */
function getRefreshToken(): string | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem('auth-storage');
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    return parsed?.state?.refreshToken ?? null;
  } catch {
    return null;
  }
}

/**
 * Write new tokens into Zustand's persisted localStorage
 */
function setTokens(accessToken: string, refreshToken: string): void {
  if (typeof window === 'undefined') return;
  try {
    const raw = localStorage.getItem('auth-storage');
    const parsed = raw ? JSON.parse(raw) : { state: {}, version: 0 };
    parsed.state.accessToken = accessToken;
    parsed.state.refreshToken = refreshToken;
    localStorage.setItem('auth-storage', JSON.stringify(parsed));
  } catch {
    // ignore
  }
}

/**
 * Deduplicated token refresh — only one in-flight refresh at a time
 */
let refreshPromise: Promise<boolean> | null = null;

async function attemptTokenRefresh(): Promise<boolean> {
  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) return false;

    try {
      const res = await fetch(`${API_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!res.ok) return false;

      const data = await res.json();
      setTokens(data.access_token, data.refresh_token);
      return true;
    } catch {
      return false;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

/**
 * Redirect to login page, preserving current path
 */
function redirectToLogin(): void {
  if (typeof window === 'undefined') return;
  const from = window.location.pathname;
  window.location.href = `/auth/login?from=${encodeURIComponent(from)}`;
}

/**
 * Build auth headers for a request
 */
function getAuthHeaders(): Record<string, string> {
  const token = getAccessToken();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

/**
 * Make an HTTP request with timeout, auth, and error handling
 */
async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { timeout = API_TIMEOUT, skipAuth = false, ...fetchOptions } = options;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const url = `${API_URL}${endpoint}`;

    const response = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...(skipAuth ? {} : getAuthHeaders()),
        ...fetchOptions.headers,
      },
    });

    clearTimeout(timeoutId);

    // Handle 401 — attempt token refresh then retry once
    if (response.status === 401 && !skipAuth) {
      const refreshed = await attemptTokenRefresh();
      if (refreshed) {
        return request<T>(endpoint, { ...options, skipAuth: false });
      }
      redirectToLogin();
      throw new ApiError('Authentication required', 401, 'Unauthorized');
    }

    // Handle non-OK responses
    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { message: response.statusText };
      }

      throw new ApiError(
        errorData.detail || errorData.message || `Request failed with status ${response.status}`,
        response.status,
        response.statusText,
        errorData
      );
    }

    // Handle empty responses (204 No Content, etc.)
    if (response.status === 204) {
      return {} as T;
    }

    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      return {} as T;
    }

    const data = await response.json();
    return data as T;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new ApiError('Request timeout', 408, 'Request Timeout');
      }
      throw new ApiError(error.message, 0, 'Network Error');
    }

    throw new ApiError('Unknown error occurred', 0, 'Unknown Error');
  }
}

/**
 * HTTP Client API
 */
export const apiClient = {
  /**
   * Check if mock data should be used
   */
  get useMockData(): boolean {
    return USE_MOCK_DATA;
  },

  /**
   * GET request
   */
  get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return request<T>(endpoint, {
      ...options,
      method: 'GET',
    });
  },

  /**
   * POST request
   */
  post<T>(endpoint: string, data?: unknown, options?: RequestOptions): Promise<T> {
    return request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  /**
   * PUT request
   */
  put<T>(endpoint: string, data?: unknown, options?: RequestOptions): Promise<T> {
    return request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  /**
   * PATCH request
   */
  patch<T>(endpoint: string, data?: unknown, options?: RequestOptions): Promise<T> {
    return request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  /**
   * DELETE request
   */
  delete<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return request<T>(endpoint, {
      ...options,
      method: 'DELETE',
    });
  },

  /**
   * Upload file(s) using FormData
   */
  async upload<T>(
    endpoint: string,
    files: File | File[],
    additionalData?: Record<string, string>,
    options?: RequestOptions
  ): Promise<T> {
    const formData = new FormData();

    // Backend expects single file as 'file'
    const fileArray = Array.isArray(files) ? files : [files];
    fileArray.forEach((file) => {
      formData.append('file', file);
    });

    // Add additional data
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }

    const { timeout = API_TIMEOUT, skipAuth = false, ...fetchOptions } = options || {};
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const url = `${API_URL}${endpoint}`;

      const response = await fetch(url, {
        ...fetchOptions,
        method: 'POST',
        body: formData,
        signal: controller.signal,
        headers: {
          ...(skipAuth ? {} : getAuthHeaders()),
          ...(fetchOptions.headers as Record<string, string>),
          // Don't set Content-Type — browser sets it with boundary for FormData
        },
      });

      clearTimeout(timeoutId);

      // Handle 401
      if (response.status === 401 && !skipAuth) {
        const refreshed = await attemptTokenRefresh();
        if (refreshed) {
          return this.upload<T>(endpoint, files, additionalData, options);
        }
        redirectToLogin();
        throw new ApiError('Authentication required', 401, 'Unauthorized');
      }

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          errorData = { message: response.statusText };
        }

        throw new ApiError(
          errorData.detail || errorData.message || `Upload failed with status ${response.status}`,
          response.status,
          response.statusText,
          errorData
        );
      }

      const data = await response.json();
      return data as T;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof ApiError) {
        throw error;
      }

      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new ApiError('Upload timeout', 408, 'Request Timeout');
        }
        throw new ApiError(error.message, 0, 'Network Error');
      }

      throw new ApiError('Unknown error occurred', 0, 'Unknown Error');
    }
  },

  /**
   * Download file
   */
  async download(endpoint: string, filename: string, options?: RequestOptions): Promise<void> {
    const { timeout = API_TIMEOUT, skipAuth = false, ...fetchOptions } = options || {};
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const url = `${API_URL}${endpoint}`;

      const response = await fetch(url, {
        ...fetchOptions,
        signal: controller.signal,
        headers: {
          ...(skipAuth ? {} : getAuthHeaders()),
          ...(fetchOptions.headers as Record<string, string>),
        },
      });

      clearTimeout(timeoutId);

      // Handle 401
      if (response.status === 401 && !skipAuth) {
        const refreshed = await attemptTokenRefresh();
        if (refreshed) {
          return this.download(endpoint, filename, options);
        }
        redirectToLogin();
        throw new ApiError('Authentication required', 401, 'Unauthorized');
      }

      if (!response.ok) {
        throw new ApiError(
          `Download failed with status ${response.status}`,
          response.status,
          response.statusText
        );
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof ApiError) {
        throw error;
      }

      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new ApiError('Download timeout', 408, 'Request Timeout');
        }
        throw new ApiError(error.message, 0, 'Network Error');
      }

      throw new ApiError('Unknown error occurred', 0, 'Unknown Error');
    }
  },
};

export default apiClient;
