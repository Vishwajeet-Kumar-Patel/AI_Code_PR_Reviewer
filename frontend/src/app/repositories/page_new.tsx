'use client';

import { useState, useEffect, useMemo } from 'react';
import Layout from '@/components/Layout';
import { FolderGit2, Star, GitFork, RefreshCw, AlertCircle, ChevronLeft, ChevronRight, Clock } from 'lucide-react';
import apiClient from '@/lib/api-client';
import type { Repository } from '@/types';

export default function Repositories() {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(12);
  const [sortOrder, setSortOrder] = useState<'newest' | 'oldest' | 'name'>('newest');

  useEffect(() => {
    loadRepositories();
  }, []);

  const loadRepositories = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.listRepositories({ max: 100 });
      setRepositories(response.repositories || []);
    } catch (error: any) {
      console.error('Failed to load repositories:', error);
      setError(error.message || 'Failed to load repositories from GitHub');
    } finally {
      setLoading(false);
    }
  };

  // Sort and paginate repositories
  const sortedRepositories = useMemo(() => {
    const sorted = [...repositories].sort((a, b) => {
      if (sortOrder === 'newest') {
        const dateA = new Date((a as any).updated_at || (a as any).created_at || 0).getTime();
        const dateB = new Date((b as any).updated_at || (b as any).created_at || 0).getTime();
        return dateB - dateA; // Newest first
      } else if (sortOrder === 'oldest') {
        const dateA = new Date((a as any).updated_at || (a as any).created_at || 0).getTime();
        const dateB = new Date((b as any).updated_at || (b as any).created_at || 0).getTime();
        return dateA - dateB; // Oldest first
      } else {
        return a.name.localeCompare(b.name); // Alphabetical
      }
    });
    return sorted;
  }, [repositories, sortOrder]);

  const paginatedRepositories = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return sortedRepositories.slice(startIndex, endIndex);
  }, [sortedRepositories, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(sortedRepositories.length / itemsPerPage);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
  };

  return (
    <Layout user={{ name: 'Vishwajeet Kumar', avatar_url: '' }}>
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-white mb-2">Repositories</h1>
              <p className="text-gray-400">
                {repositories.length > 0 
                  ? `${repositories.length} ${repositories.length === 1 ? 'repository' : 'repositories'} found` 
                  : 'Your connected GitHub repositories'}
              </p>
            </div>
            <div className="flex items-center space-x-3">
              {/* Sort dropdown */}
              <select
                value={sortOrder}
                onChange={(e) => {
                  setSortOrder(e.target.value as any);
                  setCurrentPage(1);
                }}
                disabled={loading}
                className="bg-dark-700 border border-dark-600 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary-600 disabled:opacity-50"
              >
                <option value="newest">Most Recent</option>
                <option value="oldest">Oldest First</option>
                <option value="name">Name (A-Z)</option>
              </select>
              {/* Refresh button */}
              <button
                onClick={loadRepositories}
                disabled={loading}
                className="flex items-center space-x-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-900/20 border border-red-700 rounded-lg p-4 flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
            <div>
              <p className="text-red-400 font-medium">Error loading repositories</p>
              <p className="text-red-300 text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <RefreshCw className="w-8 h-8 text-primary-500 animate-spin mx-auto mb-4" />
              <p className="text-gray-400">Loading repositories from GitHub...</p>
            </div>
          </div>
        ) : repositories.length === 0 ? (
          /* Empty State */
          <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
            <div className="w-16 h-16 bg-dark-700 rounded-full flex items-center justify-center mb-4">
              <FolderGit2 className="w-8 h-8 text-gray-400" />
            </div>
            <h2 className="text-xl font-bold text-white mb-2">No Repositories Found</h2>
            <p className="text-gray-400 max-w-md mb-4">
              No repositories were found for your GitHub account. Make sure your GitHub token has the correct permissions.
            </p>
            <button
              onClick={loadRepositories}
              className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
            >
              Try Again
            </button>
          </div>
        ) : (
          <>
            {/* Repository Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {paginatedRepositories.map((repo) => (
                <div
                  key={repo.id}
                  className="bg-dark-800 border border-dark-700 rounded-lg p-5 hover:border-primary-600 transition-all duration-200 cursor-pointer group"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-3 flex-1 min-w-0">
                      <FolderGit2 className="w-5 h-5 text-primary-500 flex-shrink-0" />
                      <div className="min-w-0 flex-1">
                        <h3 className="text-white font-semibold truncate group-hover:text-primary-400 transition-colors">
                          {repo.name}
                        </h3>
                        <p className="text-xs text-gray-400 truncate">{repo.owner}</p>
                      </div>
                    </div>
                    {repo.language && (
                      <span className="px-2 py-1 bg-primary-600/20 text-primary-400 text-xs rounded flex-shrink-0 ml-2">
                        {repo.language}
                      </span>
                    )}
                  </div>

                  {repo.description && (
                    <p className="text-sm text-gray-400 mb-3 line-clamp-2 min-h-[40px]">
                      {repo.description}
                    </p>
                  )}

                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <div className="flex items-center space-x-3">
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
                    </div>
                    {(repo as any).updated_at && (
                      <div className="flex items-center space-x-1 text-gray-500">
                        <Clock className="w-3 h-3" />
                        <span>{formatDate((repo as any).updated_at)}</span>
                      </div>
                    )}
                  </div>

                  {(repo as any).private && (
                    <div className="mt-3 pt-3 border-t border-dark-700">
                      <span className="px-2 py-0.5 bg-yellow-600/20 text-yellow-400 rounded text-xs">
                        Private
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between bg-dark-800 border border-dark-700 rounded-lg p-4">
                <div className="text-sm text-gray-400">
                  Showing <span className="font-semibold text-white">{((currentPage - 1) * itemsPerPage) + 1}</span> to{' '}
                  <span className="font-semibold text-white">{Math.min(currentPage * itemsPerPage, sortedRepositories.length)}</span> of{' '}
                  <span className="font-semibold text-white">{sortedRepositories.length}</span> repositories
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="p-2 text-gray-400 hover:text-white hover:bg-dark-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    aria-label="Previous page"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                  
                  <div className="flex items-center space-x-1">
                    {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                      let pageNum: number;
                      if (totalPages <= 7) {
                        pageNum = i + 1;
                      } else if (currentPage <= 4) {
                        pageNum = i + 1;
                      } else if (currentPage >= totalPages - 3) {
                        pageNum = totalPages - 6 + i;
                      } else {
                        pageNum = currentPage - 3 + i;
                      }
                      
                      return (
                        <button
                          key={pageNum}
                          onClick={() => handlePageChange(pageNum)}
                          className={`min-w-[36px] h-9 px-2 rounded-lg text-sm font-medium transition-colors ${
                            currentPage === pageNum
                              ? 'bg-primary-600 text-white'
                              : 'text-gray-400 hover:text-white hover:bg-dark-700'
                          }`}
                          aria-label={`Page ${pageNum}`}
                          aria-current={currentPage === pageNum ? 'page' : undefined}
                        >
                          {pageNum}
                        </button>
                      );
                    })}
                  </div>

                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    className="p-2 text-gray-400 hover:text-white hover:bg-dark-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    aria-label="Next page"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </Layout>
  );
}
