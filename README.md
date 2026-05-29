Automatically checks Coles and Woolworths weekly for sales on chosen products, and notifies you via a GitHub Issue (which can trigger a GitHub Mobile push notification if setup)

# DISCLAIMER 
Currently only works for coles, Woolworths' API blocks the python library from accessing the website. I am working on a solution.


## Setup
### Create the `sale-alert` label
Use the exact syntax or the label will not work as intended.

### Enable GitHub Mobile notifications (Optional)
- Install the **GitHub Mobile** app
- Go to your repo --> **Watch** --> **Custom** --> tick **Issues**
- You'll get a push notification whenever a sale issue is created

### Edit your tracked products
Open `products/products.json` and replace the examples with your own products:

```
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
- `normal_price` is the regular (non-sale) price — used to detect a discount
- The scripts also detect Coles/Woolworths' own "on special" flags, even if price hasn't changed

### Run manually to test
Go to **Actions** --> **Supermarket Sale Checker** --> **Run workflow**


## Notes
- Coles and Woolworths have **unofficial APIs**. They may occasionally change or add bot protection
- If checks start failing, check the **Actions** tab for error logs

 
