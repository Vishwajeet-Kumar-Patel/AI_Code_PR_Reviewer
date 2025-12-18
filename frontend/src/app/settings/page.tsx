'use client';

import { useState } from 'react';
import Layout from '@/components/Layout';
import { Settings, Save, Github, Key, Database, Sparkles, Shield, Bell } from 'lucide-react';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    githubToken: '••••••••••••••••••',
    openaiKey: '••••••••••••••••••',
    aiProvider: 'openai',
    securityScan: true,
    complexityAnalysis: true,
    autoReview: false,
    notifications: {
      email: true,
      prOpened: true,
      reviewCompleted: true,
      criticalIssues: true,
    },
  });

  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    // In production, this would save to backend
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <Layout user={{ name: 'Vishwajeet Kumar', avatar_url: '' }}>
      <div className="p-6 max-w-4xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white mb-2">Settings</h1>
          <p className="text-gray-400">Configure your AI Code Review System preferences</p>
        </div>

        <div className="space-y-6">
          {/* GitHub Configuration */}
          <div className="bg-dark-800 border border-dark-700 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center">
              <Github className="w-5 h-5 mr-2 text-primary-500" />
              GitHub Integration
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  GitHub Personal Access Token
                </label>
                <input
                  type="password"
                  value={settings.githubToken}
                  onChange={(e) => setSettings({ ...settings, githubToken: e.target.value })}
                  className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-600"
                  placeholder="ghp_••••••••••••••••••"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Required scopes: repo, read:org, read:user
                </p>
              </div>
            </div>
          </div>

          {/* AI Configuration */}
          <div className="bg-dark-800 border border-dark-700 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center">
              <Sparkles className="w-5 h-5 mr-2 text-primary-500" />
              AI Provider Settings
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  AI Provider
                </label>
                <select
                  value={settings.aiProvider}
                  onChange={(e) => setSettings({ ...settings, aiProvider: e.target.value })}
                  className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-600"
                >
                  <option value="openai">OpenAI (GPT-4)</option>
                  <option value="gemini">Google Gemini</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  OpenAI API Key
                </label>
                <input
                  type="password"
                  value={settings.openaiKey}
                  onChange={(e) => setSettings({ ...settings, openaiKey: e.target.value })}
                  className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-600"
                  placeholder="sk-••••••••••••••••••"
                />
              </div>
            </div>
          </div>

          {/* Analysis Settings */}
          <div className="bg-dark-800 border border-dark-700 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center">
              <Shield className="w-5 h-5 mr-2 text-primary-500" />
              Analysis Features
            </h2>
            <div className="space-y-3">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.securityScan}
                  onChange={(e) => setSettings({ ...settings, securityScan: e.target.checked })}
                  className="w-5 h-5 rounded border-dark-600 bg-dark-700 text-primary-600 focus:ring-2 focus:ring-primary-600"
                />
                <div>
                  <div className="text-sm font-medium text-gray-300">Security Vulnerability Scanning</div>
                  <div className="text-xs text-gray-500">Detect potential security issues in code</div>
                </div>
              </label>
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.complexityAnalysis}
                  onChange={(e) => setSettings({ ...settings, complexityAnalysis: e.target.checked })}
                  className="w-5 h-5 rounded border-dark-600 bg-dark-700 text-primary-600 focus:ring-2 focus:ring-primary-600"
                />
                <div>
                  <div className="text-sm font-medium text-gray-300">Complexity Analysis</div>
                  <div className="text-xs text-gray-500">Analyze cyclomatic and cognitive complexity</div>
                </div>
              </label>
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.autoReview}
                  onChange={(e) => setSettings({ ...settings, autoReview: e.target.checked })}
                  className="w-5 h-5 rounded border-dark-600 bg-dark-700 text-primary-600 focus:ring-2 focus:ring-primary-600"
                />
                <div>
                  <div className="text-sm font-medium text-gray-300">Automatic Review</div>
                  <div className="text-xs text-gray-500">Automatically review new pull requests</div>
                </div>
              </label>
            </div>
          </div>

          {/* Notification Settings */}
          <div className="bg-dark-800 border border-dark-700 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center">
              <Bell className="w-5 h-5 mr-2 text-primary-500" />
              Notifications
            </h2>
            <div className="space-y-3">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.notifications.prOpened}
                  onChange={(e) => setSettings({
                    ...settings,
                    notifications: { ...settings.notifications, prOpened: e.target.checked }
                  })}
                  className="w-5 h-5 rounded border-dark-600 bg-dark-700 text-primary-600 focus:ring-2 focus:ring-primary-600"
                />
                <span className="text-sm text-gray-300">New Pull Request Opened</span>
              </label>
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.notifications.reviewCompleted}
                  onChange={(e) => setSettings({
                    ...settings,
                    notifications: { ...settings.notifications, reviewCompleted: e.target.checked }
                  })}
                  className="w-5 h-5 rounded border-dark-600 bg-dark-700 text-primary-600 focus:ring-2 focus:ring-primary-600"
                />
                <span className="text-sm text-gray-300">Review Completed</span>
              </label>
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.notifications.criticalIssues}
                  onChange={(e) => setSettings({
                    ...settings,
                    notifications: { ...settings.notifications, criticalIssues: e.target.checked }
                  })}
                  className="w-5 h-5 rounded border-dark-600 bg-dark-700 text-primary-600 focus:ring-2 focus:ring-primary-600"
                />
                <span className="text-sm text-gray-300">Critical Issues Detected</span>
              </label>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-400">
              {saved && <span className="text-green-500">✓ Settings saved successfully</span>}
            </p>
            <button
              onClick={handleSave}
              className="flex items-center space-x-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors font-medium"
            >
              <Save className="w-4 h-4" />
              <span>Save Settings</span>
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
}
