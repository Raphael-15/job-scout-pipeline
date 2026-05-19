#!/usr/bin/env python3
"""
Job Matching Module
Matches job descriptions against user profile
"""

import json
import logging
from typing import Dict, List
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class JobMatcher:
    """Matches jobs against user profile"""
    
    def __init__(self, profile_path: str = 'config/profile.json', keywords_path: str = 'config/job_keywords.json'):
        """Initialize matcher with profile and keywords"""
        self.profile = self._load_json(profile_path)
        self.keywords = self._load_json(keywords_path)
        
        # Extract searchable keywords from profile
        self.user_skills = self._extract_profile_keywords()
    
    def _load_json(self, path: str) -> Dict:
        """Load JSON file"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"File not found: {path}")
            return {}
    
    def _extract_profile_keywords(self) -> List[str]:
        """Extract all searchable keywords from profile"""
        keywords = []
        
        if self.profile:
            # Add technical skills
            tech_skills = self.profile.get('technical_skills', {})
            for skill_list in tech_skills.values():
                keywords.extend(skill_list)
            
            # Add domain expertise
            keywords.extend(self.profile.get('domain_expertise', []))
            
            # Add job titles
            keywords.extend(self.profile.get('job_titles_target', []))
        
        return [kw.lower() for kw in keywords]
    
    def calculate_match_score(self, job: Dict) -> float:
        """Calculate match score between job and profile (0-100)"""
        if not self.profile:
            return 0
        
        job_text = self._prepare_job_text(job)
        
        # Initialize score components
        skill_score = self._calculate_skill_match(job_text)
        location_score = self._calculate_location_match(job)
        level_score = self._calculate_level_match(job_text)
        
        # Weighted average
        final_score = (skill_score * 0.6) + (location_score * 0.2) + (level_score * 0.2)
        
        return min(100, max(0, final_score))
    
    def _prepare_job_text(self, job: Dict) -> str:
        """Prepare job text for analysis"""
        parts = [
            job.get('job_title', ''),
            job.get('job_description', ''),
            job.get('location', '')
        ]
        return ' '.join(parts).lower()
    
    def _calculate_skill_match(self, job_text: str) -> float:
        """Calculate skill match percentage"""
        if not self.user_skills:
            return 0
        
        matches = 0
        for skill in self.user_skills:
            if skill.lower() in job_text:
                matches += 1
        
        return (matches / len(self.user_skills)) * 100
    
    def _calculate_location_match(self, job: Dict) -> float:
        """Calculate location match"""
        location = job.get('location', '').lower()
        priority = self.profile.get('location_priority', [])
        
        for loc in priority:
            if loc.lower() in location:
                return 100 if 'barcelona' in location else 80
        
        if 'spain' in location:
            return 50
        
        return 0
    
    def _calculate_level_match(self, job_text: str) -> float:
        """Calculate job level match (entry-level, internship, etc.)"""
        seniority = self.keywords.get('seniority_levels', {})
        
        # Check for entry-level keywords
        for keyword in seniority.get('entry_level', []):
            if keyword.lower() in job_text:
                return 100
        
        # Check for internship keywords
        for keyword in seniority.get('internship', []):
            if keyword.lower() in job_text:
                return 100
        
        # Check for early career
        for keyword in seniority.get('early_career', []):
            if keyword.lower() in job_text:
                return 80
        
        # Check for exclusion keywords (senior, manager, etc.)
        exclude = self.keywords.get('exclude_keywords', [])
        for keyword in exclude:
            if keyword.lower() in job_text:
                return 0
        
        # If no level specified, default to moderate match
        return 50

def main():
    """Test the matcher"""
    matcher = JobMatcher()
    
    # Test job
    test_job = {
        "job_title": "Junior Data Analyst",
        "job_description": "Looking for a Python and SQL specialist for entry-level position in Barcelona. Experience with Tableau and Power BI required.",
        "location": "Barcelona, Spain"
    }
    
    score = matcher.calculate_match_score(test_job)
    print(f"Match score: {score}%")

if __name__ == "__main__":
    main()
