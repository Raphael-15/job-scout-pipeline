# Job Scout Pipeline 🚀

An automated job scraping and matching pipeline that monitors 50+ companies in Spain (Barcelona priority) for entry-level positions, internships, and junior roles matching your profile. Get instant email notifications when new opportunities are posted.

## Features

✅ **Automated Monitoring** - Checks 50+ company career pages and LinkedIn every 6 hours  
✅ **Smart Matching** - Analyzes job descriptions against your skills and experience  
✅ **Email Alerts** - Instant notifications to your inbox when matches are found  
✅ **Deduplication** - Won't send duplicate notifications for the same job  
✅ **Location Filtering** - Prioritizes Barcelona, Spain region  
✅ **GitHub Actions** - Runs completely free on GitHub's servers  

## Companies Monitored

### 🔝 Top Consulting / Tech
- Revolut, Schneider Electric, Eiffage Energía, Mecalux, Dragados, Thermo King, Oliver Wyman

### ⚡ Energy / Industrial / Sustainability
- Nexus Energía, ENGIE, Danone, Sorigué, SDG Group

### 📊 Consulting / Data / Big Tech
- KPMG, NTT Data, HP, Deloitte, PwC, Accenture, BCG

### 🏗 Engineering / Infrastructure
- IDOM, RDT Engineers, Technip Energies, COMSA, Valmet, CELSA Group, Elecnor, Ingerop, VINCI, Copisa, TYPSA

### 🌱 Energy / Environmental / Utilities
- Veolia, Fichtner, ProZero, Avesa

### 🚗 Industrial / Manufacturing / Automotive
- Applus IDIADA, ABB, Henkel, B. Braun, Unex

### 💼 Finance / Consulting / Business
- Banco Sabadell, Caixa Enginyers

### 🚚 Logistics / Retail / Others
- TGW Logistics, Elis, BonÀrea, VICIO, Red Bull

### 🧠 Innovation / Tech / R&D
- Eurecat, Minsait, Bertrandt, Simon

**Total: 50+ companies tracked**

## Quick Start

### Prerequisites
- Python 3.9+
- GitHub account
- Gmail account (for email notifications)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Raphael-15/job-scout-pipeline.git
   cd job-scout-pipeline
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your profile** (edit `config.yaml`)
   ```yaml
   profile:
     email: samemphis98@gmail.com
     match_threshold: 15  # 15%+ match
     location_priority: ["Barcelona", "Spain"]
   ```

4. **Set up Gmail for email notifications** (see [EMAIL_SETUP.md](EMAIL_SETUP.md))

5. **Enable GitHub Actions** (see [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md))

## How It Works

```
1. GitHub Actions triggers every 6 hours
2. Scraper visits company career pages & LinkedIn
3. Extracts job listings with descriptions
4. Matches jobs against your profile (15%+ threshold)
5. Filters for Spain/Barcelona location
6. Deduplicates (skips jobs you've already seen)
7. Sends email notification for new matches
8. Updates job database to prevent re-notifications
```

## Email Notification Example

When a job matches your profile, you'll receive an email like:

```
Subject: ✅ New Job Match Found! - Barcelona, Spain

Company: Revolut
Position: Junior Data Analyst
Location: Barcelona, Spain
Posted: Today

Match Score: 72%
Matched Skills:
✓ Python (85%)
✓ Data Analysis (80%)
✓ SQL (70%)

Apply: [Direct Link]
```

## Configuration

### Match Threshold
- **Strict (20%+)**: Fewer, highly relevant jobs
- **Balanced (15%+)**: More options (RECOMMENDED)
- **Loose (10%+)**: See everything

### Update Frequency
Default: Every 6 hours via GitHub Actions
Can be modified in `.github/workflows/job-scout.yml`

### Companies to Monitor
Edit `config/companies.json` to add/remove companies

## Project Structure

```
job-scout-pipeline/
├── README.md
├── EMAIL_SETUP.md
├── GITHUB_ACTIONS_SETUP.md
├── requirements.txt
├── config/
│   ├── config.yaml              # Your profile & preferences
│   ├── companies.json           # List of companies to monitor
│   └── job_keywords.json        # Skill matching keywords
├── src/
│   ├── scraper.py              # Web scraping logic
│   ├── matcher.py              # Job matching algorithm
│   ├── email_notifier.py        # Email sending logic
│   └── job_database.py          # Job tracking database
├── data/
│   └── seen_jobs.json          # Database of notified jobs
└── .github/
    └── workflows/
        └── job-scout.yml        # GitHub Actions automation
```

## Usage

### Local Testing
```bash
python src/scraper.py
```

### Manual Job Search
```bash
python main.py --run-once
```

### View Matched Jobs
```bash
python src/matcher.py --show-matches
```

## Troubleshooting

### Emails not arriving?
- Check Gmail app password is set correctly
- Verify email in `config.yaml` is correct
- Check spam/promotions folder

### No jobs found?
- Verify companies are still hiring
- Lower match threshold in `config.yaml`
- Check job_keywords.json matches your skills

### GitHub Actions not running?
- Ensure workflow is enabled in Settings → Actions
- Check workflow run logs for errors
- Verify secrets are set (see GITHUB_ACTIONS_SETUP.md)

## Data Privacy

- Your CV data stays on your machine/GitHub
- Email credentials stored as GitHub Secrets (encrypted)
- No data shared with third parties
- Job database stored locally

## Contributing

Want to add more companies or improve matching?
1. Fork the repository
2. Make changes
3. Submit a pull request

## License

MIT License - See LICENSE file

## Support

Having issues? Check:
1. [EMAIL_SETUP.md](EMAIL_SETUP.md) - Email configuration
2. [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) - GitHub Actions setup
3. Create an issue on GitHub

---

**Start monitoring now and never miss a job opportunity! 🎯**

Built with ❤️ for your career in energy, data, and engineering.
