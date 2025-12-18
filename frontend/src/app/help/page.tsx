'use client';

import { useState } from 'react';
import Layout from '@/components/Layout';
import { HelpCircle, Book, Github, Terminal, Zap, Shield, Search } from 'lucide-react';

const sections = [
  {
    title: 'Getting Started',
    icon: Zap,
    items: [
      { q: 'How do I connect my GitHub repository?', a: 'Go to Settings, enter your GitHub Personal Access Token with repo permissions, and save. Then navigate to Repositories to see your repos.' },
      { q: 'How do I analyze a pull request?', a: 'Navigate to Dashboard, find the PR you want to analyze, and click on it. Then click "Analyze PR" to start the AI-powered review.' },
      { q: 'What permissions does the GitHub token need?', a: 'Your token needs: repo (full access), read:org, and read:user scopes to function properly.' },
    ],
  },
  {
    title: 'Features',
    icon: Shield,
    items: [
      { q: 'What does the security scan detect?', a: 'Our AI scans for SQL injection, XSS vulnerabilities, insecure dependencies, exposed secrets, authentication issues, and more.' },
      { q: 'How is code complexity measured?', a: 'We calculate cyclomatic complexity, cognitive complexity, and maintainability index to assess code quality.' },
      { q: 'Can I customize analysis settings?', a: 'Yes! Go to Settings to enable/disable security scanning, complexity analysis, and automatic reviews.' },
    ],
  },
  {
    title: 'Troubleshooting',
    icon: Terminal,
    items: [
      { q: 'Why am I not seeing any pull requests?', a: 'Ensure your GitHub token is valid and you have access to repositories with open PRs. Check the connection status on Dashboard.' },
      { q: 'The AI analysis is taking too long', a: 'Large PRs with many files may take several minutes. The system analyzes code, runs security scans, and generates detailed insights.' },
      { q: 'How do I update my API keys?', a: 'Navigate to Settings and update your GitHub token or OpenAI API key. Changes take effect immediately.' },
    ],
  },
];

export default function Help() {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedItem, setExpandedItem] = useState<string | null>(null);

  const filteredSections = sections.map(section => ({
    ...section,
    items: section.items.filter(item =>
      item.q.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.a.toLowerCase().includes(searchQuery.toLowerCase())
    ),
  })).filter(section => section.items.length > 0);

  return (
    <Layout user={{ name: 'Vishwajeet Kumar', avatar_url: '' }}>
      <div className="p-6 max-w-5xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white mb-2">Help & Documentation</h1>
          <p className="text-gray-400">Find answers and learn how to use the AI Code Review System</p>
        </div>

        {/* Search Bar */}
        <div className="mb-8">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search for help..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-600"
            />
          </div>
        </div>

        {/* Quick Links */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-dark-800 border border-dark-700 rounded-lg p-5 hover:border-primary-600 transition-colors"
          >
            <Github className="w-8 h-8 text-primary-500 mb-3" />
            <h3 className="text-white font-semibold mb-1">GitHub Docs</h3>
            <p className="text-sm text-gray-400">Learn about GitHub integration</p>
          </a>
          <a
            href="https://platform.openai.com/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-dark-800 border border-dark-700 rounded-lg p-5 hover:border-primary-600 transition-colors"
          >
            <Book className="w-8 h-8 text-primary-500 mb-3" />
            <h3 className="text-white font-semibold mb-1">API Documentation</h3>
            <p className="text-sm text-gray-400">View API references</p>
          </a>
          <div className="bg-dark-800 border border-dark-700 rounded-lg p-5">
            <HelpCircle className="w-8 h-8 text-primary-500 mb-3" />
            <h3 className="text-white font-semibold mb-1">Support</h3>
            <p className="text-sm text-gray-400">Contact: support@aicodereview.com</p>
          </div>
        </div>

        {/* FAQ Sections */}
        <div className="space-y-6">
          {filteredSections.map((section) => (
            <div key={section.title} className="bg-dark-800 border border-dark-700 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center">
                <section.icon className="w-5 h-5 mr-2 text-primary-500" />
                {section.title}
              </h2>
              <div className="space-y-3">
                {section.items.map((item, index) => (
                  <div key={index} className="border-b border-dark-700 last:border-0 pb-3 last:pb-0">
                    <button
                      onClick={() => setExpandedItem(expandedItem === `${section.title}-${index}` ? null : `${section.title}-${index}`)}
                      className="w-full text-left flex items-center justify-between py-2 text-gray-300 hover:text-white transition-colors"
                    >
                      <span className="font-medium">{item.q}</span>
                      <span className="text-2xl">{expandedItem === `${section.title}-${index}` ? '−' : '+'}</span>
                    </button>
                    {expandedItem === `${section.title}-${index}` && (
                      <div className="mt-2 text-sm text-gray-400 leading-relaxed">
                        {item.a}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {filteredSections.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-400">No results found for "{searchQuery}"</p>
            <button
              onClick={() => setSearchQuery('')}
              className="mt-4 text-primary-500 hover:text-primary-400"
            >
              Clear search
            </button>
          </div>
        )}

        {/* Video Tutorials */}
        <div className="mt-8 bg-gradient-to-r from-primary-900/30 to-purple-900/30 border border-primary-700/50 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-3">📺 Video Tutorials</h2>
          <p className="text-gray-300 text-sm mb-4">
            Check out our video tutorials for step-by-step guides on using the AI Code Review System.
          </p>
          <button className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors text-sm font-medium">
            Watch Tutorials
          </button>
        </div>
      </div>
    </Layout>
  );
}
