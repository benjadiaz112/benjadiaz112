"""Refresh public GitHub metrics and the activity panel's data."""
import argparse
import json
import os
import re
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

LOGIN = "benjadiaz112"
API = "https://api.github.com"
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "stats.json"


class ContributionCalendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.labels = {}
        self.tooltip = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "td" and {"id", "data-date", "data-level"} <= attrs.keys():
            self.cells[attrs["id"]] = date.fromisoformat(attrs["data-date"])
        if tag == "tool-tip":
            self.tooltip = attrs.get("for")

    def handle_data(self, data):
        if self.tooltip and data.strip():
            self.labels[self.tooltip] = self.labels.get(self.tooltip, "") + data

    def handle_endtag(self, tag):
        if tag == "tool-tip":
            self.tooltip = None

    def day_counts(self):
        result = {}
        for key, day in self.cells.items():
            label = self.labels.get(key, "").strip()
            match = re.match(r"^(No|[\d,]+) contributions? on ", label)
            if not match:
                raise ValueError("GitHub returned an unreadable contribution calendar")
            count = match[1].replace(",", "")
            result[day] = 0 if count == "No" else int(count)
        days = sorted(result)
        if len(days) < 365 or (days[-1] - days[0]).days != len(days) - 1:
            raise ValueError("GitHub returned an incomplete contribution calendar")
        return result


def get(url, api=False):
    headers = {"User-Agent": "benjadiaz112-profile-dashboard", "Accept-Language": "en-US"}
    if api:
        headers["Accept"] = "application/vnd.github+json"
        if token := os.environ.get("GH_TOKEN"):
            headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(url, headers=headers), timeout=25) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if api else body


def public_repos():
    repos = []
    for page in range(1, 21):
        batch = get(f"{API}/users/{LOGIN}/repos?type=owner&per_page=100&page={page}", api=True)
        repos.extend(repo for repo in batch if not repo["private"])
        if len(batch) < 100:
            return repos
    raise ValueError("Unexpected number of repository pages")


def refresh(calendar_html, previous, profile, repos, include_private):
    parser = ContributionCalendar()
    parser.feed(calendar_html)
    daily = parser.day_counts()
    as_of = max(daily)
    # GitHub pads its visual calendar to a Sunday. Use 53 columns at most.
    start = as_of - timedelta(days=(as_of.weekday() + 1) % 7 + 52 * 7)
    series = [daily.get(start + timedelta(days=i), 0) for i in range((as_of-start).days + 1)]
    total_since_january = sum(count for day, count in daily.items() if day.year == as_of.year)

    annual = {key: previous[key] for key in ("annual_contributions", "annual_year", "annual_as_of")}
    if include_private:
        old_total = annual["annual_contributions"]
        if as_of.year == previous["annual_year"] and total_since_january < old_total:
            raise ValueError("Visible total dropped below the saved combined total. Check GitHub visibility.")
        annual = {
            "annual_contributions": total_since_january,
            "annual_year": as_of.year,
            "annual_as_of": as_of.isoformat(),
        }

    return {
        **annual,
        "calendar_scope": "visible" if include_private else "public",
        "calendar_start": start.isoformat(),
        "calendar_end": as_of.isoformat(),
        "days": series,
        "followers": profile["followers"],
        "public_repos": len(repos),
        "stars": sum(repo["stargazers_count"] for repo in repos),
    }


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--include-private", action="store_true")
    options = args.parse_args()
    previous = json.loads(DATA.read_text(encoding="utf-8"))
    updated = refresh(
        get(f"https://github.com/users/{LOGIN}/contributions"),
        previous,
        get(f"{API}/users/{LOGIN}", api=True),
        public_repos(),
        options.include_private,
    )
    DATA.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
