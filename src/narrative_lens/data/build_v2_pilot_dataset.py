"""
Author-candidate pilot scraper (Phase 1, Dataset V2).

Scrapes ONLY the small, manually-verified candidate account list below (5 Left-wing +
4-5 Western candidates), NOT the full NARRATIVES_ACCOUNTS dict, and writes to a SEPARATE
pilot file (never touches the existing data/raw/*.csv files).

Requires TWITTER_AUTH_TOKEN to be set by the user themselves in their own terminal, e.g.
(PowerShell): $env:TWITTER_AUTH_TOKEN = '<your-auth-token-cookie>'
This script will refuse to run (raise RuntimeError) if that env var is not set - it does
NOT prompt for or collect the token itself.

Output: data/candidates/v2_pilot/pilot_authors_raw.csv
Schema: text, narrative, author, source, platform, timestamp, event_id, is_synthetic,
        collection_date
"""

import csv
import datetime
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Manually verified (2026-09-22, via logged-out X profile pages) candidates for Phase 1.
# Each was checked for: exists, active, verified/plausibly-real, on-topic for the narrative,
# NOT already present in NARRATIVES_ACCOUNTS (build_twitter_dataset.py).
PILOT_CANDIDATES = {
    "Left-wing": [
        "AOC",            # US Congresswoman, personal account, 12.6M followers, active
        "RBReich",        # Robert Reich, economist/commentator, active
        "mehdirhasan",    # journalist/commentator, active
        "TheYoungTurks",  # progressive media org, active
        "MeidasTouch",    # media network - NOTE: heavy on video/clip content, verify
                          # text-per-post volume during QC before trusting for training data
    ],
    "Western": [
        "vonderleyen",    # EU Commission President, personal voice (overlaps institutionally
                          # with existing EU_Commission but distinct personal style)
        "AtlanticCouncil",  # think tank - non-governmental, genuinely diversifies away from
                            # official statements
        "ianbremmer",     # geopolitical pundit/analyst (Eurasia Group/GZERO) - individual voice,
                          # sometimes critical of Western policy; verify during QC that his posts
                          # actually carry alliance-aligned framing, not just neutral analysis
        "CFR_org",        # Council on Foreign Relations - US foreign-policy think tank,
                          # "takes no institutional positions on policy" per its own bio;
                          # adds an establishment-analysis voice distinct from govt accounts
        "ChathamHouse",   # Royal Institute of International Affairs (UK) - adds a European/UK
                          # think-tank voice, complementing the US-heavy CFR_org/AtlanticCouncil
    ],
}

# Backup only - NOT scraped by default (not iterated in scrape_pilot_candidates below). Same
# "official government institution" pattern as existing FCDOGovUK, doesn't add real diversity.
# Merge into PILOT_CANDIDATES["Western"] manually only if one of the 5 above fails QC.
PILOT_BACKUP_CANDIDATES = {
    "Western": ["10DowningStreet"],
}

TARGET_TEXTS_PER_ACCOUNT = 100
OUTPUT_PATH = "data/candidates/v2_pilot/pilot_authors_raw.csv"


def setup_driver():
    options = webdriver.EdgeOptions()
    options.add_argument("--disable-notifications")
    return webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)


def scrape_pilot_candidates(target_texts_per_account=TARGET_TEXTS_PER_ACCOUNT):
    collected_texts = set()
    file_exists = os.path.isfile(OUTPUT_PATH)
    if file_exists:
        import pandas as pd
        existing = pd.read_csv(OUTPUT_PATH)
        collected_texts = set(existing["text"].dropna().astype(str).tolist())

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "text", "narrative", "author", "source", "platform", "timestamp",
                "event_id", "is_synthetic", "collection_date",
            ])

    _auth_token = os.environ.get("TWITTER_AUTH_TOKEN")
    if not _auth_token:
        raise RuntimeError(
            "Missing TWITTER_AUTH_TOKEN environment variable. Set it yourself with: "
            "$env:TWITTER_AUTH_TOKEN = '<your-auth-token-cookie>' (PowerShell), then re-run "
            "this script. This script will never prompt for or collect the token itself."
        )

    driver = setup_driver()
    collection_date = datetime.date.today().isoformat()

    try:
        driver.get("https://x.com")
        time.sleep(3)
        driver.add_cookie({"name": "auth_token", "value": _auth_token, "domain": ".x.com"})
        driver.get("https://x.com")
        time.sleep(5)

        for narrative, accounts in PILOT_CANDIDATES.items():
            for account in accounts:
                print(f"Scraping pilot candidate @{account} ({narrative})...")
                driver.get(f"https://x.com/{account}")
                time.sleep(30)

                account_collected = 0
                scroll_attempts = 0
                no_new_counter = 0

                while account_collected < target_texts_per_account and scroll_attempts < 50:
                    previous = account_collected
                    articles = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')

                    for article in articles:
                        try:
                            text_elem = article.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"]')
                            text = text_elem.text.replace("\n", " ").replace("\r", " ").strip()

                            if text and text not in collected_texts:
                                time_elem = article.find_element(By.TAG_NAME, "time")
                                tweet_date = time_elem.get_attribute("datetime")

                                collected_texts.add(text)
                                account_collected += 1

                                with open(OUTPUT_PATH, "a", newline="", encoding="utf-8") as f:
                                    csv.writer(f).writerow([
                                        text, narrative, account, "twitter", "twitter",
                                        tweet_date, "", False, collection_date,
                                    ])

                                if account_collected >= target_texts_per_account:
                                    break
                        except Exception:
                            continue

                    if account_collected == previous:
                        no_new_counter += 1
                    else:
                        no_new_counter = 0

                    if no_new_counter >= 3:
                        print(f"  Stopping early @{account}: {account_collected} collected.")
                        break

                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(10)
                    scroll_attempts += 1

                print(f"  Finished @{account}: {account_collected} new texts.")
                time.sleep(10)

    finally:
        driver.quit()
        print(f"\nDone. Pilot data saved to {OUTPUT_PATH} (existing dataset files untouched).")


if __name__ == "__main__":
    scrape_pilot_candidates()
