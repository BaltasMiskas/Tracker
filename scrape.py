import requests
import json
import os
from datetime import datetime

# 1. Expanded to track categories across BOTH web properties
COLLECTIONS = {
    # --- MagicLinen Bedding ---
    "MagicLinen - Bedding": "https://magiclinen.com/collections/linen-bedding/products.json?limit=250",
    "MagicLinen - Clearance": "https://magiclinen.com/collections/clearance/products.json?limit=250",
    
    # --- MagicLinen Clothing (Split to capture everything!) ---
    "MagicLinen - Women's Clothing": "https://magiclinen.com/collections/womens-clothing/products.json?limit=250",
    "MagicLinen - Men's Clothing": "https://magiclinen.com/collections/mens-clothing/products.json?limit=250",
    "MagicLinen - Linen Tops": "https://magiclinen.com/collections/linen-tops/products.json?limit=250",
    
    # --- No More Accessories ---
    "NoMoreAccessories - Rings": "https://nomoreaccessories.com/collections/rings/products.json?limit=250",
    "NoMoreAccessories - Earrings": "https://nomoreaccessories.com/collections/earrings/products.json?limit=250",
    "NoMoreAccessories - Outlet": "https://nomoreaccessories.com/collections/outlet/products.json?limit=250"
}

def fetch_current_stock():
    current_data = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for category, url in COLLECTIONS.items():
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                products = response.json().get('products', [])
                
                # Determine standard base domain for structural hyperlinks
                base_domain = "https://magiclinen.com" if "MagicLinen" in category else "https://nomoreaccessories.com"
                
                for p in products:
                    product_title = p['title']
                    product_url = f"{base_domain}/products/{p['handle']}"
                    image_url = p['images'][0]['src'] if p.get('images') else ""
                    
                    for v in p['variants']:
                        variant_title = v['title']
                        # Namespace item identifiers to avoid name collisions across properties
                        unique_id = f"[{category.split(' - ')[0]}] {product_title} ({variant_title})"
                        
                        current_data[unique_id] = {
                            "product_name": product_title,
                            "variant_name": variant_title,
                            "price": float(v['price']),
                            "available": v['available'],
                            "url": product_url,
                            "image": image_url,
                            "category": category
                        }
        except Exception as e:
            print(f"Error scraping {category}: {e}")
            
    return current_data

def generate_html(changes, total_tracked):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M local time")
    
    cards_html = ""
    if not changes:
        cards_html = "<div class='no-changes'>🎉 No price or availability updates detected in the last 24 hours.</div>"
    else:
        for item in changes:
            badge_class = "badge-alert" if "Stock" in item['type'] else "badge-price"
            
            cards_html += f"""
            <div class="card">
                <img src="{item['image']}" alt="{item['name']}">
                <div class="card-content">
                    <span class="category-tag">{item['category']}</span>
                    <h3>{item['name']}</h3>
                    <p class="change-detail">
                        <span class="{badge_class}">{item['type']}</span> 
                        {item['details']}
                    </p>
                    <a href="{item['url']}" target="_blank" class="buy-btn">View Store ↗</a>
                </div>
            </div>
            """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Store Price & Stock Monitor</title>
    <style>
        :root {{ --bg: #faf9f6; --text: #2b2b2b; --card-bg: #ffffff; --primary: #5c6370; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        header {{ border-bottom: 1px solid #e0dad4; padding-bottom: 20px; margin-bottom: 30px; }}
        h1 {{ margin: 0 0 10px 0; font-weight: 400; color: #3b3f46; }}
        .meta {{ font-size: 0.9rem; color: #777; margin: 0; }}
        .grid {{ display: grid; grid-template-columns: 1fr; gap: 20px; }}
        .card {{ background: var(--card-bg); border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); display: flex; overflow: hidden; border: 1px solid #ede9e4; }}
        .card img {{ width: 120px; height: 120px; object-fit: cover; background: #f0f0f0; }}
        .card-content {{ padding: 15px; flex: 1; position: relative; }}
        .category-tag {{ font-size: 0.75rem; text-transform: uppercase; tracking-letter: 1px; color: #d4a373; font-weight: bold; display: block; margin-bottom: 5px; }}
        h3 {{ margin: 0 0 10px 0; font-size: 1.1rem; font-weight: 500; padding-right: 120px; }}
        .change-detail {{ margin: 0 0 15px 0; font-size: 0.95rem; }}
        .badge-price {{ background: #e2f0d9; color: #385723; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85rem; }}
        .badge-alert {{ background: #fce4d6; color: #c65911; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85rem; }}
        .buy-btn {{ position: absolute; right: 15px; bottom: 15px; font-size: 0.85rem; text-decoration: none; color: var(--primary); border: 1px solid var(--primary); padding: 6px 12px; border-radius: 4px; transition: all 0.2s; }}
        .buy-btn:hover {{ background: var(--primary); color: white; }}
        .no-changes {{ background: white; padding: 30px; text-align: center; border-radius: 8px; border: 1px dashed #ccc; color: #666; }}
        @media(max-width: 600px) {{
            .card {{ flex-direction: column; }}
            .card img {{ width: 100%; height: 180px; }}
            .buy-btn {{ position: static; display: inline-block; margin-top: 10px; }}
            h3 {{ padding-right: 0; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Combined Brand Monitor</h1>
            <p class="meta">Tracking {total_tracked} variants across properties • Checked: {timestamp}</p>
        </header>
        <main class="grid">
            {cards_html}
        </main>
    </div>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def main():
    current_stock = fetch_current_stock()
    changes = []
    
    old_stock = {}
    if os.path.exists("history.json"):
        try:
            with open("history.json", "r", encoding="utf-8") as f:
                old_stock = json.load(f)
        except Exception:
            pass

    for unique_id, info in current_stock.items():
        if unique_id in old_stock:
            old_item = old_stock[unique_id]
            
            if info['price'] != old_item['price']:
                change_type = "Price Drop 📉" if info['price'] < old_item['price'] else "Price Increase 📈"
                changes.append({
                    "name": unique_id,
                    "type": change_type,
                    "details": f"Was €{old_item['price']:.2f} → Now <strong>€{info['price']:.2f}</strong>",
                    "url": info['url'],
                    "image": info['image'],
                    "category": info['category']
                })
                
            if info['available'] != old_item['available']:
                change_type = "Back In Stock ✨" if info['available'] else "Sold Out ❌"
                changes.append({
                    "name": unique_id,
                    "type": change_type,
                    "details": f"Status updated to {'Available' if info['available'] else 'Out of stock'}",
                    "url": info['url'],
                    "image": info['image'],
                    "category": info['category']
                })

    generate_html(changes, len(current_stock))
    
    with open("history.json", "w", encoding="utf-8") as f:
        json.dump(current_stock, f, indent=2)

if __name__ == "__main__":
    main()
