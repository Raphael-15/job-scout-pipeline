#!/usr/bin/env python3
"""
Email Notification Module
Sends email notifications for matching jobs
"""

import smtplib
import logging
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)

class EmailNotifier:
    """Handles email notifications for job matches"""
    
    def __init__(self):
        """Initialize email notifier with credentials from environment"""
        self.sender_email = os.environ.get('EMAIL_ADDRESS')
        self.sender_password = os.environ.get('EMAIL_PASSWORD')
        self.recipient_email = os.environ.get('RECIPIENT_EMAIL')
        self.notified_jobs = self._load_notified_jobs()
    
    def _load_notified_jobs(self) -> Dict:
        """Load list of already notified jobs"""
        notified_file = 'data/notified_jobs.json'
        try:
            if os.path.exists(notified_file):
                with open(notified_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load notified jobs: {str(e)}")
        return {}
    
    def _save_notified_jobs(self):
        """Save list of notified jobs"""
        os.makedirs('data', exist_ok=True)
        notified_file = 'data/notified_jobs.json'
        try:
            with open(notified_file, 'w') as f:
                json.dump(self.notified_jobs, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save notified jobs: {str(e)}")
    
    def _already_notified(self, job_id: str) -> bool:
        """Check if job was already notified"""
        return job_id in self.notified_jobs
    
    def _mark_notified(self, job_id: str, job_data: Dict):
        """Mark job as notified"""
        self.notified_jobs[job_id] = {
            "notified_at": datetime.now().isoformat(),
            "job_title": job_data.get("job_title"),
            "company": job_data.get("company"),
            "match_score": job_data.get("match_score")
        }
        self._save_notified_jobs()
    
    def send_notification(self, job: Dict) -> bool:
        """Send email notification for a single job"""
        job_id = job.get("job_id")
        
        # Skip if already notified
        if self._already_notified(job_id):
            logger.debug(f"Job {job_id} already notified, skipping")
            return False
        
        # Check credentials
        if not self.sender_email or not self.sender_password:
            logger.warning("Email credentials not configured")
            return False
        
        try:
            subject = self._build_subject(job)
            body_html = self._build_email_html(job)
            
            self._send_email(subject, body_html)
            self._mark_notified(job_id, job)
            
            logger.info(f"✅ Email sent for: {job['job_title']} @ {job['company']}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def _build_subject(self, job: Dict) -> str:
        """Build email subject"""
        match_score = job.get("match_score", 0)
        company = job.get("company", "Company")
        location = job.get("location", "Spain")
        
        return f"✅ Job Match Found ({match_score}%)! {company} | {location}"
    
    def _build_email_html(self, job: Dict) -> str:
        """Build HTML email body"""
        match_score = job.get("match_score", 0)
        job_title = job.get("job_title", "Position")
        company = job.get("company", "Company")
        location = job.get("location", "Not specified")
        description = job.get("job_description", "")[:300]
        job_url = job.get("careers_url", "#")
        posted_date = job.get("posted_date", "Recently")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
        .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
        .job-card {{ background: white; padding: 20px; margin: 20px 0; border-left: 4px solid #667eea; border-radius: 5px; }}
        .match-score {{ font-size: 28px; font-weight: bold; color: #667eea; }}
        .field {{ margin: 15px 0; }}
        .label {{ font-weight: bold; color: #667eea; }}
        .value {{ margin-top: 5px; color: #555; }}
        .cta-button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .cta-button:hover {{ background: #764ba2; }}
        .footer {{ text-align: center; margin-top: 30px; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div style="font-size: 24px;">🎯 NEW JOB MATCH!</div>
            <div class="match-score">{match_score}%</div>
        </div>
        
        <div class="content">
            <div class="job-card">
                <div class="field">
                    <div class="label">Job Title</div>
                    <div class="value">{job_title}</div>
                </div>
                
                <div class="field">
                    <div class="label">Company</div>
                    <div class="value">{company}</div>
                </div>
                
                <div class="field">
                    <div class="label">Location</div>
                    <div class="value">📍 {location}</div>
                </div>
                
                <div class="field">
                    <div class="label">Posted</div>
                    <div class="value">⏰ {posted_date}</div>
                </div>
                
                <div class="field">
                    <div class="label">Job Description (Preview)</div>
                    <div class="value">{description}...</div>
                </div>
                
                <a href="{job_url}" class="cta-button" target="_blank">👉 View Full Job & Apply</a>
            </div>
            
            <div class="footer">
                <p>Job Scout Pipeline - Your automated job search assistant</p>
                <p>Running every 6 hours to find the best opportunities for you</p>
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _send_email(self, subject: str, body_html: str):
        """Send email via SMTP (Gmail)"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = self.recipient_email
            
            # Attach HTML
            part = MIMEText(body_html, "html")
            message.attach(part)
            
            # Send email
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_email, message.as_string())
        
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            raise
    
    def send_batch_notifications(self, jobs: List[Dict]) -> int:
        """Send notifications for multiple jobs"""
        sent_count = 0
        
        logger.info(f"📧 Sending notifications for {len(jobs)} matching jobs")
        
        for job in jobs:
            if self.send_notification(job):
                sent_count += 1
        
        logger.info(f"✅ Sent {sent_count}/{len(jobs)} notifications")
        return sent_count

def main():
    """Test email notifier"""
    notifier = EmailNotifier()
    
    test_job = {
        "job_id": "test_001",
        "job_title": "Junior Data Analyst",
        "company": "Test Company",
        "location": "Barcelona, Spain",
        "job_description": "We are looking for a data analyst with Python and SQL",
        "careers_url": "https://example.com/job",
        "match_score": 78,
        "posted_date": datetime.now().isoformat()
    }
    
    logger.info("Testing email notification...")
    success = notifier.send_notification(test_job)
    
    if success:
        logger.info("✅ Test email sent successfully!")
    else:
        logger.error("❌ Failed to send test email")

if __name__ == "__main__":
    main()
