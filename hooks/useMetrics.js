import { useCallback } from 'react';
import { metricsService } from '../lib/monitoring/metrics_service';

/**
 * useMetrics Hook
 * 
 * A custom React hook that provides an easy way to track metrics
 * in React components. Provides methods for tracking profile enrichment,
 * job search, and skill verification events.
 * 
 * @returns {Object} Object containing tracking methods
 */
const useMetrics = () => {
  /**
   * Track profile enrichment event
   */
  const trackProfileEnrichment = useCallback(async (enrichmentData = {}) => {
    try {
      return await metricsService.trackProfileEnrichment(enrichmentData);
    } catch (error) {
      console.error('Error tracking profile enrichment:', error);
    }
  }, []);

  /**
   * Track enhanced job search event
   */
  const trackEnhancedJobSearch = useCallback(async (searchData = {}) => {
    try {
      return await metricsService.trackEnhancedJobSearch(searchData);
    } catch (error) {
      console.error('Error tracking enhanced job search:', error);
    }
  }, []);

  /**
   * Track skill verification event
   */
  const trackSkillVerification = useCallback(async (verificationData = {}) => {
    try {
      return await metricsService.trackSkillVerification(verificationData);
    } catch (error) {
      console.error('Error tracking skill verification:', error);
    }
  }, []);

  /**
   * Track generic user event
   */
  const trackEvent = useCallback(async (eventType, eventData = {}) => {
    try {
      return await metricsService.trackEvent(eventType, eventData);
    } catch (error) {
      console.error(`Error tracking ${eventType} event:`, error);
    }
  }, []);

  /**
   * Track user satisfaction rating
   */
  const trackSatisfaction = useCallback(async (satisfactionScore, feedback = '') => {
    try {
      return await metricsService.trackUserSatisfaction(
        satisfactionScore,
        feedback
      );
    } catch (error) {
      console.error('Error tracking user satisfaction:', error);
    }
  }, []);

  return {
    trackProfileEnrichment,
    trackEnhancedJobSearch,
    trackSkillVerification,
    trackEvent,
    trackSatisfaction,
  };
};

export default useMetrics; 