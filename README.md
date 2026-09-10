# Daily Stock Price Email

Sends a formatted email every morning with the current price and
day-over-day change for a watchlist of stocks, using live data from
Yahoo Finance. Runs automatically via GitHub Actions — no server needed.

## Watchlist

GOOG, AAPL, META, TSLA, NVDA, INTC, AMZN, NFLX

> **Note:** SpaceX isn't included because it's privately held and has no
> public stock ticker. Add or remove any ticker by editing the
> `WATCHLIST` dict at the top of `stock_price_email.py`.

## How it works

1. GitHub Actions triggers `stock_price_email.py` every day at **6:00 AM
   UTC+1** (5:00 AM UTC) — same schedule as the crypto price email project.
2. The script pulls each stock's last two closing prices via `yfinance`.
3. It computes the $ and % change and emails a plain-text + HTML summary
   via Gmail SMTP.

## Setup

1. **Create a Gmail App Password** (not your regular Gmail password):
   Google Account → Security → 2-Step Verification → App Passwords.

2. **Add three repo secrets** (Settings → Secrets and variables → Actions):

   | Secret | Value |
   |---|---|
   | `EMAIL_ADDRESS` | the Gmail address sending the email |
   | `EMAIL_APP_PASSWORD` | the App Password from step 1 |
   | `RECIPIENT_EMAIL` | where the daily email should go |

3. Push this repo to GitHub — the workflow in
   `.github/workflows/daily.yml` picks it up automatically. You can also
   trigger it manually anytime from the **Actions** tab
   ("Run workflow" button) to test it without waiting for 6 AM.

## Run locally (for testing)

```bash
pip install -r requirements.txt
export EMAIL_ADDRESS="you@gmail.com"
export EMAIL_APP_PASSWORD="your-app-password"
export RECIPIENT_EMAIL="you@gmail.com"
python stock_price_email.py
```

## Project structure

```
stock-price-email/
├── .github/workflows/daily.yml   # cron schedule + Actions job
├── stock_price_email.py          # fetch prices, build & send email
├── requirements.txt
└── README.md
```
