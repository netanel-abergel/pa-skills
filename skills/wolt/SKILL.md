---
name: wolt
description: "Order food from Wolt via browser automation. Use when: owner asks to order food, browse restaurants, reorder a previous order, or check delivery status. Requires one-time cookie setup from a logged-in browser session."
---

# Wolt Skill

Automates food ordering via Wolt's web app using browser automation + saved session cookies.

---

## Minimum Model
Any model. Browser automation is deterministic. Use medium+ model only for natural language parsing (e.g. "order me something from Japanika").

---

## Architecture

Wolt blocks server-side login with hCaptcha. The solution:
1. **One-time setup**: export cookies from a real logged-in browser session
2. **Runtime**: inject cookies into the automated browser — skip login entirely
3. **Order flow**: browse → select → add to cart → checkout (all automated)

---

## Setup (One-Time)

### Step 1: Export cookies from Chrome/Firefox

In Chrome, install the extension **"EditThisCookie"** or **"Cookie-Editor"**, then:
1. Go to wolt.com and log in normally
2. Open the extension → Export → copy JSON
3. Save to `/root/.credentials/wolt-cookies.json`

Or via DevTools:
```javascript
// In Chrome DevTools Console on wolt.com:
JSON.stringify(document.cookie)
```

### Step 2: Verify cookie file exists
```bash
ls /root/.credentials/wolt-cookies.json
```

---

## Cookie Injection (Before Every Session)

```python
import json
from playwright.sync_api import sync_playwright

COOKIES_FILE = "/root/.credentials/wolt-cookies.json"
WOLT_URL = "https://wolt.com/en/isr"

def start_wolt_session():
    with open(COOKIES_FILE) as f:
        cookies = json.load(f)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()
        page.goto(WOLT_URL)
        
        # Verify logged in
        if "Log in" in page.content():
            raise Exception("Cookies expired — need to re-export from browser")
        
        return page, context, browser
```

---

## Core Flows

### 1. Browse Restaurants by Address

```python
def browse_restaurants(page, address: str):
    """Search for restaurants near an address"""
    page.goto("https://wolt.com/en/isr")
    
    # Enter address
    page.fill('[placeholder="Enter delivery address"]', address)
    page.wait_for_selector('[data-test-id="suggestion-item"]', timeout=5000)
    page.click('[data-test-id="suggestion-item"]:first-child')
    page.wait_for_load_state("networkidle")
    
    # Get restaurant list
    restaurants = page.query_selector_all('[data-test-id="venue-card"]')
    return [r.inner_text() for r in restaurants[:10]]
```

### 2. Search for a Specific Restaurant

```python
def find_restaurant(page, name: str):
    """Find a restaurant by name"""
    page.goto(f"https://wolt.com/en/isr/search?q={name}")
    page.wait_for_load_state("networkidle")
    
    results = page.query_selector_all('[data-test-id="venue-card"]')
    for result in results:
        if name.lower() in result.inner_text().lower():
            result.click()
            return True
    return False
```

### 3. Add Item to Cart

```python
def add_to_cart(page, item_name: str):
    """Find an item by name and add to cart"""
    # Search in menu
    items = page.query_selector_all('[data-test-id="product-card"]')
    for item in items:
        if item_name.lower() in item.inner_text().lower():
            item.click()
            page.wait_for_selector('[data-test-id="add-to-cart-button"]')
            page.click('[data-test-id="add-to-cart-button"]')
            return True
    return False
```

### 4. View Cart & Checkout

```python
def checkout(page):
    """Proceed to checkout"""
    page.click('[data-test-id="cart-button"]')
    page.wait_for_selector('[data-test-id="order-submit-button"]')
    
    # Verify order details before confirming
    order_summary = page.query_selector('[data-test-id="order-summary"]')
    return order_summary.inner_text() if order_summary else None
```

---

## Full Order Flow

```python
def order_food(address: str, restaurant: str, item: str):
    """
    Complete order flow:
    1. Load session with cookies
    2. Find restaurant
    3. Add item to cart
    4. Return order summary (DO NOT auto-confirm — always show to owner first)
    """
    page, context, browser = start_wolt_session()
    
    try:
        # Find restaurant
        found = find_restaurant(page, restaurant)
        if not found:
            return f"❌ לא מצאתי '{restaurant}' ב-Wolt"
        
        # Add item
        added = add_to_cart(page, item)
        if not added:
            return f"❌ לא מצאתי '{item}' בתפריט"
        
        # Get summary
        summary = checkout(page)
        return f"✅ נוסף לסל:\n{summary}\n\nלאשר הזמנה?"
        
    finally:
        browser.close()
```

---

## Agent Interface

### Natural Language Parsing

When owner says:
- "תזמיני לי פיצה מ-Pizza Hut" → `order_food(default_address, "Pizza Hut", "pizza")`
- "מה יש ב-Aroma?" → `find_restaurant + list_menu`
- "תזמיני שוב את מה שהזמנתי אחרון" → check last order from memory

### Always Ask Before Confirming

**NEVER auto-submit an order.** Always:
1. Show order summary (items, price, ETA)
2. Wait for explicit "כן" / "אשר" from owner
3. Only then click confirm

```python
# ✅ Correct flow:
summary = order_food(address, restaurant, item)
# → report to owner, wait for confirmation
# → only then: page.click('[data-test-id="order-submit-button"]')
```

---

## Memory

Save last order to memory for reorder support:
```bash
/opt/ocana/openclaw/workspace/memory/wolt-last-order.json
```

```json
{
  "restaurant": "Pizza Hut",
  "item": "Pepperoni Pizza",
  "address": "Rothschild 45, Tel Aviv",
  "ordered_at": "2026-04-02T10:30:00Z",
  "total": "₪89"
}
```

---

## Default Delivery Address

Store owner's default address in memory:
```bash
/opt/ocana/openclaw/workspace/memory/wolt-settings.json
```

```json
{
  "default_address": "...",
  "preferred_payment": "saved card"
}
```

---

## Limitations

| Limitation | Workaround |
|---|---|
| hCaptcha blocks server login | Use exported cookies (one-time setup) |
| Cookies expire | Re-export from browser when prompted |
| No official consumer API | All automation via browser |
| Address must be exact | Use autocomplete suggestion, not free text |

---

## Cost Tips

- All Wolt interactions are browser-based — no LLM tokens during execution
- Only parse natural language once per request
- Cache restaurant menus if browsing repeatedly
- Never re-login if cookies are valid

---

## Integration

- **With owner-briefing**: mention if a reorder is possible ("Ordered last from Pizza Hut — reorder?")
- **With memory**: save preferences, last order, default address
- **With calendar**: could auto-order lunch before long meetings
