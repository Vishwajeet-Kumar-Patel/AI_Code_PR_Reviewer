"""
Analytics Service for Code Review Metrics

Provides comprehensive analytics including:
- Team productivity metrics
- Code quality trends
- Developer skill analysis
- Technical debt tracking
- Predictive analytics
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

import pandas as pd
import numpy as np
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from app.db.database import get_db

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for generating analytics and insights from code review data"""
    
    async def get_team_productivity_metrics(
        self,
        db: Session,
        organization_id: Optional[int] = None,
        days_back: int = 30
    ) -> Dict:
        """
        Calculate team productivity metrics
        
        Args:
            db: Database session
            organization_id: Filter by organization
            days_back: Number of days to analyze
            
        Returns:
            Productivity metrics dictionary
        """
        logger.info(f"Calculating team productivity metrics for last {days_back} days")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Query review data
        query = """
        SELECT 
            DATE(r.created_at) as review_date,
            COUNT(*) as total_reviews,
            AVG(r.review_time_seconds) as avg_review_time,
            SUM(r.lines_added + r.lines_deleted) as total_lines_changed,
            AVG(r.code_quality_score) as avg_quality_score,
            COUNT(CASE WHEN r.critical_issues > 0 THEN 1 END) as reviews_with_critical_issues,
            COUNT(DISTINCT r.repository) as unique_repos,
            COUNT(DISTINCT r.reviewer_id) as active_reviewers
        FROM code_reviews r
        WHERE r.created_at >= :cutoff_date
        """
        
        if organization_id:
            query += " AND r.organization_id = :org_id"
        
        query += " GROUP BY DATE(r.created_at) ORDER BY review_date"
        
        params = {"cutoff_date": cutoff_date}
        if organization_id:
            params["org_id"] = organization_id
        
        result = db.execute(query, params)
        daily_metrics = result.fetchall()
        
        if not daily_metrics:
            return self._empty_productivity_metrics()
        
        # Calculate aggregated metrics
        df = pd.DataFrame(daily_metrics, columns=[
            'review_date', 'total_reviews', 'avg_review_time',
            'total_lines_changed', 'avg_quality_score',
            'reviews_with_critical_issues', 'unique_repos', 'active_reviewers'
        ])
        
        # Calculate velocity (reviews per day)
        velocity = df['total_reviews'].sum() / days_back
        
        # Calculate quality trend
        quality_trend = self._calculate_trend(df['avg_quality_score'].tolist())
        
        # Calculate efficiency (lines reviewed per hour)
        total_lines = df['total_lines_changed'].sum()
        total_time_hours = df['avg_review_time'].sum() / 3600
        efficiency = total_lines / total_time_hours if total_time_hours > 0 else 0
        
        return {
            'period_days': days_back,
            'total_reviews': int(df['total_reviews'].sum()),
            'velocity': {
                'reviews_per_day': round(velocity, 2),
                'trend': quality_trend
            },
            'review_time': {
                'average_seconds': int(df['avg_review_time'].mean()),
                'median_seconds': int(df['avg_review_time'].median()),
                'total_hours': round(total_time_hours, 2)
            },
            'code_volume': {
                'total_lines_changed': int(total_lines),
                'avg_lines_per_review': int(total_lines / df['total_reviews'].sum())
            },
            'quality': {
                'average_score': round(df['avg_quality_score'].mean(), 2),
                'trend': quality_trend,
                'critical_issue_rate': round(
                    df['reviews_with_critical_issues'].sum() / df['total_reviews'].sum() * 100, 2
                )
            },
            'team': {
                'unique_repositories': int(df['unique_repos'].max()),
                'active_reviewers': int(df['active_reviewers'].max()),
                'avg_reviewers_per_day': round(df['active_reviewers'].mean(), 1)
            },
            'efficiency': {
                'lines_per_hour': round(efficiency, 0),
                'reviews_per_reviewer': round(
                    df['total_reviews'].sum() / df['active_reviewers'].max(), 2
                ) if df['active_reviewers'].max() > 0 else 0
            },
            'daily_breakdown': df.to_dict('records')
        }
    
    async def get_code_quality_trends(
        self,
        db: Session,
        repository: Optional[str] = None,
        days_back: int = 90
    ) -> Dict:
        """
        Analyze code quality trends over time
        
        Args:
            db: Database session
            repository: Filter by repository
            days_back: Number of days to analyze
            
        Returns:
            Quality trends dictionary
        """
        logger.info(f"Analyzing code quality trends for {repository or 'all repos'}")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        query = """
        SELECT 
            DATE(r.created_at) as date,
            AVG(r.code_quality_score) as avg_quality,
            AVG(r.security_score) as avg_security,
            AVG(r.complexity_score) as avg_complexity,
            COUNT(*) as review_count,
            SUM(r.issues_found) as total_issues,
            SUM(r.critical_issues) as total_critical,
            SUM(r.security_vulnerabilities) as total_security_issues
        FROM code_reviews r
        WHERE r.created_at >= :cutoff_date
        """
        
        if repository:
            query += " AND r.repository = :repo"
        
        query += " GROUP BY DATE(r.created_at) ORDER BY date"
        
        params = {"cutoff_date": cutoff_date}
        if repository:
            params["repo"] = repository
        
        result = db.execute(query, params)
        trend_data = result.fetchall()
        
        if not trend_data:
            return self._empty_quality_trends()
        
        df = pd.DataFrame(trend_data, columns=[
            'date', 'avg_quality', 'avg_security', 'avg_complexity',
            'review_count', 'total_issues', 'total_critical', 'total_security_issues'
        ])
        
        # Calculate trends
        quality_trend = self._calculate_trend(df['avg_quality'].tolist())
        security_trend = self._calculate_trend(df['avg_security'].tolist())
        
        # Calculate issue density
        df['issue_density'] = df['total_issues'] / df['review_count']
        
        return {
            'period_days': days_back,
            'repository': repository,
            'quality_score': {
                'current': round(df['avg_quality'].iloc[-1], 2),
                'average': round(df['avg_quality'].mean(), 2),
                'best': round(df['avg_quality'].max(), 2),
                'worst': round(df['avg_quality'].min(), 2),
                'trend': quality_trend,
                'change_percentage': self._calculate_percentage_change(
                    df['avg_quality'].iloc[0], df['avg_quality'].iloc[-1]
                )
            },
            'security_score': {
                'current': round(df['avg_security'].iloc[-1], 2),
                'average': round(df['avg_security'].mean(), 2),
                'trend': security_trend,
                'vulnerabilities_found': int(df['total_security_issues'].sum())
            },
            'complexity_score': {
                'current': round(df['avg_complexity'].iloc[-1], 2),
                'average': round(df['avg_complexity'].mean(), 2)
            },
            'issues': {
                'total_found': int(df['total_issues'].sum()),
                'critical_count': int(df['total_critical'].sum()),
                'average_per_review': round(df['issue_density'].mean(), 2),
                'trend': self._calculate_trend(df['issue_density'].tolist())
            },
            'timeline': df[['date', 'avg_quality', 'avg_security', 'avg_complexity']].to_dict('records')
        }
    
    async def get_developer_skill_analysis(
        self,
        db: Session,
        organization_id: Optional[int] = None
    ) -> Dict:
        """
        Analyze developer skills based on code quality
        
        Args:
            db: Database session
            organization_id: Filter by organization
            
        Returns:
            Skill analysis dictionary
        """
        logger.info("Analyzing developer skills")
        
        query = """
        SELECT 
            u.username,
            u.id as user_id,
            COUNT(r.id) as total_reviews,
            AVG(r.code_quality_score) as avg_quality,
            AVG(r.security_score) as avg_security,
            AVG(r.complexity_score) as avg_complexity,
            SUM(r.lines_added) as total_lines_added,
            SUM(r.issues_found) as total_issues,
            SUM(r.critical_issues) as total_critical_issues,
            ARRAY_AGG(DISTINCT r.language) as languages_used
        FROM users u
        JOIN code_reviews r ON u.id = r.author_id
        WHERE r.created_at >= CURRENT_DATE - INTERVAL '90 days'
        """
        
        if organization_id:
            query += " AND u.organization_id = :org_id"
        
        query += """
        GROUP BY u.id, u.username
        HAVING COUNT(r.id) >= 5
        ORDER BY avg_quality DESC
        """
        
        params = {}
        if organization_id:
            params["org_id"] = organization_id
        
        result = db.execute(query, params)
        developer_data = result.fetchall()
        
        if not developer_data:
            return {'developers': []}
        
        developers = []
        for dev in developer_data:
            # Calculate skill level
            skill_score = self._calculate_skill_score(
                avg_quality=dev.avg_quality,
                avg_security=dev.avg_security,
                total_reviews=dev.total_reviews,
                critical_issues_rate=dev.total_critical_issues / dev.total_reviews
            )
            
            # Determine skill level
            if skill_score >= 85:
                skill_level = "Expert"
            elif skill_score >= 70:
                skill_level = "Advanced"
            elif skill_score >= 55:
                skill_level = "Intermediate"
            else:
                skill_level = "Beginner"
            
            # Calculate strengths and weaknesses
            strengths, weaknesses = self._identify_strengths_weaknesses({
                'quality': dev.avg_quality,
                'security': dev.avg_security,
                'complexity': dev.avg_complexity
            })
            
            developers.append({
                'username': dev.username,
                'user_id': dev.user_id,
                'skill_level': skill_level,
                'skill_score': round(skill_score, 2),
                'statistics': {
                    'total_reviews': dev.total_reviews,
                    'avg_quality_score': round(dev.avg_quality, 2),
                    'avg_security_score': round(dev.avg_security, 2),
                    'avg_complexity_score': round(dev.avg_complexity, 2),
                    'total_lines_contributed': dev.total_lines_added,
                    'issues_per_review': round(dev.total_issues / dev.total_reviews, 2)
                },
                'languages': dev.languages_used,
                'strengths': strengths,
                'weaknesses': weaknesses,
                'recommendations': self._generate_recommendations(weaknesses)
            })
        
        return {
            'total_developers': len(developers),
            'skill_distribution': self._calculate_skill_distribution(developers),
            'developers': developers
        }
    
    async def get_technical_debt_tracking(
        self,
        db: Session,
        repository: Optional[str] = None
    ) -> Dict:
        """
        Track technical debt over time
        
        Args:
            db: Database session
            repository: Filter by repository
            
        Returns:
            Technical debt metrics
        """
        logger.info(f"Tracking technical debt for {repository or 'all repos'}")
        
        query = """
        SELECT 
            r.repository,
            COUNT(*) as total_reviews,
            SUM(r.issues_found) as total_issues,
            SUM(r.critical_issues) as critical_issues,
            SUM(r.security_vulnerabilities) as security_issues,
            AVG(r.complexity_score) as avg_complexity,
            SUM(CASE WHEN r.code_quality_score < 70 THEN 1 ELSE 0 END) as low_quality_reviews,
            SUM(r.lines_added + r.lines_deleted) as total_code_changes
        FROM code_reviews r
        WHERE r.created_at >= CURRENT_DATE - INTERVAL '90 days'
        """
        
        if repository:
            query += " AND r.repository = :repo"
        
        query += " GROUP BY r.repository"
        
        params = {}
        if repository:
            params["repo"] = repository
        
        result = db.execute(query, params)
        debt_data = result.fetchall()
        
        repositories = []
        for repo_data in debt_data:
            # Calculate debt score (0-100, higher = more debt)
            debt_score = self._calculate_debt_score({
                'total_issues': repo_data.total_issues,
                'critical_issues': repo_data.critical_issues,
                'security_issues': repo_data.security_issues,
                'avg_complexity': repo_data.avg_complexity,
                'low_quality_rate': repo_data.low_quality_reviews / repo_data.total_reviews
            })
            
            # Estimate effort to fix (person-hours)
            estimated_effort = self._estimate_debt_effort(
                total_issues=repo_data.total_issues,
                critical_issues=repo_data.critical_issues,
                security_issues=repo_data.security_issues
            )
            
            repositories.append({
                'repository': repo_data.repository,
                'debt_score': round(debt_score, 2),
                'debt_level': self._categorize_debt_level(debt_score),
                'statistics': {
                    'total_issues': repo_data.total_issues,
                    'critical_issues': repo_data.critical_issues,
                    'security_vulnerabilities': repo_data.security_issues,
                    'avg_complexity': round(repo_data.avg_complexity, 2),
                    'low_quality_rate': round(
                        repo_data.low_quality_reviews / repo_data.total_reviews * 100, 2
                    )
                },
                'estimated_effort': {
                    'hours': estimated_effort,
                    'days': round(estimated_effort / 8, 1)
                },
                'priority': self._prioritize_debt(debt_score, repo_data.critical_issues)
            })
        
        # Sort by debt score (highest first)
        repositories.sort(key=lambda x: x['debt_score'], reverse=True)
        
        return {
            'total_repositories': len(repositories),
            'total_debt_hours': sum(r['estimated_effort']['hours'] for r in repositories),
            'average_debt_score': round(
                sum(r['debt_score'] for r in repositories) / len(repositories), 2
            ) if repositories else 0,
            'repositories': repositories
        }
    
    async def get_predictive_analytics(
        self,
        db: Session,
        repository: str
    ) -> Dict:
        """
        Generate predictive analytics for bug probability
        
        Args:
            db: Database session
            repository: Repository to analyze
            
        Returns:
            Predictive analytics
        """
        logger.info(f"Generating predictive analytics for {repository}")
        
        # Get historical data
        query = """
        SELECT 
            r.file_path,
            COUNT(*) as change_frequency,
            AVG(r.complexity_score) as avg_complexity,
            SUM(r.issues_found) as total_issues,
            SUM(r.critical_issues) as total_critical,
            MAX(r.created_at) as last_modified
        FROM code_reviews r
        WHERE r.repository = :repo
        AND r.created_at >= CURRENT_DATE - INTERVAL '180 days'
        GROUP BY r.file_path
        HAVING COUNT(*) >= 3
        """
        
        result = db.execute(query, {"repo": repository})
        file_data = result.fetchall()
        
        hotspots = []
        for file in file_data:
            # Calculate bug probability score
            bug_probability = self._calculate_bug_probability({
                'change_frequency': file.change_frequency,
                'avg_complexity': file.avg_complexity,
                'issue_count': file.total_issues,
                'days_since_modified': (datetime.utcnow() - file.last_modified).days
            })
            
            hotspots.append({
                'file_path': file.file_path,
                'bug_probability': round(bug_probability, 2),
                'risk_level': self._categorize_risk_level(bug_probability),
                'metrics': {
                    'change_frequency': file.change_frequency,
                    'avg_complexity': round(file.avg_complexity, 2),
                    'total_issues': file.total_issues,
                    'critical_issues': file.total_critical
                },
                'recommendation': self._get_hotspot_recommendation(bug_probability)
            })
        
        # Sort by probability (highest first)
        hotspots.sort(key=lambda x: x['bug_probability'], reverse=True)
        
        return {
            'repository': repository,
            'total_files_analyzed': len(hotspots),
            'high_risk_files': len([h for h in hotspots if h['risk_level'] == 'high']),
            'hotspots': hotspots[:20],  # Top 20 high-risk files
            'generated_at': datetime.utcnow().isoformat()
        }
    
    # Helper methods
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from time series data"""
        if len(values) < 2:
            return "stable"
        
        # Simple linear regression
        x = np.arange(len(values))
        y = np.array(values)
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.5:
            return "increasing"
        elif slope < -0.5:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_percentage_change(self, old: float, new: float) -> float:
        """Calculate percentage change"""
        if old == 0:
            return 0.0
        return round((new - old) / old * 100, 2)
    
    def _calculate_skill_score(
        self,
        avg_quality: float,
        avg_security: float,
        total_reviews: int,
        critical_issues_rate: float
    ) -> float:
        """Calculate overall skill score"""
        # Weighted scoring
        quality_weight = 0.4
        security_weight = 0.3
        experience_weight = 0.2
        reliability_weight = 0.1
        
        experience_score = min(total_reviews / 50 * 100, 100)
        reliability_score = max(0, 100 - (critical_issues_rate * 100))
        
        score = (
            avg_quality * quality_weight +
            avg_security * security_weight +
            experience_score * experience_weight +
            reliability_score * reliability_weight
        )
        
        return score
    
    def _identify_strengths_weaknesses(self, metrics: Dict) -> Tuple[List[str], List[str]]:
        """Identify strengths and weaknesses from metrics"""
        strengths = []
        weaknesses = []
        
        if metrics['quality'] >= 80:
            strengths.append("High code quality")
        elif metrics['quality'] < 60:
            weaknesses.append("Code quality needs improvement")
        
        if metrics['security'] >= 85:
            strengths.append("Strong security awareness")
        elif metrics['security'] < 70:
            weaknesses.append("Security vulnerabilities")
        
        if metrics['complexity'] >= 70:
            strengths.append("Good code simplicity")
        elif metrics['complexity'] < 50:
            weaknesses.append("Overly complex code")
        
        return strengths, weaknesses
    
    def _generate_recommendations(self, weaknesses: List[str]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        for weakness in weaknesses:
            if "quality" in weakness.lower():
                recommendations.append("Review clean code principles and refactoring techniques")
            if "security" in weakness.lower():
                recommendations.append("Complete security training and OWASP Top 10 review")
            if "complex" in weakness.lower():
                recommendations.append("Practice breaking down complex functions into smaller units")
        
        return recommendations
    
    def _calculate_skill_distribution(self, developers: List[Dict]) -> Dict:
        """Calculate skill level distribution"""
        distribution = defaultdict(int)
        for dev in developers:
            distribution[dev['skill_level']] += 1
        
        return dict(distribution)
    
    def _calculate_debt_score(self, metrics: Dict) -> float:
        """Calculate technical debt score (0-100)"""
        issue_score = min(metrics['total_issues'] / 100 * 30, 30)
        critical_score = min(metrics['critical_issues'] / 20 * 30, 30)
        security_score = min(metrics['security_issues'] / 10 * 20, 20)
        complexity_score = max(0, (100 - metrics['avg_complexity']) * 0.1)
        quality_score = metrics['low_quality_rate'] * 10
        
        return issue_score + critical_score + security_score + complexity_score + quality_score
    
    def _categorize_debt_level(self, debt_score: float) -> str:
        """Categorize debt level"""
        if debt_score >= 70:
            return "Critical"
        elif debt_score >= 50:
            return "High"
        elif debt_score >= 30:
            return "Medium"
        else:
            return "Low"
    
    def _estimate_debt_effort(
        self,
        total_issues: int,
        critical_issues: int,
        security_issues: int
    ) -> float:
        """Estimate effort to fix technical debt in hours"""
        # Estimates: critical = 4h, security = 3h, regular = 1h
        effort = (
            critical_issues * 4 +
            security_issues * 3 +
            (total_issues - critical_issues - security_issues) * 1
        )
        return effort
    
    def _prioritize_debt(self, debt_score: float, critical_issues: int) -> str:
        """Prioritize debt remediation"""
        if debt_score >= 70 or critical_issues >= 10:
            return "Urgent"
        elif debt_score >= 50 or critical_issues >= 5:
            return "High"
        elif debt_score >= 30:
            return "Medium"
        else:
            return "Low"
    
    def _calculate_bug_probability(self, metrics: Dict) -> float:
        """Calculate probability of bugs (0-100)"""
        # Factors: high churn = more bugs, high complexity = more bugs
        churn_score = min(metrics['change_frequency'] / 20 * 30, 30)
        complexity_score = max(0, (100 - metrics['avg_complexity']) * 0.3)
        issue_score = min(metrics['issue_count'] / 10 * 25, 25)
        recency_score = max(0, 15 - (metrics['days_since_modified'] / 30))
        
        return churn_score + complexity_score + issue_score + recency_score
    
    def _categorize_risk_level(self, probability: float) -> str:
        """Categorize risk level"""
        if probability >= 70:
            return "high"
        elif probability >= 40:
            return "medium"
        else:
            return "low"
    
    def _get_hotspot_recommendation(self, probability: float) -> str:
        """Get recommendation for hotspot"""
        if probability >= 70:
            return "Immediate refactoring required. Add comprehensive tests."
        elif probability >= 40:
            return "Schedule code review and consider refactoring."
        else:
            return "Monitor for changes. No immediate action needed."
    
    def _empty_productivity_metrics(self) -> Dict:
        """Return empty productivity metrics"""
        return {'total_reviews': 0, 'message': 'No data available'}
    
    def _empty_quality_trends(self) -> Dict:
        """Return empty quality trends"""
        return {'message': 'No data available'}


# Singleton instance
analytics_service = AnalyticsService()
