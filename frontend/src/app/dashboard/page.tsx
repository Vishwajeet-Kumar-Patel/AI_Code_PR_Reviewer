'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import PRCard from '@/components/PRCard';
import { Filter, Plus, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';
import apiClient from '@/lib/api-client';
import type { PullRequest, PRFilter } from '@/types';

export default function Dashboard() {
  const router = useRouter();
  const [pullRequests, setPullRequests] = useState<PullRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [backendConnected, setBackendConnected] = useState(false);
  const [filter, setFilter] = useState<PRFilter>({
    status: 'open',
    sort: 'newest',
  });

  useEffect(() => {
    checkBackendConnection();
    loadPullRequests();
  }, [filter]);

  const checkBackendConnection = async () => {
    try {
      await apiClient.healthCheck();
      setBackendConnected(true);
    } catch (error) {
      setBackendConnected(false);
      console.error('Backend connection failed:', error);
    }
  };

  const loadPullRequests = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.listPullRequests(filter);
      setPullRequests(response.items);
    } catch (error: any) {
      console.error('Failed to load pull requests:', error);
      setError(error.message || 'Failed to load pull requests from GitHub');
    } finally {
      setLoading(false);
    }
  };

  const handlePRClick = (pr: PullRequest) => {
    router.push(`/pr/${pr.repository?.owner}/${pr.repository?.name}/${pr.pr_number}`);
  };

  return (
    <Layout user={{ name: 'Vishwajeet Kumar', avatar_url: '' }}>
      <div className="p-6">
        {/* Page header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white mb-2">Pull Request Analysis Dashboard</h1>
            <p className="text-gray-400">Monitor and analyze pull requests across your repositories</p>
          </div>
          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            {backendConnected ? (
              <>
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span className="text-sm text-green-500">Connected to GitHub</span>
              </>
            ) : (
              <>
                <AlertCircle className="w-5 h-5 text-red-500" />
                <span className="text-sm text-red-500">Backend Disconnected</span>
              </>
            )}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-900/20 border border-red-700 rounded-lg p-4 flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
            <div>
              <p className="text-red-400 font-medium">Error loading pull requests</p>
              <p className="text-red-300 text-sm mt-1">{error}</p>
              <p className="text-gray-400 text-sm mt-2">
                Make sure your GitHub token is valid and you have access to repositories with open PRs.
              </p>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-dark-800 border border-dark-700 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {/* Repository filter */}
              <select
                className="bg-dark-700 border border-dark-600 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary-600"
                onChange={(e) => setFilter({ ...filter, repository: e.target.value })}
              >
                <option value="">All Repos</option>
                <option value="frontend">Frontend</option>
                <option value="backend">Backend</option>
                <option value="ai-toolkit">AI-Tool</option>
              </select>

              {/* Status filter */}
              <select
                className="bg-dark-700 border border-dark-600 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary-600"
                value={filter.status || 'all'}
                onChange={(e) => setFilter({ ...filter, status: e.target.value as any })}
              >
                <option value="all">All Status</option>
                <option value="open">Open</option>
                <option value="closed">Closed</option>
                <option value="merged">Merged</option>
              </select>

              {/* Sort */}
              <select
                className="bg-dark-700 border border-dark-600 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary-600"
                value={filter.sort}
                onChange={(e) => setFilter({ ...filter, sort: e.target.value as any })}
              >
                <option value="newest">Newest</option>
                <option value="oldest">Oldest</option>
                <option value="updated">Recently Updated</option>
              </select>

              <button className="p-2 text-gray-400 hover:text-white hover:bg-dark-700 rounded-lg transition-colors">
                <Filter className="w-5 h-5" />
              </button>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={loadPullRequests}
                className="p-2 text-gray-400 hover:text-white hover:bg-dark-700 rounded-lg transition-colors"
              >
                <RefreshCw className="w-5 h-5" />
              </button>
              <button className="flex items-center space-x-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                <Plus className="w-4 h-4" />
                <span>Analyze PR</span>
              </button>
            </div>
          </div>
        </div>

        {/* Pull Requests list */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">Pull Requests</h2>
            <span className="text-sm text-gray-400">{pullRequests.length} results</span>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-primary-600"></div>
              <p className="mt-4 text-gray-400">Loading pull requests...</p>
            </div>
          ) : pullRequests.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-400">No pull requests found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {pullRequests.map((pr) => (
                <PRCard
                  key={pr.id}
                  pullRequest={pr}
                  review={pr.reviews?.[0]}
                  onClick={() => handlePRClick(pr)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
