import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // redirect on certain conditions
import shouldLogin from '../utils/shouldLogin';
// NOTE: the logger is not necessarily needed, 
// but it is convenient to log the requests for debugging

// Module-level variables
let isFetchWrapped = false;
let originalFetch = null;
let wrappedFetchInstance = null;

// Module-level storage for current callbacks (updated by hook instances)
let currentLabel = 'fetch-logger';
let currentLogger = console.info;
// Use navigate function to redirect, 
// but this include a hook, should be dealed carefully
let currentNavigate = null;

// Initialize fetch wrapper once at module load
// This ensures we capture the original fetch before any wrapping
if (typeof window !== 'undefined' && typeof window.fetch === 'function' && !isFetchWrapped) {
  // Store the ORIGINAL fetch before wrapping
  originalFetch = window.fetch.bind(window);
  
  wrappedFetchInstance = async (...args) => {
    const [resource, config = {}] = args;
    const method = (config.method || 'GET').toUpperCase();
    const target =
      typeof resource === 'string'
        ? resource
        : resource && resource.url
        ? resource.url
        : 'unknown';
    const started = performance.now();

    try {
      // Call the ORIGINAL fetch, not the wrapped one
      const response = await originalFetch(...args);
      const duration = Math.round(performance.now() - started);
      const status = response.status;
      const url = response.url || target;
      
      // Log all response status codes
      currentLogger(
        `[${currentLabel}] ${method} ${url} -> ${status} (${duration}ms)`
      );

      // Check whether a redirect should happen (e.g., not logged in)
      const redirectPath = shouldLogin(status);
      if (redirectPath && typeof currentNavigate === 'function') {
        try {
          currentNavigate(redirectPath);
        } catch (err) {
          // If navigation fails for any reason, just log it and continue
          currentLogger(`[${currentLabel}] Failed to navigate to ${redirectPath}:`, err);
        }
      }

      return response;
    } catch (error) {
      const duration = Math.round(performance.now() - started);
      currentLogger(
        `[${currentLabel}] ${method} ${target} -> FAILED (${duration}ms)`,
        error
      );
      throw error;
    }
  };

  wrappedFetchInstance._wrappedByUseFetchLogger = true;
  window.fetch = wrappedFetchInstance;
  isFetchWrapped = true;
}

/**
 * Hook that wraps window.fetch to log response status codes for all requests.
 *
 * @param {string} label - Helpful label to identify where the logger was installed.
 * @param {{ logger?: Function }} [options] - Optional logger; defaults to console.info.
 */
export default function useFetchLogger(label = 'fetch-logger', options = {}) {
  const { logger = console.info } = options;
  const navigate = useNavigate();

  // Update module-level callbacks when hook mounts or values change
  useEffect(() => {
    if (typeof window === 'undefined' || typeof window.fetch !== 'function') {
      return;
    }

    // Update module-level callbacks so wrapped fetch can use them
    currentLabel = label;
    currentLogger = logger;
    currentNavigate = navigate;

    // Verify fetch is still wrapped (safety check)
    if (!isFetchWrapped || window.fetch !== wrappedFetchInstance) {
      // Only re-initialize if originalFetch exists (we already have the original)
      // If originalFetch doesn't exist, the module-level initialization should have handled it
      if (originalFetch && wrappedFetchInstance) {
        wrappedFetchInstance._wrappedByUseFetchLogger = true;
        window.fetch = wrappedFetchInstance;
        isFetchWrapped = true;
      }
    }
  }, [logger, label, navigate]);
}
