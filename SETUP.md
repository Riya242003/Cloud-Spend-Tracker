# Azure Cost on Wallpaper — Setup Guide

This shows your Azure month-to-date cost right on your desktop wallpaper, updated automatically.

There are two parts: setting up an "app" in Azure so the script is allowed to read your cost data, and setting up the script itself on your computer.

---

## Part 1: Install Python

1. Go to https://www.python.org/downloads/ and download the latest Python for Windows.
2. Run the installer. **Important:** on the first screen, check the box that says "Add python.exe to PATH" before clicking Install.
3. To check it worked, open Command Prompt (press Windows key, type `cmd`, press Enter) and type:
   ```
   python --version
   ```
   You should see something like `Python 3.12.x`.

---

## Part 2: Put the files in a folder

1. Create a folder, for example `C:\AzureCostWallpaper`.
2. Put these 4 files in it (the ones I've created for you):
   - `azure_cost_wallpaper.py`
   - `config.json`
   - `requirements.txt`
   - `README.md` (this file)

---

## Part 3: Install the required Python libraries

1. Open Command Prompt.
2. Navigate to your folder:
   ```
   cd C:\AzureCostWallpaper
   ```
3. Install the libraries:
   ```
   pip install -r requirements.txt
   ```
   Wait for it to finish (it downloads a few packages).

---

## Part 4: Create an Azure "app" so the script can read your cost

The script can't just log in as you every time (that would need a browser popup daily). Instead, we create a small service identity ("service principal") that's only allowed to read cost data.

1. Go to https://portal.azure.com and sign in.
2. In the search bar at top, type **App registrations** and open it.
3. Click **+ New registration**.
   - Name: anything, e.g. `cost-wallpaper-reader`
   - Leave other settings default.
   - Click **Register**.
4. On the app's Overview page, copy and save these two values somewhere safe:
   - **Application (client) ID**
   - **Directory (tenant) ID**
5. On the left menu, click **Certificates & secrets**.
   - Click **+ New client secret**.
   - Give it a description, choose an expiry (12 months is fine — you'll need to redo this step when it expires).
   - Click **Add**.
   - Immediately copy the **Value** column (not the Secret ID) — this is your `client_secret`. It will disappear if you navigate away, so copy it now.

6. Now give this app permission to read cost data:
   - In the search bar, type **Subscriptions** and open it.
   - Click on your subscription.
   - Copy the **Subscription ID** shown there.
   - On the left menu of the subscription, click **Access control (IAM)**.
   - Click **+ Add** → **Add role assignment**.
   - Search for and select **Cost Management Reader**. Click Next.
   - Under "Assign access to", choose **User, group, or service principal**.
   - Click **+ Select members**, search for the app name you created (`cost-wallpaper-reader`), select it, click Select.
   - Click **Review + assign** (twice).

That's it on the Azure side. You now have 4 values: tenant ID, client ID, client secret, subscription ID.

---

## Part 5: Fill in config.json

Open `config.json` in Notepad and replace the placeholder text with your real values, keeping the quotes:

```json
{
  "tenant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "client_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "client_secret": "your-secret-value-here",
  "subscription_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "base_wallpaper_path": ""
}
```

Optional: if you want the cost text overlaid on top of your favorite photo instead of a plain dark background, set `base_wallpaper_path` to the full path of that image, e.g. `"C:\\Users\\YourName\\Pictures\\mywallpaper.jpg"` (note the double backslashes).

Save and close the file.

**Keep config.json private** — it contains a secret. Don't upload it anywhere public like GitHub.

---

## Part 6: Test it

1. In Command Prompt (still inside the folder), run:
   ```
   python azure_cost_wallpaper.py
   ```
2. If it works, you'll see something like:
   ```
   Done. Azure month-to-date cost: USD 42.17
   ```
   And your wallpaper will change to show that cost in the top-right corner.

**If you get an error:**
- `ModuleNotFoundError` → go back to Part 3, the pip install didn't complete.
- `AuthenticationFailed` or `403` → double check the 4 values in config.json, and make sure the role assignment in Part 4 Step 6 actually completed.
- No cost shown / cost is 0 → this is normal if you haven't spent anything yet this month, or your subscription is a free trial with no cost data yet.

---

## Part 7: Make it run automatically every day

We'll use Windows Task Scheduler so this runs on its own — no need to open anything.

1. Press Windows key, type **Task Scheduler**, open it.
2. Click **Create Task** (not "Create Basic Task", so we get more options).
3. **General tab:**
   - Name: `Azure Cost Wallpaper`
   - Select "Run whether user is logged on or not" only if you don't mind entering your Windows password once for it — otherwise leave "Run only when user is logged on" selected (simpler, and wallpaper changes only make sense when you're logged in anyway).
4. **Triggers tab:**
   - Click **New**.
   - Begin the task: **On a schedule**.
   - Choose **Daily**, or if you want it refreshed a few times a day, choose **Daily** and then also check "Repeat task every: 1 hour, for a duration of: 1 day" in the advanced settings at the bottom.
   - Set a start time, e.g. 9:00 AM.
   - Click OK.
5. **Actions tab:**
   - Click **New**.
   - Action: **Start a program**.
   - Program/script: type `python` (or the full path shown by running `where python` in Command Prompt).
   - Add arguments: `azure_cost_wallpaper.py`
   - Start in: `C:\AzureCostWallpaper` (this is important — it's how the script finds config.json)
   - Click OK.
6. Click **OK** to save the whole task. Enter your Windows password if prompted.

To test the scheduled task immediately: find it in the Task Scheduler Library list, right-click it, and choose **Run**. Your wallpaper should update within a few seconds.

---

## Notes

- The client secret you created in Part 4 will expire after the period you chose (e.g. 12 months). When it does, the script will start failing with an authentication error — just repeat Part 4 Step 5 to create a new secret and update config.json.
- This only shows month-to-date cost (resets to the start of each calendar month). If you'd rather see "cost so far today" or "cost for last 24 hours", that needs a small tweak to the `timeframe` value in the script — let me know if you want that version instead.
- This app only has "Cost Management Reader" access — it cannot see or change any of your actual resources, only billing data.
