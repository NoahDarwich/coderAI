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
}

/**
 * Make an HTTP request with timeout and error handling
 */
async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { timeout = API_TIMEOUT, ...fetchOptions } = options;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const url = `${API_URL}${endpoint}`;

    const response = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...fetchOptions.headers,
      },
    });

    clearTimeout(timeoutId);

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

    // Handle empty responses
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

    // Add files
    const fileArray = Array.isArray(files) ? files : [files];
    fileArray.forEach((file) => {
      formData.append('files', file);
    });

    // Add additional data
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }

    const { timeout = API_TIMEOUT, ...fetchOptions } = options || {};
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const url = `${API_URL}${endpoint}`;

      const response = await fetch(url, {
        ...fetchOptions,
        method: 'POST',
        body: formData,
        signal: controller.signal,
        // Don't set Content-Type header - browser will set it with boundary
      });

      clearTimeout(timeoutId);

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
    const { timeout = API_TIMEOUT, ...fetchOptions } = options || {};
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const url = `${API_URL}${endpoint}`;

      const response = await fetch(url, {
        ...fetchOptions,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

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
