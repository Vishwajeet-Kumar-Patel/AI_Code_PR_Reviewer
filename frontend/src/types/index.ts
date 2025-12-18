// API Response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

// User types
export interface User {
  id: number;
  github_username: string;
  email?: string;
  avatar_url?: string;
  created_at: string;
}

// Repository types
export interface Repository {
  id: number;
  owner: string;
  name: string;
  full_name: string;
  description?: string;
  language?: string;
}

// Pull Request types
export interface PullRequest {
  id: number;
  repository_id: number;
  pr_number: number;
  title: string;
  description?: string;
  author: string;
  state: 'open' | 'closed' | 'merged';
  base_branch: string;
  head_branch: string;
  created_at: string;
  updated_at: string;
  repository?: Repository;
  reviews?: Review[];
}

// Code Analysis types
export interface FileAnalysis {
  file_path: string;
  language: string;
  issues: Issue[];
  complexity_metrics?: ComplexityMetrics;
  security_findings?: SecurityFinding[];
  quality_score: number;
}

export interface Issue {
  type: 'security' | 'warning' | 'info' | 'complexity';
  severity: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  description: string;
  line_number?: number;
  line_range?: { start: number; end: number };
  code_snippet?: string;
  recommendation: string;
  category?: string;
}

export interface ComplexityMetrics {
  cyclomatic_complexity: number;
  cognitive_complexity: number;
  lines_of_code: number;
  maintainability_index?: number;
}

export interface SecurityFinding {
  vulnerability_type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  line_number: number;
  code_snippet: string;
  recommendation: string;
  cwe_id?: string;
  owasp_category?: string;
}

// Review types
export interface Review {
  id: string;
  pull_request_id: number;
  user_id?: number;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  quality_score?: number;
  security_score?: number;
  complexity_score?: number;
  file_analyses?: FileAnalysis[];
  security_issues?: Issue[];
  complexity_issues?: Issue[];
  summary?: string;
  recommendations?: string[];
  ai_provider?: string;
  analysis_duration?: number;
  created_at: string;
  completed_at?: string;
  pull_request?: PullRequest;
}

// Review Request
export interface ReviewRequest {
  repository_owner: string;
  repository_name: string;
  pull_request_number: number;
  github_token?: string;
}

// Dashboard Statistics
export interface DashboardStats {
  total_reviews: number;
  reviews_today: number;
  avg_quality_score: number;
  critical_issues: number;
  repositories_count: number;
  open_prs: number;
}

// Filter types
export interface PRFilter {
  repository?: string;
  status?: 'open' | 'closed' | 'merged' | 'all';
  author?: string;
  sort?: 'newest' | 'oldest' | 'updated';
  search?: string;
}

// Pagination
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}
