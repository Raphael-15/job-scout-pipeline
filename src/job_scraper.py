#!/usr/bin/env python3
"""
Job Scraper Module
Scrapes job listings from company career pages and LinkedIn
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from job_matcher import JobMatcher
from email_notifier import EmailNotifier

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_scout.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JobScraper:
    """Scrapes job listings from company websites"""
    
    def __init__(self, config_path: str = 'config/companies.json'):
        """Initialize scraper with company list"""
        self.companies = self._load_companies(config_path)
        self.matcher = JobMatcher()
        self.notifier = EmailNotifier()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def _load_companies(self, config_path: str) -> List[Dict]:
        """Load companies from config"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('companies', [])
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            return []
    
    def scrape_all_companies(self) -> List[Dict]:
        """Scrape jobs from all companies"""
        all_jobs = []
        logger.info(f"Starting scrape for {len(self.companies)} companies")
        
        for company in self.companies:
            logger.info(f"Scraping {company['name']}...")
            jobs = self.scrape_company(company)
            all_jobs.extend(jobs)
        
        logger.info(f"Total jobs found: {len(all_jobs)}")
        return all_jobs
    
    def scrape_company(self, company: Dict) -> List[Dict]:
        """Scrape jobs from a single company"""
        jobs = []
        
        try:
            # Try to scrape careers page
            jobs.extend(self._scrape_careers_page(company))
        except Exception as e:
            logger.warning(f"Error scraping {company['name']}: {str(e)}")
        
        return jobs
    
    def _scrape_careers_page(self, company: Dict) -> List[Dict]:
        """Scrape the careers page of a company"""
        jobs = []
        url = company.get('careers_url')
        
        if not url:
            return jobs
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Generic job extraction (works for most sites)
            job_elements = soup.find_all(['div', 'li'], class_=lambda x: x and ('job' in x.lower() or 'position' in x.lower()))
            
            for element in job_elements:
                job_data = self._extract_job_data(element, company)
                if job_data:
                    jobs.append(job_data)
        
        except requests.RequestException as e:
            logger.warning(f"Network error for {company['name']}: {str(e)}")
        
        return jobs
    
    def _extract_job_data(self, element, company: Dict) -> Dict:
        """Extract job information from HTML element"""
        try:
            title_elem = element.find(['h1', 'h2', 'h3', 'a'], class_=lambda x: x and 'title' in (x.lower() if x else ''))
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            # Build job data
            job_data = {
                "job_id": f"{company['name']}-{title}-{datetime.now().timestamp()}",
                "job_title": title,
                "company": company['name'],
                "location": company.get('location', 'Spain'),
                "careers_url": company.get('careers_url', ''),
                "job_description": element.get_text(strip=True)[:500],  # First 500 chars
                "posted_date": datetime.now().isoformat(),
                "source": "company_website"
            }
            
            return job_data
        
        except Exception as e:
            logger.debug(f"Error extracting job data: {str(e)}")
            return None

def main():
    """Main execution function"""
    logger.info("="*60)
    logger.info("Job Scout Pipeline Started")
    logger.info("="*60)
    
    # Initialize scraper
    scraper = JobScraper()
    
    # Scrape all jobs
    jobs = scraper.scrape_all_companies()
    
    # Match jobs against profile
    matching_jobs = []
    logger.info(f"Matching {len(jobs)} jobs against profile...")
    
    for job in jobs:
        match_score = scraper.matcher.calculate_match_score(job)
        if match_score >= 15:  # 15% threshold
            job['match_score'] = match_score
            matching_jobs.append(job)
            logger.info(f"Match found: {job['job_title']} @ {job['company']} ({match_score}%)")
    
    logger.info(f"Found {len(matching_jobs)} matching jobs")
    
    # Send notifications for new jobs
    if matching_jobs:
        logger.info("Sending email notifications...")
        scraper.notifier.send_batch_notifications(matching_jobs)
    
    # Save job database
    _save_job_database(matching_jobs)
    
    logger.info("="*60)
    logger.info("Job Scout Pipeline Completed")
    logger.info("="*60)

def _save_job_database(jobs: List[Dict]):
    """Save matched jobs to database"""
    try:
        os.makedirs('data', exist_ok=True)
        
        # Load existing jobs
        db_file = 'data/found_jobs.json'
        existing_jobs = []
        
        if os.path.exists(db_file):
            with open(db_file, 'r') as f:
                existing_jobs = json.load(f)
        
        # Add new jobs (avoid duplicates by job_id)
        existing_ids = {job['job_id'] for job in existing_jobs}
        new_jobs = [job for job in jobs if job['job_id'] not in existing_ids]
        
        # Save all jobs
        all_jobs = existing_jobs + new_jobs
        with open(db_file, 'w') as f:
            json.dump(all_jobs, f, indent=2)
        
        logger.info(f"Job database updated: {len(new_jobs)} new jobs, {len(all_jobs)} total")
    
    except Exception as e:
        logger.error(f"Error saving job database: {str(e)}")

if __name__ == "__main__":
    main()
