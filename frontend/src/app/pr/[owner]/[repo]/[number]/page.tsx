'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Layout from '@/components/Layout';
import IssueCard from '@/components/IssueCard';
import { GitPullRequest, Clock, User, FileCode, ArrowLeft } from 'lucide-react';
import { format } from 'date-fns';
import Link from 'next/link';
import apiClient from '@/lib/api-client';
import type { PullRequest, Review, FileAnalysis } from '@/types';
import clsx from 'clsx';

export default function PRDetailPage() {
  const params = useParams();
  const { owner, repo, number } = params;
  
  const [pullRequest, setPullRequest] = useState<PullRequest | null>(null);
  const [review, setReview] = useState<Review | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState<'feedback' | 'diff' | 'files'>('feedback');
  const [selectedFile, setSelectedFile] = useState<FileAnalysis | null>(null);

  useEffect(() => {
    loadData();
  }, [owner, repo, number]);

  const loadData = async () => {
    try {
      setLoading(true);
      const pr = await apiClient.getPullRequest(owner as string, repo as string, Number(number));
      setPullRequest(pr);
      
      if (pr.reviews && pr.reviews.length > 0) {
        const latestReview = pr.reviews[0];
        const fullReview = await apiClient.getReview(latestReview.id);
        setReview(fullReview);
        if (fullReview.file_analyses && fullReview.file_analyses.length > 0) {
          setSelectedFile(fullReview.file_analyses[0]);
        }
      }
    } catch (error) {
      console.error('Failed to load PR details:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-primary-600"></div>
            <p className="mt-4 text-gray-400">Loading PR analysis...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!pullRequest || !review) {
    return (
      <Layout>
        <div className="p-6">
          <p className="text-gray-400">Pull request not found</p>
        </div>
      </Layout>
    );
  }

  const allIssues = [
    ...(review.security_issues || []),
    ...(review.complexity_issues || []),
  ];

  return (
    <Layout user={{ name: 'Vishwajeet Kumar' }}>
      <div className="p-6">
        {/* Back button */}
        <Link
          href="/dashboard"
          className="inline-flex items-center space-x-2 text-sm text-gray-400 hover:text-white mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </Link>

        {/* PR Header */}
        <div className="bg-dark-800 border border-dark-700 rounded-lg p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <GitPullRequest className="w-6 h-6 text-primary-600" />
                <h1 className="text-2xl font-bold text-white">{pullRequest.title}</h1>
                <span className="text-gray-500">#{pullRequest.pr_number}</span>
              </div>
              <p className="text-gray-400">{pullRequest.repository?.full_name}</p>
            </div>
            <span className={clsx('badge', pullRequest.state === 'open' ? 'badge-success' : 'badge-info')}>
              {pullRequest.state}
            </span>
          </div>

          <div className="flex items-center space-x-6 text-sm text-gray-400">
            <div className="flex items-center space-x-2">
              <User className="w-4 h-4" />
              <span>{pullRequest.author}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4" />
              <span>{format(new Date(pullRequest.created_at), 'MMM d, yyyy HH:mm')}</span>
            </div>
            <div>
              <span className="text-gray-500">{pullRequest.base_branch}</span>
              <span className="mx-2">←</span>
              <span className="text-white">{pullRequest.head_branch}</span>
            </div>
          </div>
        </div>

        {/* Scores */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-dark-800 border border-dark-700 rounded-lg p-4">
            <p className="text-sm text-gray-400 mb-2">Quality Score</p>
            <p className={clsx('text-3xl font-bold', review.quality_score && review.quality_score >= 70 ? 'text-green-500' : 'text-yellow-500')}>
              {review.quality_score?.toFixed(0) || 'N/A'}
            </p>
          </div>
          <div className="bg-dark-800 border border-dark-700 rounded-lg p-4">
            <p className="text-sm text-gray-400 mb-2">Security Score</p>
            <p className={clsx('text-3xl font-bold', review.security_score && review.security_score >= 70 ? 'text-green-500' : 'text-red-500')}>
              {review.security_score?.toFixed(0) || 'N/A'}
            </p>
          </div>
          <div className="bg-dark-800 border border-dark-700 rounded-lg p-4">
            <p className="text-sm text-gray-400 mb-2">Complexity Score</p>
            <p className={clsx('text-3xl font-bold', review.complexity_score && review.complexity_score >= 70 ? 'text-green-500' : 'text-yellow-500')}>
              {review.complexity_score?.toFixed(0) || 'N/A'}
            </p>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-dark-800 border border-dark-700 rounded-lg">
          <div className="border-b border-dark-700 flex">
            <button
              onClick={() => setSelectedTab('feedback')}
              className={clsx(
                'px-6 py-3 text-sm font-medium transition-colors',
                selectedTab === 'feedback'
                  ? 'text-white border-b-2 border-primary-600'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              Feedback
            </button>
            <button
              onClick={() => setSelectedTab('diff')}
              className={clsx(
                'px-6 py-3 text-sm font-medium transition-colors',
                selectedTab === 'diff'
                  ? 'text-white border-b-2 border-primary-600'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              Diff
            </button>
            <button
              onClick={() => setSelectedTab('files')}
              className={clsx(
                'px-6 py-3 text-sm font-medium transition-colors',
                selectedTab === 'files'
                  ? 'text-white border-b-2 border-primary-600'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              Files Changed ({review.file_analyses?.length || 0})
            </button>
            <div className="ml-auto px-6 py-3 text-sm text-gray-400 flex items-center space-x-2">
              <span>Review Summary</span>
              <button className="text-primary-600 hover:text-primary-500">→</button>
            </div>
          </div>

          <div className="p-6">
            {selectedTab === 'feedback' && (
              <div>
                <h3 className="text-lg font-semibold text-white mb-4">
                  Review Issues ({allIssues.length})
                </h3>
                {allIssues.length === 0 ? (
                  <p className="text-gray-400">No issues found</p>
                ) : (
                  <div>
                    {allIssues.map((issue, index) => (
                      <IssueCard
                        key={index}
                        issue={issue}
                        fileName={selectedFile?.file_path}
                      />
                    ))}
                  </div>
                )}
              </div>
            )}

            {selectedTab === 'files' && (
              <div>
                <h3 className="text-lg font-semibold text-white mb-4">Changed Files</h3>
                <div className="space-y-2">
                  {review.file_analyses?.map((file, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedFile(file)}
                      className={clsx(
                        'w-full flex items-center space-x-3 p-3 rounded-lg transition-colors text-left',
                        selectedFile?.file_path === file.file_path
                          ? 'bg-primary-600 text-white'
                          : 'bg-dark-700 text-gray-300 hover:bg-dark-600'
                      )}
                    >
                      <FileCode className="w-4 h-4" />
                      <span className="text-sm">{file.file_path}</span>
                      <span className="ml-auto text-xs">{file.issues.length} issues</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {selectedTab === 'diff' && (
              <div>
                <p className="text-gray-400">Diff view coming soon...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
