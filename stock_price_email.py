"""
stock_price_email.py
---------------------
Fetches the current price (and prior close) for a watchlist of stocks,
computes the day-over-day $ and % change, and emails a formatted
summary via Gmail SMTP.

Designed to run daily on GitHub Actions (see .github/workflows/daily.yml).

Required environment variables (set as GitHub Actions secrets):
    EMAIL_ADDRESS    - the Gmail address sending the email
    EMAIL_APP_PASSWORD - a Gmail App Password (not your regular password)
    RECIPIENT_EMAIL  - where the daily email should be sent
"""
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import yfinance as yf

# Ticker -> display name. Add/remove tickers here.
WATCHLIST = {
    "GOOG": "Alphabet (Google)",
    "AAPL": "Apple",
    "META": "Meta Platforms",
    "TSLA": "Tesla",
    "NVDA": "NVIDIA",
    "INTC": "Intel",
    "AMZN": "Amazon",
    "NFLX": "Netflix",
}
# Note: SpaceX has no public ticker (it's privately held) so it's not
# included here. Swap in any other ticker by adding it to WATCHLIST above.


def fetch_prices() -> list[dict]:
    """Returns a list of {ticker, name, price, prev_close, change, pct_change}."""
    results = []

    for symbol, name in WATCHLIST.items():
        try:
            # last 5 trading days is a safety margin around weekends/holidays
            hist = yf.Ticker(symbol).history(period="5d")
            if len(hist) < 2:
                print(f"Warning: not enough data for {symbol}, skipping")
                continue
            price = float(hist["Close"].iloc[-1])
            prev_close = float(hist["Close"].iloc[-2])
            change = price - prev_close
            pct_change = (change / prev_close) * 100 if prev_close else 0
            results.append(
                {
                    "ticker": symbol,
                    "name": name,
                    "price": price,
                    "prev_close": prev_close,
                    "change": change,
                    "pct_change": pct_change,
                }
            )
        except Exception as e:
            print(f"Warning: could not fetch {symbol}: {e}")
    return results


def build_email_body(rows: list[dict]) -> tuple[str, str]:
    today = datetime.now().strftime("%A, %B %d, %Y")

    # ---- plain text version ----
    lines = [f"Daily Stock Prices — {today}", ""]
    for r in rows:
        arrow = "▲" if r["change"] >= 0 else "▼"
        lines.append(
            f"{r['ticker']:<6} {r['name']:<22} ${r['price']:>9,.2f}  "
            f"{arrow} {r['change']:+.2f} ({r['pct_change']:+.2f}%)"
        )
    text_body = "\n".join(lines)

    # ---- HTML version ----
    rows_html = ""
    for r in rows:
        color = "#16a34a" if r["change"] >= 0 else "#dc2626"
        arrow = "▲" if r["change"] >= 0 else "▼"
        rows_html += f"""
        <tr>
          <td style="padding:10px 14px;font-weight:600;">{r['ticker']}</td>
          <td style="padding:10px 14px;color:#6b7280;">{r['name']}</td>
          <td style="padding:10px 14px;text-align:right;">${r['price']:,.2f}</td>
          <td style="padding:10px 14px;text-align:right;color:{color};font-weight:600;">
            {arrow} {r['change']:+.2f} ({r['pct_change']:+.2f}%)
          </td>
        </tr>"""

    html_body = f"""
    <html>
      <body style="font-family:Segoe UI,Arial,sans-serif;background:#0d1117;padding:24px;color:#e6edf3;">
        <div style="max-width:560px;margin:auto;background:#161b22;border-radius:12px;overflow:hidden;border:1px solid #30363d;">
          <div style="background:#1f6feb;padding:18px 24px;">
            <h2 style="margin:0;color:white;">📈 Daily Stock Prices</h2>
            <p style="margin:4px 0 0;color:#dbeafe;font-size:13px;">{today}</p>
          </div>
          <table style="width:100%;border-collapse:collapse;">
            <thead>
              <tr style="background:#0d1117;color:#8b949e;font-size:12px;text-transform:uppercase;">
                <th style="padding:10px 14px;text-align:left;">Ticker</th>
                <th style="padding:10px 14px;text-align:left;">Company</th>
                <th style="padding:10px 14px;text-align:right;">Price</th>
                <th style="padding:10px 14px;text-align:right;">Change</th>
              </tr>
            </thead>
            <tbody>{rows_html}
            </tbody>
          </table>
          <div style="padding:14px 24px;color:#6b7280;font-size:12px;">
            Sent automatically every morning via GitHub Actions.
          </div>
        </div>
      </body>
    </html>
    """
    return text_body, html_body


def send_email(text_body: str, html_body: str):
    sender = os.environ["EMAIL_ADDRESS"]
    password = os.environ["EMAIL_APP_PASSWORD"]
    recipient = os.environ["RECIPIENT_EMAIL"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📈 Daily Stock Prices — {datetime.now().strftime('%b %d, %Y')}"
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    print(f"Email sent to {recipient}")


def main():
    rows = fetch_prices()
    if not rows:
        print("No prices fetched — aborting without sending email.")
        return
    text_body, html_body = build_email_body(rows)
    send_email(text_body, html_body)


if __name__ == "__main__":
    main()
