'use client';

import { useState } from 'react';
import {
  Wand2,
  GitPullRequest,
  FileCode,
  BookOpen,
  Zap,
  CheckCircle,
  XCircle,
  AlertCircle,
  Loader2,
  Copy,
  Check,
  Code2
} from 'lucide-react';
import { codeFixesAPI, type CodeFix } from '@/lib/api/advanced-features';

export default function CodeFixesPage() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [fixes, setFixes] = useState<CodeFix[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [selectedFix, setSelectedFix] = useState<number | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [isCreatingPR, setIsCreatingPR] = useState(false);
  const [prResult, setPrResult] = useState<any>(null);

  // Repository info for PR creation
  const [repoInfo, setRepoInfo] = useState({
    repository: '',
    branch: 'main',
  });

  const languages = [
    { value: 'python', label: 'Python' },
    { value: 'javascript', label: 'JavaScript' },
    { value: 'typescript', label: 'TypeScript' },
    { value: 'java', label: 'Java' },
    { value: 'go', label: 'Go' },
    { value: 'rust', label: 'Rust' },
  ];

  const handleAnalyze = async () => {
    if (!code.trim()) return;

    setIsAnalyzing(true);
    setFixes([]);
    setSummary(null);
    setSelectedFix(null);

    try {
      const result = await codeFixesAPI.generateFixes({
        code,
        language,
        context: {
          file_path: 'code_analysis.py',
        },
      });
      setFixes(result.fixes);
      setSummary(result.summary);
    } catch (error: any) {
      console.error('Analysis failed:', error);
      const errorMessage = typeof error.response?.data?.detail === 'string' 
        ? error.response.data.detail 
        : error.response?.data?.detail 
          ? JSON.stringify(error.response.data.detail)
          : error.message || 'Analysis failed';
      setSummary({
        error: errorMessage,
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleCopyCode = (fixedCode: string, index: number) => {
    navigator.clipboard.writeText(fixedCode);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const handleCreatePR = async () => {
    if (!repoInfo.repository || fixes.length === 0) return;

    setIsCreatingPR(true);
    setPrResult(null);

    try {
      const result = await codeFixesAPI.createFixPR({
        repository: repoInfo.repository,
        branch: repoInfo.branch,
        fixes: fixes,
        title: `Automated Code Fixes - ${fixes.length} issues`,
        description: `AI-powered automated fixes for code quality improvements.\n\nFixed ${summary?.critical_fixes || 0} critical issues.`,
      });
      setPrResult(result);
    } catch (error: any) {
      const errorMessage = typeof error.response?.data?.detail === 'string'
        ? error.response.data.detail
        : error.response?.data?.detail
          ? JSON.stringify(error.response.data.detail)
          : error.message || 'PR creation failed';
      setPrResult({
        success: false,
        error: errorMessage,
      });
    } finally {
      setIsCreatingPR(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300 border-red-200 dark:border-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300 border-orange-200 dark:border-orange-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300 border-yellow-200 dark:border-yellow-800';
      case 'low':
        return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 border-blue-200 dark:border-blue-800';
      default:
        return 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300 border-gray-200 dark:border-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-indigo-50 dark:from-gray-900 dark:to-indigo-900/20">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-lg">
              <Wand2 className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
                AI-Powered Code Fixes
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Automated code improvements and PR generation
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Input Section */}
          <div className="lg:col-span-2 space-y-6">
            {/* Code Input Card */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                  <Code2 className="w-5 h-5 mr-2 text-indigo-600" />
                  Your Code
                </h2>
              </div>

              <div className="p-6 space-y-4">
                {/* Language Selector */}
                <div className="flex flex-wrap gap-2">
                  {languages.map((lang) => (
                    <button
                      key={lang.value}
                      onClick={() => setLanguage(lang.value)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                        language === lang.value
                          ? 'bg-indigo-600 text-white shadow-md'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                      }`}
                    >
                      {lang.label}
                    </button>
                  ))}
                </div>

                {/* Code Textarea */}
                <div>
                  <textarea
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    placeholder={`Paste your ${language} code here...\n\nExample:\ndef calculate_sum(a, b):\n    result = a + b\n    return result`}
                    className="w-full h-80 px-4 py-3 bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-mono text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                  />
                </div>

                {/* Analyze Button */}
                <button
                  onClick={handleAnalyze}
                  disabled={!code.trim() || isAnalyzing}
                  className="w-full flex items-center justify-center space-x-2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-lg font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Analyzing Code...</span>
                    </>
                  ) : (
                    <>
                      <Wand2 className="w-5 h-5" />
                      <span>Analyze & Generate Fixes</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Fixes Results */}
            {fixes.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between">
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                      <CheckCircle className="w-5 h-5 mr-2 text-green-600" />
                      Generated Fixes ({fixes.length})
                    </h2>
                    {summary && (
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {summary.critical_fixes} critical • {summary.estimated_time_saved} saved
                      </span>
                    )}
                  </div>
                </div>

                <div className="p-6 space-y-4">
                  {fixes.map((fix, index) => (
                    <div
                      key={index}
                      className={`border-2 rounded-lg overflow-hidden transition-all ${
                        selectedFix === index
                          ? 'border-indigo-500 shadow-lg'
                          : 'border-gray-200 dark:border-gray-700'
                      }`}
                    >
                      {/* Fix Header */}
                      <button
                        onClick={() => setSelectedFix(selectedFix === index ? null : index)}
                        className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-left"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                              <span className={`px-2 py-1 rounded text-xs font-medium border ${getSeverityColor(fix.severity)}`}>
                                {fix.severity}
                              </span>
                              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                                {fix.issue_type}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {fix.description}
                            </p>
                          </div>
                          <div className="ml-4 text-sm font-semibold text-indigo-600 dark:text-indigo-400">
                            {(fix.confidence * 100).toFixed(0)}% confident
                          </div>
                        </div>
                      </button>

                      {/* Fix Details (Expanded) */}
                      {selectedFix === index && (
                        <div className="p-4 space-y-4 bg-white dark:bg-gray-800">
                          {/* Original Code */}
                          <div>
                            <div className="flex items-center justify-between mb-2">
                              <label className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">
                                Original Code
                              </label>
                              <XCircle className="w-4 h-4 text-red-500" />
                            </div>
                            <pre className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded text-xs font-mono text-gray-900 dark:text-gray-100 overflow-x-auto">
                              {fix.original_code}
                            </pre>
                          </div>

                          {/* Fixed Code */}
                          <div>
                            <div className="flex items-center justify-between mb-2">
                              <label className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">
                                Fixed Code
                              </label>
                              <div className="flex items-center space-x-2">
                                <CheckCircle className="w-4 h-4 text-green-500" />
                                <button
                                  onClick={() => handleCopyCode(fix.fixed_code, index)}
                                  className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                                  title="Copy code"
                                >
                                  {copiedIndex === index ? (
                                    <Check className="w-4 h-4 text-green-500" />
                                  ) : (
                                    <Copy className="w-4 h-4 text-gray-500" />
                                  )}
                                </button>
                              </div>
                            </div>
                            <pre className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded text-xs font-mono text-gray-900 dark:text-gray-100 overflow-x-auto">
                              {fix.fixed_code}
                            </pre>
                          </div>

                          {/* Explanation */}
                          <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded">
                            <p className="text-sm text-blue-900 dark:text-blue-100">
                              <strong>Explanation:</strong> {fix.explanation}
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Error Display */}
            {summary?.error && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-red-200 dark:border-red-800 overflow-hidden">
                <div className="p-6">
                  <div className="flex items-start space-x-3">
                    <AlertCircle className="w-6 h-6 text-red-500 mt-0.5" />
                    <div>
                      <h3 className="font-semibold text-red-900 dark:text-red-100 mb-1">
                        Analysis Failed
                      </h3>
                      <p className="text-sm text-red-700 dark:text-red-300">
                        {summary.error}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Sidebar - Actions & PR */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Quick Actions
                </h2>
              </div>

              <div className="p-6 space-y-3">
                <button className="w-full flex items-center space-x-3 px-4 py-3 bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-lg transition-colors text-left">
                  <FileCode className="w-5 h-5" />
                  <div>
                    <div className="font-medium text-sm">Generate Tests</div>
                    <div className="text-xs opacity-75">Create test cases</div>
                  </div>
                </button>

                <button className="w-full flex items-center space-x-3 px-4 py-3 bg-green-50 dark:bg-green-900/20 hover:bg-green-100 dark:hover:bg-green-900/30 text-green-700 dark:text-green-300 rounded-lg transition-colors text-left">
                  <BookOpen className="w-5 h-5" />
                  <div>
                    <div className="font-medium text-sm">Generate Docs</div>
                    <div className="text-xs opacity-75">Auto-document code</div>
                  </div>
                </button>

                <button className="w-full flex items-center space-x-3 px-4 py-3 bg-yellow-50 dark:bg-yellow-900/20 hover:bg-yellow-100 dark:hover:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 rounded-lg transition-colors text-left">
                  <Zap className="w-5 h-5" />
                  <div>
                    <div className="font-medium text-sm">Quick Fix</div>
                    <div className="text-xs opacity-75">Single issue fix</div>
                  </div>
                </button>
              </div>
            </div>

            {/* PR Creation */}
            {fixes.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                    <GitPullRequest className="w-5 h-5 mr-2 text-purple-600" />
                    Create Pull Request
                  </h2>
                </div>

                <div className="p-6 space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Repository
                    </label>
                    <input
                      type="text"
                      value={repoInfo.repository}
                      onChange={(e) => setRepoInfo({ ...repoInfo, repository: e.target.value })}
                      placeholder="owner/repo"
                      className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Branch
                    </label>
                    <input
                      type="text"
                      value={repoInfo.branch}
                      onChange={(e) => setRepoInfo({ ...repoInfo, branch: e.target.value })}
                      placeholder="main"
                      className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>

                  <button
                    onClick={handleCreatePR}
                    disabled={!repoInfo.repository || isCreatingPR}
                    className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
                  >
                    {isCreatingPR ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Creating PR...</span>
                      </>
                    ) : (
                      <>
                        <GitPullRequest className="w-5 h-5" />
                        <span>Create PR</span>
                      </>
                    )}
                  </button>

                  {/* PR Result */}
                  {prResult && (
                    <div className={`p-4 rounded-lg ${
                      prResult.success
                        ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
                        : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
                    }`}>
                      <div className="flex items-start space-x-2">
                        {prResult.success ? (
                          <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5" />
                        ) : (
                          <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5" />
                        )}
                        <div className="flex-1">
                          <p className={`text-sm font-medium ${
                            prResult.success
                              ? 'text-green-900 dark:text-green-100'
                              : 'text-red-900 dark:text-red-100'
                          }`}>
                            {prResult.success ? 'PR Created Successfully!' : 'PR Creation Failed'}
                          </p>
                          {prResult.pr_url && (
                            <a
                              href={prResult.pr_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-green-700 dark:text-green-300 hover:underline mt-1 block"
                            >
                              View PR →
                            </a>
                          )}
                          {prResult.error && (
                            <p className="text-xs text-red-700 dark:text-red-300 mt-1">
                              {prResult.error}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Stats */}
            <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
              <h3 className="font-semibold mb-4">Code Fix Benefits</h3>
              <div className="space-y-3 text-sm">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4" />
                  <span>Instant code improvements</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4" />
                  <span>Auto-generate PRs</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4" />
                  <span>Best practice enforcement</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4" />
                  <span>90% faster than manual</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
