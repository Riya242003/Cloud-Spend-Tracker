# Cloud-Spend-Tracker

*Azure spend, right on your desktop.*

I kept forgetting to check my Azure billing dashboard until the invoice showed up as a surprise. Cloud-Spend-Tracker fixes that by quietly painting your month-to-date Azure cost onto your desktop wallpaper, refreshed automatically throughout the day. No dashboard to open, no browser tab to remember — the number is just *there*, every time you look at your screen.

![ Cloud-Spend-Tracker wallpaper example](./AZURECOSTIMAGE.png)

## What it does

CostCanvas talks to the Azure Cost Management API using a read-only service identity, pulls your current month-to-date spend, and renders it as clean overlay text on top of a background image of your choice. A Windows scheduled task keeps it running in the background, so the number you see is never more than an hour or two stale.

## Why I built it

I was checking my Azure cost manually, on my own schedule, which in practice meant "rarely." Cost overruns on cloud resources are easy to miss until they're expensive. Putting the number somewhere I look dozens of times a day — my desktop — turned an occasional chore into a passive habit.

## Features

- Pulls live month-to-date cost from the Azure Cost Management API
- Renders the cost as an overlay on your own wallpaper photo, or a clean dark background
- Runs unattended via Windows Task Scheduler — no manual triggering needed
- Uses a scoped service principal with **Cost Management Reader** access only — it cannot read or modify any actual Azure resources
- Configurable refresh frequency (hourly, daily, or whatever schedule you prefer)

## How it works

```
Azure Cost Management API  →  Python script  →  Pillow image render  →  Windows wallpaper API
```

1. `ClientSecretCredential` authenticates against your Azure AD tenant using a service principal scoped only to cost data.
2. The script queries `ActualCost` for the current billing period (`MonthToDate`).
3. Pillow draws the resulting number, along with a timestamp, onto your chosen background image.
4. The generated image is set as your desktop wallpaper via the Windows `SystemParametersInfoW` API.
5. Task Scheduler re-runs the whole thing on a timer, so the number stays current without you doing anything.

## Tech stack

- Python 3.12
- `azure-identity` / `azure-mgmt-costmanagement` — Azure authentication and billing data
- `Pillow` — image generation
- Windows Task Scheduler — automation
- `ctypes` — native Windows API call to set the wallpaper

## Setup

Full step-by-step instructions — including creating the Azure app registration, assigning the right role, and configuring Task Scheduler — are in [`SETUP.md`](./SETUP.md).

Quick version, if you've done this kind of thing before:

```bash
pip install -r requirements.txt
cp config.example.json config.json   # then fill in your own values
python azure_cost_wallpaper.py
```

## Security notes

- The service principal used here is granted **Cost Management Reader** only — read access to billing data, nothing else.
- `config.json` holds a client secret and is intentionally excluded via `.gitignore`. Never commit real credentials — always use `config.example.json` as the template and keep your actual `config.json` local.
- Client secrets expire on whatever schedule you set in Azure AD (12 months, in my case) — rotate them there and update `config.json` when they do.

## Roadmap / ideas

- [ ] Support for "cost in the last 24 hours" as an alternative to month-to-date
- [ ] Budget threshold alerts (e.g. flash red past a set number)
- [ ] Cross-platform support (macOS wallpaper API, Linux via `feh`/`nitrogen`)
- [ ] Multi-subscription support with a combined total

## License

MIT — do whatever you'd like with it.
