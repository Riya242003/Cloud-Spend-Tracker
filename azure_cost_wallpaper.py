"""
Azure Cost on Wallpaper
------------------------
Fetches your Azure month-to-date cost using the Cost Management API,
draws it on an image, and sets that image as your Windows desktop wallpaper.

Run manually with:
    python azure_cost_wallpaper.py

Or schedule it with Windows Task Scheduler (see README.md for steps).
"""

"""
Azure Cost on Wallpaper
------------------------
Fetches your Azure month-to-date cost using the Cost Management API,
draws it on an image, and sets that image as your Windows desktop wallpaper.

Run manually with:
    python azure_cost_wallpaper.py

Or schedule it with Windows Task Scheduler (see README.md for steps).
"""

import json
import os
import ctypes
from datetime import datetime

from azure.identity import ClientSecretCredential
from azure.mgmt.costmanagement import CostManagementClient
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
OUTPUT_IMAGE_PATH = os.path.join(SCRIPT_DIR, "wallpaper_with_cost.png")


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def get_month_to_date_cost(config):
    """Ask Azure how much you've spent so far this month."""
    credential = ClientSecretCredential(
        tenant_id=config["tenant_id"],
        client_id=config["client_id"],
        client_secret=config["client_secret"],
    )
    client = CostManagementClient(credential)
    scope = f"/subscriptions/{config['subscription_id']}"

    query = {
        "type": "ActualCost",
        "timeframe": "MonthToDate",
        "dataset": {
            "granularity": "None",
            "aggregation": {
                "totalCost": {
                    "name": "PreTaxCost",
                    "function": "Sum",
                }
            },
        },
    }

    result = client.query.usage(scope=scope, parameters=query)
    rows = result.rows
    columns = [c.name for c in result.columns]

    if not rows:
        return 0.0, "USD"

    cost_index = columns.index("PreTaxCost") if "PreTaxCost" in columns else 0
    currency_index = columns.index("Currency") if "Currency" in columns else None

    total_cost = rows[0][cost_index]
    currency = rows[0][currency_index] if currency_index is not None else "USD"
    return round(total_cost, 2), currency


def get_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def create_wallpaper_image(cost, currency, base_wallpaper_path=None):
    width, height = 1920, 1080

    if base_wallpaper_path and os.path.exists(base_wallpaper_path):
        img = Image.open(base_wallpaper_path).convert("RGB").resize((width, height))
    else:
        img = Image.new("RGB", (width, height), color=(18, 18, 28))

    draw = ImageDraw.Draw(img, "RGBA")

    main_text = f"Azure Cost (MTD): {currency} {cost}"
    updated_text = f"Updated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}"

    try:
        font_big = ImageFont.truetype("C:\\Windows\\Fonts\\ariali.ttf", 24)
        font_small = ImageFont.truetype("C:\\Windows\\Fonts\\ariali.ttf", 18)
    except OSError:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    margin = 50
    text_w, text_h = get_text_size(draw, main_text, font_big)
    x = width - text_w - margin - 20
    y = margin

    # semi-transparent box behind the text so it stays readable on any wallpaper
    draw.rectangle(
        [x - 20, y - 15, x + text_w + 20, y + text_h + 50],
        fill=(0, 0, 0, 160),
    )
    draw.text((x, y), main_text, font=font_big, fill=(255, 255, 255))
    draw.text((x, y + text_h + 8), updated_text, font=font_small, fill=(210, 210, 210))

    img.save(OUTPUT_IMAGE_PATH)
    return OUTPUT_IMAGE_PATH


def set_wallpaper(image_path):
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, image_path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )


def main():
    config = load_config()
    cost, currency = get_month_to_date_cost(config)
    base_wallpaper = config.get("base_wallpaper_path") or None
    image_path = create_wallpaper_image(cost, currency, base_wallpaper)
    set_wallpaper(image_path)
    print(f"Done. Azure month-to-date cost: {currency} {cost}")


if __name__ == "__main__":
    main()

