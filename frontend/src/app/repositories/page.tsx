'use client';

import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { FolderGit2, Star, GitFork, RefreshCw, AlertCircle } from 'lucide-react';
import apiClient from '@/lib/api-client';
import type { Repository } from '@/types';

export default function Repositories() {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadRepositories();
  }, []);

  const loadRepositories = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.listRepositories();
      setRepositories(response.repositories);
    } catch (error: any) {
      console.error('Failed to load repositories:', error);
      setError(error.message || 'Failed to load repositories from GitHub');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout user={{ name: 'Vishwajeet Kumar', avatar_url: '' }}>
      <div className="p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white mb-2">Repositories</h1>
            <p className="text-gray-400">Your connected GitHub repositories</p>
          </div>
          <button
            onClick={loadRepositories}
            disabled={loading}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {error && (
          <div className="mb-6 bg-red-900/20 border border-red-700 rounded-lg p-4 flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
            <div>
              <p className="text-red-400 font-medium">Error loading repositories</p>
              <p className="text-red-300 text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <RefreshCw className="w-8 h-8 text-primary-500 animate-spin mx-auto mb-4" />
              <p className="text-gray-400">Loading repositories from GitHub...</p>
            </div>
          </div>
        ) : repositories.length === 0 ? (
          <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
            <div className="w-16 h-16 bg-dark-700 rounded-full flex items-center justify-center mb-4">
              <FolderGit2 className="w-8 h-8 text-gray-400" />
            </div>
            <h2 className="text-xl font-bold text-white mb-2">No Repositories Found</h2>
            <p className="text-gray-400 max-w-md">
              No repositories were found for your GitHub account. Make sure your GitHub token has the correct permissions.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {repositories.map((repo) => (
              <div
                key={repo.id}
                className="bg-dark-800 border border-dark-700 rounded-lg p-5 hover:border-primary-600 transition-colors cursor-pointer"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <FolderGit2 className="w-5 h-5 text-primary-500" />
                    <div>
                      <h3 className="text-white font-semibold">{repo.name}</h3>
                      <p className="text-xs text-gray-400">{repo.owner}</p>
                    </div>
                  </div>
                  {repo.language && (
                    <span className="px-2 py-1 bg-primary-600/20 text-primary-400 text-xs rounded">
                      {repo.language}
                    </span>
                  )}
                </div>

                {repo.description && (
                  <p className="text-sm text-gray-400 mb-3 line-clamp-2">
                    {repo.description}
                  </p>
                )}

                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  {typeof (repo as any).stars === 'number' && (
                    <div className="flex items-center space-x-1">
                      <Star className="w-3 h-3" />
                      <span>{(repo as any).stars}</span>
                    </div>
                  )}
                  {typeof (repo as any).forks === 'number' && (
                    <div className="flex items-center space-x-1">
                      <GitFork className="w-3 h-3" />
                      <span>{(repo as any).forks}</span>
                    </div>
                  )}
                  {(repo as any).private && (
                    <span className="px-2 py-0.5 bg-yellow-600/20 text-yellow-400 rounded">
                      Private
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
