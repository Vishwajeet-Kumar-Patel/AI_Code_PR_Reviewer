'use client';

import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Sparkles, TrendingUp, AlertTriangle, Code, Activity, CheckCircle, RefreshCw } from 'lucide-react';
import apiClient from '@/lib/api-client';

interface InsightStats {
  totalReviews: number;
  averageQualityScore: number;
  criticalIssues: number;
  resolvedIssues: number;
  topLanguages: { language: string; count: number }[];
  recentTrends: { date: string; reviews: number }[];
}

export default function Insights() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<InsightStats>({
    totalReviews: 0,
    averageQualityScore: 0,
    criticalIssues: 0,
    resolvedIssues: 0,
    topLanguages: [],
    recentTrends: [],
  });

  useEffect(() => {
    loadInsights();
  }, []);

  const loadInsights = async () => {
    setLoading(true);
    try {
      // Simulate loading insights data
      // In production, this would call the backend API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setStats({
        totalReviews: 156,
        averageQualityScore: 8.4,
        criticalIssues: 12,
        resolvedIssues: 89,
        topLanguages: [
          { language: 'TypeScript', count: 45 },
          { language: 'Python', count: 38 },
          { language: 'JavaScript', count: 32 },
          { language: 'Java', count: 21 },
        ],
        recentTrends: [
          { date: '2025-12-18', reviews: 8 },
          { date: '2025-12-17', reviews: 12 },
          { date: '2025-12-16', reviews: 10 },
          { date: '2025-12-15', reviews: 15 },
        ],
      });
    } catch (error) {
      console.error('Failed to load insights:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout user={{ name: 'Vishwajeet Kumar', avatar_url: '' }}>
      <div className="p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white mb-2">AI Insights</h1>
            <p className="text-gray-400">Code quality metrics and analytics powered by AI</p>
          </div>
          <button
            onClick={loadInsights}
            disabled={loading}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <Sparkles className="w-8 h-8 text-primary-500 animate-pulse mx-auto mb-4" />
              <p className="text-gray-400">Loading AI insights...</p>
            </div>
          </div>
        ) : (
          <>
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-dark-800 border border-dark-700 rounded-lg p-5">
                <div className="flex items-center justify-between mb-3">
                  <Code className="w-8 h-8 text-blue-500" />
                  <span className="text-xs text-gray-400">Total</span>
                </div>
                <div className="text-2xl font-bold text-white mb-1">{stats.totalReviews}</div>
                <div className="text-sm text-gray-400">Code Reviews</div>
              </div>

              <div className="bg-dark-800 border border-dark-700 rounded-lg p-5">
                <div className="flex items-center justify-between mb-3">
                  <TrendingUp className="w-8 h-8 text-green-500" />
                  <span className="text-xs text-gray-400">Average</span>
                </div>
                <div className="text-2xl font-bold text-white mb-1">{stats.averageQualityScore.toFixed(1)}/10</div>
                <div className="text-sm text-gray-400">Quality Score</div>
              </div>

              <div className="bg-dark-800 border border-dark-700 rounded-lg p-5">
                <div className="flex items-center justify-between mb-3">
                  <AlertTriangle className="w-8 h-8 text-red-500" />
                  <span className="text-xs text-gray-400">Active</span>
                </div>
                <div className="text-2xl font-bold text-white mb-1">{stats.criticalIssues}</div>
                <div className="text-sm text-gray-400">Critical Issues</div>
              </div>

              <div className="bg-dark-800 border border-dark-700 rounded-lg p-5">
                <div className="flex items-center justify-between mb-3">
                  <CheckCircle className="w-8 h-8 text-emerald-500" />
                  <span className="text-xs text-gray-400">Completed</span>
                </div>
                <div className="text-2xl font-bold text-white mb-1">{stats.resolvedIssues}</div>
                <div className="text-sm text-gray-400">Resolved Issues</div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Top Languages */}
              <div className="bg-dark-800 border border-dark-700 rounded-lg p-6">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center">
                  <Code className="w-5 h-5 mr-2 text-primary-500" />
                  Top Languages Analyzed
                </h2>
                <div className="space-y-4">
                  {stats.topLanguages.map((lang, index) => (
                    <div key={lang.language}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-300">{lang.language}</span>
                        <span className="text-sm text-gray-400">{lang.count} reviews</span>
                      </div>
                      <div className="w-full bg-dark-700 rounded-full h-2">
                        <div
                          className="bg-primary-600 h-2 rounded-full transition-all"
                          style={{ width: `${(lang.count / stats.topLanguages[0].count) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recent Activity */}
              <div className="bg-dark-800 border border-dark-700 rounded-lg p-6">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center">
                  <Activity className="w-5 h-5 mr-2 text-primary-500" />
                  Recent Activity (Last 7 Days)
                </h2>
                <div className="space-y-3">
                  {stats.recentTrends.map((trend) => (
                    <div key={trend.date} className="flex items-center justify-between p-3 bg-dark-700 rounded-lg">
                      <span className="text-sm text-gray-300">
                        {new Date(trend.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                      </span>
                      <div className="flex items-center space-x-2">
                        <div className="flex items-center space-x-1">
                          {Array.from({ length: Math.min(trend.reviews, 5) }).map((_, i) => (
                            <div key={i} className="w-2 h-2 bg-primary-500 rounded-full"></div>
                          ))}
                        </div>
                        <span className="text-sm font-medium text-white">{trend.reviews} reviews</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* AI Recommendations */}
            <div className="mt-6 bg-gradient-to-r from-primary-900/30 to-purple-900/30 border border-primary-700/50 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-white mb-3 flex items-center">
                <Sparkles className="w-5 h-5 mr-2 text-primary-400" />
                AI-Powered Recommendations
              </h2>
              <div className="space-y-2">
                <p className="text-gray-300 text-sm">
                  • Consider focusing on reducing complexity in TypeScript modules - 34% show high cyclomatic complexity
                </p>
                <p className="text-gray-300 text-sm">
                  • Security scans detected 12 critical issues - prioritize authentication and input validation fixes
                </p>
                <p className="text-gray-300 text-sm">
                  • Code quality has improved 15% this week - maintain consistent review practices
                </p>
              </div>
            </div>
          </>
        )}
      </div>
    </Layout>
  );
}
