# RP Mail

A Windows desktop application for reviewing potential relationships between research projects and research outputs in Research Portal+ (RP+), and contacting researchers from a personal email account.

**Initial release: v0.1.0**

## Features

- Import CSV or Excel (.xlsx) files, edit records, and preview confirmation emails.
- Find publicly listed email addresses through researcher profiles linked from RP+ project pages.
- Prefer contacts whose profile links appear on both the project and publication pages. Retain alternative contacts, source URLs, and lookup timestamps.
- Send a test email, create drafts, or send selected records through a personal account in classic Outlook for Windows.
- Track drafts and submissions locally to prevent duplicate processing.
- Retry page timeouts once and continue after individual page failures. Stop on access restrictions, rate limits, or verification pages.

Finding an email address does not confirm a research relationship. Records must be reviewed before sending. RP Mail does not update RP+ records.

## Requirements

- Windows 64-bit
- Python 3.10+ when running from source
- Microsoft Edge for public email lookup
- **Classic Outlook for Windows**, with the personal sending account configured

New Outlook is not supported by the current sending integration. The application uses Outlook's existing account session and does not ask for or store your email password.

## Getting Started

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python desktop_app.py
```

No separate Playwright browser download is required; the application uses the installed Microsoft Edge browser.

1. Enter your name and personal sending address in the account settings.
2. Import your research data and select records.
3. Run the email lookup and review the suggested contacts and sources.
4. Check the relationship evidence and email preview.
5. Send a test email to yourself before creating drafts or sending reviewed records.

The desktop interface defaults to English. Use the **English / 中文** selector in the top bar to switch languages. Your preference is saved; records and edits are retained when switching. Researcher-facing emails remain in English and use a personal sender's voice.

## Input Data

Required columns: `output_uuid`, `project_uuid`, `project_code`, `title`, `output_url`, and `already_in_relations`.

Automatic email lookup also requires `project_url`. Excel imports use the active worksheet, with column names in the first row.

[examples/sample.csv](examples/sample.csv) contains fictional data for exploring the interface. It is not intended for sending or live lookup.

## Local Data

Working records and settings are stored in `personal_data/`. Processing history is stored in `send_history.sqlite3`. Preserve both when upgrading.

The repository excludes real research datasets, personal account settings, collected contacts, logs, and sending history.

## Testing

```powershell
.venv\Scripts\python tests/run_tests.py
```

Automated checks use temporary data and simulated sending. They do not contact researchers or access RP+. The desktop test briefly opens a Tk window.

A live lookup was verified in the packaged Windows application: one project record returned three publicly listed contact emails and saved the results. This does not establish full-dataset coverage or verify email delivery.

## Building the Windows Application

```powershell
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python -m PyInstaller --noconfirm RPMail.spec
```

Run `dist/RPMail/RPMail.exe` and keep its adjacent `_internal` folder. The packaged application does not require a separate Python installation.

## Current Limitations

- No inbox synchronization, automatic reply classification, or RP+ updates.
- Researchers without linked public profiles or published email addresses need manual contact details.
- Multiple relationships produce separate emails; grouping by researcher is not implemented.
- Generated drafts must be sent manually in Outlook. Later automatic sends skip those records.
- Submission to Outlook does not guarantee delivery. Check the Outbox, Sent Items, and bounce messages.
- Website changes, network conditions, and Outlook account policies can affect lookup and sending.
- The application does not bypass website access restrictions or verification challenges.
