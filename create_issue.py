#!/usr/bin/env python3
"""
Reads coles_sales.json and woolworths_sales.json and creates a GitHub issue
summarising all active sales found.
"""

import json
import os
import sys
import requests


def load_sales(filename: str) -> list:
    try:
        with open(filename) as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def build_issue_body(coles_sales: list, woolworths_sales: list) -> str:
    lines = ["## 🛒 Supermarket Sale Alert!\n"]

    if coles_sales:
        lines.append("### 🔴 Coles\n")
        lines.append("| Product | Normal Price | Sale Price | Link |")
        lines.append("|---------|-------------|------------|---------|")
        for s in coles_sales:
            lines.append(
                f"| [{s['name']}] | ${s['normal_price']:.2f} | ${s['sale_price']:.2f} | ({s['url']}) |"
            )
        lines.append("")

    if woolworths_sales:
        lines.append("### 🟢 Woolworths\n")
        lines.append("| Product | Normal Price | Sale Price | Link |")
        lines.append("|---------|-------------|------------|---------|")
        for s in woolworths_sales:
            lines.append(
                f"| [{s['name']}] | ${s['normal_price']:.2f} | ${s['sale_price']:.2f} | ({s['url']}) |"
            )
        lines.append("")

    lines.append("---")
    lines.append("_This issue was automatically created by the supermarket sale checker workflow._")
    return "\n".join(lines)


def create_github_issue(title: str, body: str):
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]

    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    payload = {
        "title": title,
        "body": body,
        "labels": ["sale-alert"],
    }

    response = requests.post(url, json=payload, headers=headers, timeout=10)
    response.raise_for_status()
    issue = response.json()
    print(f"Issue created: {issue['html_url']}")


def main():
    coles_sales = load_sales("coles_sales.json")
    woolworths_sales = load_sales("woolworths_sales.json")

    total = len(coles_sales) + len(woolworths_sales)

    if total == 0:
        print("No sales found — skipping issue creation.")
        sys.exit(0)

    stores = []
    if coles_sales:
        stores.append(f"Coles ({len(coles_sales)})")
    if woolworths_sales:
        stores.append(f"Woolworths ({len(woolworths_sales)})")

    title = f"🛒 Sale Alert: {total} item(s) on sale — {' & '.join(stores)}"
    body = build_issue_body(coles_sales, woolworths_sales)
    create_github_issue(title, body)


if __name__ == "__main__":
    main()
