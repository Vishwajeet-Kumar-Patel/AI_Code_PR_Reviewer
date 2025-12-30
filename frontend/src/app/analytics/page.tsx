'use client';

import { useState } from 'react';
import {
  BarChart,
  TrendingUp,
  Users,
  Target,
  AlertTriangle,
  Sparkles,
  Calendar,
  Activity,
  Award,
  Loader2,
  ArrowUp,
  ArrowDown
} from 'lucide-react';
import useSWR from 'swr';
import { analyticsAPI } from '@/lib/api/advanced-features';

export default function AnalyticsPage() {
  const [selectedPeriod, setSelectedPeriod] = useState('30d');
  const [selectedDev, setSelectedDev] = useState('');

  // Fetch analytics data
  const { data: productivity, isLoading: loadingProductivity } = useSWR(
    ['productivity', selectedPeriod],
    () => analyticsAPI.getProductivity({ time_period: selectedPeriod })
  );

  const { data: codeQuality, isLoading: loadingQuality } = useSWR(
    ['code-quality', selectedPeriod],
    () => analyticsAPI.getCodeQuality({ time_period: selectedPeriod })
  );

  const { data: techDebt, isLoading: loadingDebt } = useSWR(
    'technical-debt',
    () => analyticsAPI.getTechnicalDebt()
  );

  const { data: predictive } = useSWR(
    'predictive',
    () => analyticsAPI.getPredictive()
  );

  const periods = [
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' },
    { value: '90d', label: '90 Days' },
    { value: '1y', label: '1 Year' },
  ];

  const getTrendIcon = (trend: string) => {
    if (trend === 'improving' || trend === 'up') {
      return <ArrowUp className="w-4 h-4 text-green-500" />;
    } else if (trend === 'declining' || trend === 'down') {
      return <ArrowDown className="w-4 h-4 text-red-500" />;
    }
    return null;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-900 dark:to-blue-900/20">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-xl shadow-lg">
                <BarChart className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
                  Advanced Analytics
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Comprehensive insights and metrics
                </p>
              </div>
            </div>

            {/* Period Selector */}
            <div className="flex items-center space-x-2 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
              {periods.map((period) => (
                <button
                  key={period.value}
                  onClick={() => setSelectedPeriod(period.value)}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                    selectedPeriod === period.value
                      ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
                      : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  {period.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Average Review Time */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <Activity className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              {productivity && getTrendIcon(productivity.trends.review_time_trend)}
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              {loadingProductivity ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                `${productivity?.average_review_time || 0}h`
              )}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Avg Review Time
            </div>
          </div>

          {/* PR Merge Rate */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <Target className="w-5 h-5 text-green-600 dark:text-green-400" />
              </div>
              {productivity && getTrendIcon(productivity.trends.merge_rate_trend)}
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              {loadingProductivity ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                `${((productivity?.pr_merge_rate || 0) * 100).toFixed(1)}%`
              )}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              PR Merge Rate
            </div>
          </div>

          {/* Technical Debt */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="p-2 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
                <AlertTriangle className="w-5 h-5 text-orange-600 dark:text-orange-400" />
              </div>
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              {loadingDebt ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                `${techDebt?.total_debt_hours || 0}h`
              )}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Technical Debt
            </div>
          </div>

          {/* Code Coverage */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                <Award className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              {loadingQuality ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                `${((codeQuality?.quality_metrics.code_coverage || 0) * 100).toFixed(1)}%`
              )}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Code Coverage
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Team Productivity */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                <Users className="w-5 h-5 mr-2 text-blue-600" />
                Team Productivity
              </h2>
            </div>
            <div className="p-6">
              {loadingProductivity ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 rounded-lg">
                      <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                        Reviews Completed
                      </div>
                      <div className="text-2xl font-bold text-gray-900 dark:text-white">
                        {productivity?.reviews_completed || 0}
                      </div>
                    </div>
                    <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg">
                      <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                        Avg PR Size
                      </div>
                      <div className="text-2xl font-bold text-gray-900 dark:text-white">
                        {productivity?.average_pr_size || 0}
                      </div>
                    </div>
                  </div>

                  {/* Top Performers */}
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                      Top Performers
                    </h3>
                    <div className="space-y-2">
                      {productivity?.top_performers?.slice(0, 3).map((performer, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg"
                        >
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                              {idx + 1}
                            </div>
                            <div>
                              <div className="font-medium text-gray-900 dark:text-white text-sm">
                                {performer.developer}
                              </div>
                              <div className="text-xs text-gray-500 dark:text-gray-400">
                                {performer.reviews_completed} reviews
                              </div>
                            </div>
                          </div>
                          <div className="text-sm font-semibold text-blue-600 dark:text-blue-400">
                            {performer.avg_review_time}h
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Code Quality Trends */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
                Code Quality Metrics
              </h2>
            </div>
            <div className="p-6">
              {loadingQuality ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Quality Metrics Grid */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                        Complexity
                      </div>
                      <div className="text-lg font-bold text-gray-900 dark:text-white">
                        {codeQuality?.quality_metrics.average_complexity.toFixed(1) || 0}
                      </div>
                    </div>
                    <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                      <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                        Bug Density
                      </div>
                      <div className="text-lg font-bold text-gray-900 dark:text-white">
                        {codeQuality?.quality_metrics.bug_density.toFixed(2) || 0}
                      </div>
                    </div>
                    <div className="p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                      <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                        Tech Debt
                      </div>
                      <div className="text-lg font-bold text-gray-900 dark:text-white">
                        {((codeQuality?.quality_metrics.technical_debt_ratio || 0) * 100).toFixed(0)}%
                      </div>
                    </div>
                    <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                        Coverage
                      </div>
                      <div className="text-lg font-bold text-gray-900 dark:text-white">
                        {((codeQuality?.quality_metrics.code_coverage || 0) * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>

                  {/* Quality Gates */}
                  <div className="p-4 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-lg">
                    <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                      Quality Gates Status
                    </h3>
                    <div className="flex items-center justify-around">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                          {codeQuality?.quality_gates.passed || 0}
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">Passed</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                          {codeQuality?.quality_gates.warnings || 0}
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">Warnings</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                          {codeQuality?.quality_gates.failed || 0}
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">Failed</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Technical Debt & Predictive Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Technical Debt Details */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                <AlertTriangle className="w-5 h-5 mr-2 text-orange-600" />
                Technical Debt Analysis
              </h2>
            </div>
            <div className="p-6">
              {loadingDebt ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Debt by Category */}
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                      Debt by Category
                    </h3>
                    <div className="space-y-2">
                      {techDebt?.debt_by_category &&
                        Object.entries(techDebt.debt_by_category).map(([category, hours]) => (
                          <div key={category} className="flex items-center justify-between">
                            <span className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                              {category.replace('_', ' ')}
                            </span>
                            <div className="flex items-center space-x-2">
                              <div className="w-32 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-gradient-to-r from-orange-500 to-red-500"
                                  style={{
                                    width: `${Math.min((Number(hours) / (techDebt.total_debt_hours || 1)) * 100, 100)}%`,
                                  }}
                                />
                              </div>
                              <span className="text-sm font-semibold text-gray-900 dark:text-white w-12 text-right">
                                {hours}h
                              </span>
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>

                  {/* ROI Analysis */}
                  {techDebt?.roi_analysis && (
                    <div className="p-4 bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 rounded-lg">
                      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                        ROI Analysis
                      </h3>
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <div className="text-gray-600 dark:text-gray-400">Est. Cost</div>
                          <div className="font-bold text-gray-900 dark:text-white">
                            ${techDebt.roi_analysis.estimated_cost.toLocaleString()}
                          </div>
                        </div>
                        <div>
                          <div className="text-gray-600 dark:text-gray-400">Savings</div>
                          <div className="font-bold text-green-600 dark:text-green-400">
                            ${techDebt.roi_analysis.potential_savings.toLocaleString()}
                          </div>
                        </div>
                      </div>
                      <div className="mt-2 pt-2 border-t border-orange-200 dark:border-orange-800">
                        <div className="text-gray-600 dark:text-gray-400 text-xs">Payback Period</div>
                        <div className="font-bold text-gray-900 dark:text-white">
                          {techDebt.roi_analysis.payback_period}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Predictive Analytics */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                <Sparkles className="w-5 h-5 mr-2 text-purple-600" />
                Predictive Insights
              </h2>
            </div>
            <div className="p-6">
              {predictive ? (
                <div className="space-y-4">
                  {/* Predictions */}
                  <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg">
                    <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                      Next Month Forecast
                    </h3>
                    <div className="text-3xl font-bold text-purple-600 dark:text-purple-400 mb-2">
                      {predictive.predictions.next_month_reviews} reviews
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      Risk Score: {predictive.predictions.risk_score}/10
                    </div>
                  </div>

                  {/* Bottlenecks */}
                  {predictive.predictions.predicted_bottlenecks.length > 0 && (
                    <div>
                      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                        Predicted Bottlenecks
                      </h3>
                      <div className="space-y-2">
                        {predictive.predictions.predicted_bottlenecks.map((bottleneck, idx) => (
                          <div
                            key={idx}
                            className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-900 dark:text-red-100"
                          >
                            {bottleneck}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Recommendations */}
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                      AI Recommendations
                    </h3>
                    <div className="space-y-2">
                      {predictive.recommendations.slice(0, 3).map((rec, idx) => (
                        <div
                          key={idx}
                          className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg"
                        >
                          <div className="flex items-start space-x-2">
                            <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                              rec.priority === 'high'
                                ? 'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300'
                                : rec.priority === 'medium'
                                ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/50 dark:text-yellow-300'
                                : 'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300'
                            }`}>
                              {rec.priority}
                            </span>
                            <div className="flex-1">
                              <p className="text-sm text-gray-900 dark:text-white font-medium">
                                {rec.action}
                              </p>
                              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                                {rec.impact}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* ML Insights */}
                  <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-600 dark:text-gray-400">ML Confidence</span>
                      <span className="font-semibold text-gray-900 dark:text-white">
                        {((predictive.ml_insights.confidence || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center py-12">
                  <div className="text-center text-gray-500 dark:text-gray-400">
                    <Sparkles className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p className="text-sm">No predictive data available</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
