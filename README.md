# lidlplus-api
The Lidl Plus API (in Python)

Fork of https://github.com/Andre0512/lidl-plus
## Installing

Clone this repo `git clone https://github.com/Zsobix/lidlplus-api`

Install all requirements `pip install -r requirements.txt`

Run `playwright install`

Install all dependencies that playwright requires

Done!

## Usage
1. Install Python 3
2. Import "api" in your project
3. ???
4. profit

## Functions
`lidl = api.LidlPlusApi(language="YOUR_LANGUAGE_CODE", country="YOUR_COUNTRY_CODE", (and optionally) refresh_token="YOUR_REFRESH_TOKEN")`

Initialize the LidlPlusApi class

---
`lidl.login(email="YOUR_EMAIL", password="YOUR_PASSWORD")`

Login to your Lidl Plus account using playwright

---
`lidl.receipts(only_favourite=False, pageNumber=1)`

Get all receipts from your account in 25 receipt chunks

---
`lidl.receipt(ticket_id)`

Get the specific receipt with the ticket id (returned from lidl.receipts, id field)

---
`lidl.coupons(store_id)`

Get all coupons from account with the specified store id (returned from lidl.get_stores)

---
`lidl.activate_coupon(coupon_id)`

Activate the specified coupon using the coupon id (returned from lidl.coupons)

---
`lidl.deactivate_coupon(coupon_id)`

Deactivate the specified coupon using the coupon id (returned from lidl.coupons)

---
`lidl.start_couponplus()`

EXPERIMENTAL PROBABLY DOESN'T WORK!!! Starts the coupon plus program for your account

---
`lidl.couponplus(store_id)`

DOESN'T WORK!!! Gets the information for the current month's coupon plus program with the store id (returned from lidl.get_stores)

---
`lidl.purchaseLottery_details(coupon_id)`

Gets the information about the scratch card/fortune wheel promotion with the coupon id (returned from lidl.home(store_id)["purchaseLottery"][0]["id"])

---
`lidl.redeem_purchaseLottery(coupon_id)`

Redeems the specifed scratch card/fortune wheel promotion with the coupon id (returned from lidl.home(store_id)["purchaseLottery"][0]["id"])

---
`lidl.purchaseLottery_status(coupon_id)`

Gets the status (redeemed coupon id, or nothing if no prize) of the scratch card/fortune wheel promotions with the coupon id (returned from lidl.home(store_id)["purchaseLottery"][0]["id"])

---
`lidl.loyalty_id`

Gets the account's loyalty id

---

`lidl.generate_loyalty_id()`

Generates the qr code of the loyalty id

---
`lidl.get_stores()`

Gets all the stores in the your specified country

---
`lidl.offers(store_id)`

Gets all the offers with the store id (returned from lidl.get_stores())

---
`lidl.brochures(store_id)`

Gets all brochures with the store id (returned from lidl.get_stores())

---
`lidl.translations()`

Gets all translation keys and translations in your specified language

---
`lidl.activecoupons_count(store_id)`

Gets the number of active coupons with the store id (returned from lidl.get_stores())

---
`lidl.home(store_id)`

Gets all the home page data when the lidl plus app is loaded

---
`lidl.store_schedule(store_id)`

Gets today's store schedule with the store id (returned from lidl.get_stores())

---
`lidl.store_details(store_id)`

Gets the specified store details with the store id (returned from lidl.get_stores())
