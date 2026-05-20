# 🛒 Supermarket Sale Checker

Automatically checks Coles and Woolworths weekly for sales on your tracked products, and notifies you via a GitHub Issue (which triggers a GitHub Mobile push notification).

## Setup

### 1. Create a GitHub repo and push these files
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Create the `sale-alert` label
Go to your repo → **Issues** → **Labels** → **New label**
- Name: `sale-alert`
- Colour: pick anything (e.g. `#e11d48`)

### 3. Enable GitHub Mobile notifications
- Install the **GitHub Mobile** app
- Go to your repo → **Watch** → **Custom** → tick **Issues**
- You'll get a push notification whenever a sale issue is created

### 4. Edit your tracked products
Open `products/products.json` and replace the examples with your own products:

```json
{
  "coles": [
    { "name": "Product Name", "id": "optional", "normal_price": 5.50 }
  ],
  "woolworths": [
    { "name": "Product Name", "stockcode": "optional", "normal_price": 5.50 }
  ]
}
```

**Tips for finding products:**
- Use the exact product name as shown on the Coles/Woolworths website
- `normal_price` is the full (non-sale) price — used to detect a discount
- The scripts also detect Coles/Woolworths' own "on special" flags, even if price hasn't changed

### 5. Run manually to test
Go to **Actions** → **Supermarket Sale Checker** → **Run workflow**

---

## How it works

| File | Purpose |
|------|---------|
| `.github/workflows/sale-checker.yml` | Runs every Monday at 8 AM AEST |
| `check_coles.py` | Queries the Coles API for your products |
| `check_woolworths.py` | Queries the Woolworths API for your products |
| `create_issue.py` | Creates a GitHub Issue with a sale summary table |
| `products/products.json` | Your list of tracked products and normal prices |

## ⚠️ Notes

- Coles and Woolworths have **unofficial APIs** — they may occasionally change or add bot protection
- If checks start failing, check the **Actions** tab for error logs
- The `GITHUB_TOKEN` used for issue creation is automatically provided by GitHub Actions — no setup needed
