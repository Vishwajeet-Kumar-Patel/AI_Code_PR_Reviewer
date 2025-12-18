import { AlertTriangle, Info, AlertCircle, Shield } from 'lucide-react';
import clsx from 'clsx';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/cjs/styles/prism';
import type { Issue } from '@/types';

interface IssueCardProps {
  issue: Issue;
  fileName?: string;
}

export default function IssueCard({ issue, fileName }: IssueCardProps) {
  const getIcon = () => {
    switch (issue.type) {
      case 'security':
        return <Shield className="w-4 h-4" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4" />;
      case 'complexity':
        return <AlertCircle className="w-4 h-4" />;
      default:
        return <Info className="w-4 h-4" />;
    }
  };

  const getTypeStyles = () => {
    switch (issue.type) {
      case 'security':
        return 'border-red-500 bg-red-500/10';
      case 'warning':
        return 'border-yellow-500 bg-yellow-500/10';
      case 'complexity':
        return 'border-blue-500 bg-blue-500/10';
      default:
        return 'border-gray-500 bg-gray-500/10';
    }
  };

  const getSeverityBadge = () => {
    const colors: Record<string, string> = {
      critical: 'bg-red-600 text-white',
      high: 'bg-orange-600 text-white',
      medium: 'bg-yellow-600 text-white',
      low: 'bg-blue-600 text-white',
    };
    return colors[issue.severity] || colors.low;
  };

  return (
    <div className={clsx('border-l-4 rounded-lg p-4 mb-4', getTypeStyles())}>
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div className={clsx('p-2 rounded-lg', issue.type === 'security' ? 'bg-red-600' : 'bg-gray-700')}>
            {getIcon()}
          </div>
          <div>
            <h4 className="text-sm font-semibold text-white">{issue.title}</h4>
            {fileName && issue.line_number && (
              <p className="text-xs text-gray-400 mt-1">
                {fileName} • Line {issue.line_number}
              </p>
            )}
          </div>
        </div>
        <span className={clsx('badge px-2 py-1 text-xs font-semibold', getSeverityBadge())}>
          {issue.severity}
        </span>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-300 mb-3">{issue.description}</p>

      {/* Code snippet */}
      {issue.code_snippet && (
        <div className="mb-3 rounded-lg overflow-hidden">
          <SyntaxHighlighter
            language="typescript"
            style={vscDarkPlus}
            customStyle={{
              margin: 0,
              padding: '12px',
              fontSize: '12px',
              backgroundColor: '#1e1e1e',
            }}
          >
            {issue.code_snippet}
          </SyntaxHighlighter>
        </div>
      )}

      {/* Recommendation */}
      <div className="bg-dark-700 rounded-lg p-3">
        <p className="text-xs font-medium text-gray-400 mb-1">Recommended Action:</p>
        <p className="text-sm text-gray-200">{issue.recommendation}</p>
      </div>
    </div>
  );
}
