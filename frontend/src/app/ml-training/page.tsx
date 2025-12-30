'use client';

import { useState } from 'react';
import { 
  Brain, 
  Zap, 
  TrendingUp, 
  Play, 
  CheckCircle, 
  AlertCircle,
  BarChart3,
  Cpu,
  Loader2,
  Download,
  RefreshCw
} from 'lucide-react';
import useSWR from 'swr';
import { mlTrainingAPI, type MLModel, type PredictionRequest } from '@/lib/api/advanced-features';

export default function MLTrainingPage() {
  const [isTraining, setIsTraining] = useState(false);
  const [trainingResult, setTrainingResult] = useState<any>(null);
  const [predictionCode, setPredictionCode] = useState('');
  const [predictionResult, setPredictionResult] = useState<any>(null);
  const [selectedModelType, setSelectedModelType] = useState<'random_forest' | 'gradient_boosting'>('random_forest');

  // Fetch existing models
  const { data: modelsData, mutate: refreshModels, isLoading } = useSWR(
    'ml-models',
    () => mlTrainingAPI.getModels()
  );

  const models = modelsData?.models || [];

  // Train new model
  const handleTrainModel = async () => {
    setIsTraining(true);
    setTrainingResult(null);
    try {
      const result = await mlTrainingAPI.trainModel({
        model_type: selectedModelType,
        training_data_days: 90,
      });
      setTrainingResult(result);
      await refreshModels();
    } catch (error: any) {
      setTrainingResult({ 
        success: false, 
        error: error.response?.data?.detail || 'Training failed' 
      });
    } finally {
      setIsTraining(false);
    }
  };

  // Get prediction
  const handleGetPrediction = async () => {
    if (!predictionCode.trim()) return;
    
    try {
      const result = await mlTrainingAPI.getPrediction({
        code: predictionCode,
        language: 'python',
      });
      setPredictionResult(result);
    } catch (error: any) {
      setPredictionResult({ 
        error: error.response?.data?.detail || 'Prediction failed' 
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl shadow-lg">
                <Brain className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
                  ML Training Pipeline
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Cost-optimized code review predictions
                </p>
              </div>
            </div>
            <button
              onClick={() => refreshModels()}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span className="text-sm font-medium">Refresh</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Train New Model Section */}
          <div className="lg:col-span-2 space-y-6">
            {/* Training Card */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                  <Cpu className="w-5 h-5 mr-2 text-purple-600" />
                  Train New Model
                </h2>
              </div>
              
              <div className="p-6 space-y-4">
                {/* Model Type Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Model Type
                  </label>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <button
                      onClick={() => setSelectedModelType('random_forest')}
                      className={`p-4 border-2 rounded-lg transition-all ${
                        selectedModelType === 'random_forest'
                          ? 'border-purple-600 bg-purple-50 dark:bg-purple-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-purple-300'
                      }`}
                    >
                      <div className="font-medium text-gray-900 dark:text-white">Random Forest</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        High accuracy, interpretable
                      </div>
                    </button>
                    <button
                      onClick={() => setSelectedModelType('gradient_boosting')}
                      className={`p-4 border-2 rounded-lg transition-all ${
                        selectedModelType === 'gradient_boosting'
                          ? 'border-purple-600 bg-purple-50 dark:bg-purple-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-purple-300'
                      }`}
                    >
                      <div className="font-medium text-gray-900 dark:text-white">Gradient Boosting</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Best performance, complex
                      </div>
                    </button>
                  </div>
                </div>

                {/* Train Button */}
                <button
                  onClick={handleTrainModel}
                  disabled={isTraining}
                  className="w-full flex items-center justify-center space-x-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-lg font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
                >
                  {isTraining ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Training Model...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      <span>Start Training</span>
                    </>
                  )}
                </button>

                {/* Training Result */}
                {trainingResult && (
                  <div className={`p-4 rounded-lg ${
                    trainingResult.success 
                      ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800' 
                      : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
                  }`}>
                    <div className="flex items-start space-x-3">
                      {trainingResult.success ? (
                        <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5" />
                      ) : (
                        <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5" />
                      )}
                      <div className="flex-1">
                        <h3 className={`font-medium ${
                          trainingResult.success ? 'text-green-900 dark:text-green-100' : 'text-red-900 dark:text-red-100'
                        }`}>
                          {trainingResult.success ? 'Training Completed!' : 'Training Failed'}
                        </h3>
                        {trainingResult.success && (
                          <div className="mt-2 text-sm text-green-800 dark:text-green-200 space-y-1">
                            <p>Accuracy: {(trainingResult.accuracy * 100).toFixed(2)}%</p>
                            <p>Training samples: {trainingResult.training_samples}</p>
                            <p>Training time: {trainingResult.training_time}</p>
                          </div>
                        )}
                        {trainingResult.error && (
                          <p className="mt-1 text-sm text-red-800 dark:text-red-200">
                            {trainingResult.error}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Code Prediction Card */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                  <Zap className="w-5 h-5 mr-2 text-yellow-600" />
                  Get Prediction
                </h2>
              </div>
              
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Paste your code
                  </label>
                  <textarea
                    value={predictionCode}
                    onChange={(e) => setPredictionCode(e.target.value)}
                    placeholder="def hello_world():\n    print('Hello, World!')"
                    className="w-full h-40 px-4 py-3 bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-mono text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                  />
                </div>

                <button
                  onClick={handleGetPrediction}
                  disabled={!predictionCode.trim()}
                  className="w-full flex items-center justify-center space-x-2 px-6 py-3 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <TrendingUp className="w-5 h-5" />
                  <span>Get Prediction</span>
                </button>

                {/* Prediction Result */}
                {predictionResult && !predictionResult.error && (
                  <div className="p-4 bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                    <h3 className="font-semibold text-yellow-900 dark:text-yellow-100 mb-3">
                      Prediction Results
                    </h3>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div className="bg-white dark:bg-gray-800 p-3 rounded">
                        <div className="text-gray-600 dark:text-gray-400">Review Time</div>
                        <div className="font-bold text-gray-900 dark:text-white">
                          {predictionResult.predicted_review_time} min
                        </div>
                      </div>
                      <div className="bg-white dark:bg-gray-800 p-3 rounded">
                        <div className="text-gray-600 dark:text-gray-400">Issues</div>
                        <div className="font-bold text-gray-900 dark:text-white">
                          {predictionResult.predicted_issues}
                        </div>
                      </div>
                      <div className="bg-white dark:bg-gray-800 p-3 rounded">
                        <div className="text-gray-600 dark:text-gray-400">Complexity</div>
                        <div className="font-bold text-gray-900 dark:text-white">
                          {predictionResult.complexity_score.toFixed(2)}
                        </div>
                      </div>
                      <div className="bg-white dark:bg-gray-800 p-3 rounded">
                        <div className="text-gray-600 dark:text-gray-400">Cost</div>
                        <div className="font-bold text-gray-900 dark:text-white">
                          ${predictionResult.cost_estimate.toFixed(2)}
                        </div>
                      </div>
                    </div>
                    <div className="mt-3 p-3 bg-white dark:bg-gray-800 rounded">
                      <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                        Recommendation
                      </div>
                      <div className="text-sm text-gray-900 dark:text-white">
                        {predictionResult.recommendation}
                      </div>
                    </div>
                  </div>
                )}

                {predictionResult?.error && (
                  <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                    <p className="text-sm text-red-800 dark:text-red-200">
                      {predictionResult.error}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar - Existing Models */}
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2 text-blue-600" />
                  Trained Models
                </h2>
              </div>
              
              <div className="p-6">
                {isLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
                  </div>
                ) : models.length === 0 ? (
                  <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    <Brain className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p className="text-sm">No models trained yet</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {models.map((model: MLModel) => (
                      <div
                        key={model.id}
                        className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <div className="font-medium text-gray-900 dark:text-white text-sm">
                              {model.model_type}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                              {new Date(model.training_date).toLocaleDateString()}
                            </div>
                          </div>
                          {model.is_active && (
                            <span className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs font-medium rounded">
                              Active
                            </span>
                          )}
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-xs">
                          <div>
                            <span className="text-gray-600 dark:text-gray-400">Accuracy:</span>
                            <span className="ml-1 font-semibold text-gray-900 dark:text-white">
                              {(model.accuracy * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-600 dark:text-gray-400">F1:</span>
                            <span className="ml-1 font-semibold text-gray-900 dark:text-white">
                              {(model.f1_score * 100).toFixed(1)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Stats Card */}
            <div className="bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl shadow-lg p-6 text-white">
              <h3 className="font-semibold mb-4">ML Benefits</h3>
              <div className="space-y-3 text-sm">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4" />
                  <span>80% cost reduction</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4" />
                  <span>Instant predictions</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4" />
                  <span>Continuous learning</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
