# lidlplus-api

A Python wrapper for the Lidl Plus app API.

This project is a fork of: https://github.com/Andre0512/lidl-plus

---

## Requirements

- Python **3.12+**
- Playwright (plus its required system dependencies)

---

## Installation

1. a) Install the package:

   ```bash
   pip install lidlplus-api[auth]
   ```
   b)
   > If you use an OS/Distro that doesn't support playwright, and you want to use this with the refresh token, install:
   
   
      ```bash
      pip install lidlplus-api
      ```


2. Install Playwright browsers:

   ```bash
   playwright install chromium
   ```

3. Install system dependencies required by Playwright (varies by OS).

---

## Quick start

```python
from lidlplus_api import LidlPlusApi

lidl = LidlPlusApi(
    language="YOUR_LANGUAGE_CODE",
    country="YOUR_COUNTRY_CODE",
    # optional:
    refresh_token="YOUR_REFRESH_TOKEN",
)

lidl.login(email="YOUR_EMAIL", password="YOUR_PASSWORD")
```

---

## Usage

1. Import `lidlplus_api` in your project
2. Use the `LidlPlusApi` methods below

---

## API reference

### Create client

- **Constructor**

  ```python
  lidl = LidlPlusApi(
      language="YOUR_LANGUAGE_CODE",
      country="YOUR_COUNTRY_CODE",
      refresh_token="YOUR_REFRESH_TOKEN",  # optional
  )
  ```

  Initializes the `LidlPlusApi` client.

---

### Authentication

- **Login (Playwright)**

  ```python
  lidl.login(email="YOUR_EMAIL", password="YOUR_PASSWORD")
  ```

  Logs in to your Lidl Plus account using Playwright.

---

### Receipts

- **List receipts (paged, 25 per page)**

  ```python
  lidl.receipts(only_favourite=False, pageNumber=1)
  ```

- **Get a specific receipt**

  ```python
  lidl.receipt(ticket_id)
  ```

  `ticket_id` comes from `lidl.receipts()` (`id` field).

---

### Coupons

- **List coupons for a store**

  ```python
  lidl.coupons(store_id)
  ```

  `store_id` comes from `lidl.get_stores()`.

- **Activate a coupon**

  ```python
  lidl.activate_coupon(coupon_id)
  ```

- **Deactivate a coupon**

  ```python
  lidl.deactivate_coupon(coupon_id)
  ```

  `coupon_id` comes from `lidl.coupons()`.

---

### Coupon Plus (experimental)

- **Start Coupon Plus**

  ```python
  lidl.start_couponplus()
  ```

  EXPERIMENTAL — probably doesn’t work.

- **Coupon Plus status/info**

  ```python
  lidl.couponplus(store_id)
  ```

  DOESN’T WORK — fetches info for the current month’s Coupon Plus (store from `lidl.get_stores()`).

---

### Scratch card / Fortune wheel (purchaseLottery)

- **Promotion details**

  ```python
  lidl.purchaseLottery_details(coupon_id)
  ```

- **Redeem promotion**

  ```python
  lidl.redeem_purchaseLottery(coupon_id)
  ```

- **Promotion status**

  ```python
  lidl.purchaseLottery_status(coupon_id)
  ```

  `coupon_id` comes from:
  `lidl.home(store_id)["purchaseLottery"][0]["id"]`

---

### Loyalty

- **Get loyalty id**

  ```python
  lidl.loyalty_id
  ```

- **Generate loyalty QR code**

  ```python
  lidl.generate_loyalty_id()
  ```

---

### Stores / Offers / Brochures

- **List stores**

  ```python
  lidl.get_stores()
  ```

- **Offers for a store**

  ```python
  lidl.offers(store_id)
  ```

- **Brochures for a store**

  ```python
  lidl.brochures(store_id)
  ```

---

### Translations

- **Get translation keys**

  ```python
  lidl.translations()
  ```

---

### Misc

- **Active coupons count**

  ```python
  lidl.activecoupons_count(store_id)
  ```

- **Home page data**

  ```python
  lidl.home(store_id)
  ```

- **Today’s store schedule**

  ```python
  lidl.store_schedule(store_id)
  ```

- **Store details**

  ```python
  lidl.store_details(store_id)
  ```

---

## Legal Notice

This application is an open source project written in Python, which uses the API of the Lidl Plus application, owned by **Lidl Stiftung & Co. KG**. The application was created solely for educational purposes and is not affiliated with Lidl Stiftung & Co. KG. The creator of the application is not affiliated with Lidl Stiftung & Co. KG. in any way and does not derive any financial benefits from this project. All trademarks, trade names, and logos are the property of their respective owners. Users use the application at their own risk.
