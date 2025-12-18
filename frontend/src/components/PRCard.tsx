import { format } from 'date-fns';
import { GitPullRequest, User, Clock, Tag } from 'lucide-react';
import clsx from 'clsx';
import type { PullRequest, Review } from '@/types';

interface PRCardProps {
  pullRequest: PullRequest;
  review?: Review;
  onClick?: () => void;
}

export default function PRCard({ pullRequest, review, onClick }: PRCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'closed':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'merged':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const getScoreColor = (score?: number) => {
    if (!score) return 'text-gray-400';
    if (score >= 80) return 'text-green-500';
    if (score >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div
      onClick={onClick}
      className="bg-dark-800 border border-dark-700 rounded-lg p-4 hover:border-primary-600 cursor-pointer transition-all"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-1">
            <GitPullRequest className="w-4 h-4 text-gray-400" />
            <h3 className="text-sm font-semibold text-white">
              {pullRequest.title}
            </h3>
            <span className="text-xs text-gray-500">#{pullRequest.pr_number}</span>
          </div>
          <p className="text-xs text-gray-400">{pullRequest.repository?.full_name}</p>
        </div>
        <span className={clsx('badge', getStatusColor(pullRequest.state))}>
          {pullRequest.state}
        </span>
      </div>

      {/* Author and metadata */}
      <div className="flex items-center space-x-4 text-xs text-gray-400 mb-3">
        <div className="flex items-center space-x-1">
          <User className="w-3 h-3" />
          <span>{pullRequest.author}</span>
        </div>
        <div className="flex items-center space-x-1">
          <Clock className="w-3 h-3" />
          <span>{format(new Date(pullRequest.created_at), 'MMM d, yyyy')}</span>
        </div>
        {pullRequest.repository?.language && (
          <div className="flex items-center space-x-1">
            <Tag className="w-3 h-3" />
            <span>{pullRequest.repository.language}</span>
          </div>
        )}
      </div>

      {/* Review scores */}
      {review && (
        <div className="flex items-center space-x-4 pt-3 border-t border-dark-700">
          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-400">Quality:</span>
            <span className={clsx('text-sm font-semibold', getScoreColor(review.quality_score))}>
              {review.quality_score?.toFixed(0) || 'N/A'}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-400">Security:</span>
            <span className={clsx('text-sm font-semibold', getScoreColor(review.security_score))}>
              {review.security_score?.toFixed(0) || 'N/A'}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-400">Complexity:</span>
            <span className={clsx('text-sm font-semibold', getScoreColor(review.complexity_score))}>
              {review.complexity_score?.toFixed(0) || 'N/A'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
