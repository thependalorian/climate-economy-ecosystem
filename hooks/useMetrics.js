import { useCallback } from 'react';
import { tracingService } from '@/lib/tracing/langsmith-client';

/**
 * useMetrics Hook
 * 
 * A custom React hook that provides an easy way to track metrics
 * in React components. Uses LangSmith tracing for comprehensive
 * monitoring and debugging.
 * 
 * @returns {Object} Object containing tracking methods
 */
export function useMetrics() {
  /**
   * Track a generic event
   * 
   * @param {string} eventName - The name of the event
   * @param {Object} eventData - Data associated with the event
   */
  const trackEvent = useCallback(async (eventName, eventData) => {
    try {
      // Create a unique run ID for tracing
      const runId = tracingService.createRunId();
      
      // Log the event
      await tracingService.logLlmCall(
        'metrics',
        eventName,
        JSON.stringify(eventData),
        runId,
        { event_type: 'client_side_metric' }
      );
      
      // Also send to backend API
      await fetch('/api/metrics/track', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          event_name: eventName,
          event_data: eventData,
          run_id: runId
        }),
      });
    } catch (error) {
      console.error('Error tracking metric:', error);
      // Silently fail - metrics should not break the app
    }
  }, []);
  
  /**
   * Track a page view
   * 
   * @param {string} page - The page being viewed
   */
  const trackPageView = useCallback((page) => {
    trackEvent('page_view', { page });
  }, [trackEvent]);
  
  /**
   * Track a search
   * 
   * @param {string} query - The search query
   * @param {number} resultsCount - Number of results returned
   */
  const trackSearch = useCallback((query, resultsCount) => {
    trackEvent('search', { query, results_count: resultsCount });
  }, [trackEvent]);
  
  /**
   * Track a chat completion
   * 
   * @param {string} query - The user query
   * @param {number} responseTimeMs - Response time in milliseconds
   */
  const trackChatCompletion = useCallback((query, responseTimeMs) => {
    trackEvent('chat_completion', { query, response_time_ms: responseTimeMs });
  }, [trackEvent]);
  
  /**
   * Track an error
   * 
   * @param {string} errorType - Type of error
   * @param {string} errorMessage - Error message
   */
  const trackError = useCallback((errorType, errorMessage) => {
    trackEvent('error', { error_type: errorType, error_message: errorMessage });
  }, [trackEvent]);
  
  /**
   * Track profile enrichment
   * 
   * @param {Object} enrichmentData - Data about the profile enrichment
   */
  const trackProfileEnrichment = useCallback((enrichmentData = {}) => {
    trackEvent('profile_enrichment', enrichmentData);
  }, [trackEvent]);
  
  /**
   * Track enhanced job search
   * 
   * @param {Object} searchData - Data about the job search
   */
  const trackEnhancedJobSearch = useCallback((searchData = {}) => {
    trackEvent('enhanced_job_search', searchData);
  }, [trackEvent]);
  
  /**
   * Track skill verification
   * 
   * @param {Object} verificationData - Data about the skill verification
   */
  const trackSkillVerification = useCallback((verificationData = {}) => {
    trackEvent('skill_verification', verificationData);
  }, [trackEvent]);
  
  return {
    trackEvent,
    trackPageView,
    trackSearch,
    trackChatCompletion,
    trackError,
    trackProfileEnrichment,
    trackEnhancedJobSearch,
    trackSkillVerification
  };
}
