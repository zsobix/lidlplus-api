import base64
import html
import logging
import re
from datetime import datetime, timedelta, timezone
import string
import requests
import hashlib
from jwkest import b64e
from secrets import choice
import uuid
try:
    from playwright.sync_api import sync_playwright
except:
    print("Playwright not found. Assuming this is currently being used in MSYS")
import time
import qrcode
import random
from zoneinfo import ZoneInfo
class LidlPlusApi:

    def __init__(self, language, country, refresh_token=""):
        self._login_url = ""
        self._code_verifier = ""
        self._code_challenge = ""
        self._refresh_token = refresh_token
        self._expires = None
        self._token = ""
        self._country = country.upper()
        self._language = language.lower()
        self._basech = string.ascii_letters + string.digits + "-._~"

    @property
    def refresh_token(self):
        """Lidl Plus api refresh token"""
        return self._refresh_token

    @property
    def token(self):
        """Current token to query api"""
        return self._token
    def add_code_challenge(self):
            cv_len = 64  # Use default

            code_verifier = "".join([choice(self._basech) for _ in range(cv_len)])
            _cv = code_verifier.encode("ascii")

            _method = "S256"

            try:
                _h = hashlib.sha256(_cv).digest()
                code_challenge = b64e(_h).decode("ascii")
            except KeyError:
                raise Unsupported("PKCE Transformation method:{}".format(_method)) from None

            # TODO store code_verifier

            return (
                {"code_challenge": code_challenge, "code_challenge_method": _method},
                code_verifier,
            )
    def _register_oauth_client(self):
        if self._login_url:
            return self._login_url
        self._code_challenge, self._code_verifier = self.add_code_challenge()
        self._login_url = f"https://accounts.lidl.com/connect/authorize/callback?client_id=LidlPlusNativeClient&response_type=code&scope=openid profile offline_access lpprofile lpapis&redirect_uri=com.lidlplus.app://callback&code_challenge={self._code_challenge["code_challenge"]}&code_challenge_method=S256"
        return self._login_url


    def _auth(self, payload):
        default_secret = base64.b64encode(f"LidlPlusNativeClient:secret".encode()).decode() # TGlkbFBsdXNOYXRpdmVDbGllbnQ6c2VjcmV0
        headers = {
            "Authorization": f"Basic {default_secret}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        kwargs = {"headers": headers, "data": payload, "timeout": 10}
        response = requests.post(f"https://accounts.lidl.com/connect/token", **kwargs).json()
        self._expires = datetime.now(timezone.utc) + timedelta(seconds=response["expires_in"])
        self._token = response["access_token"]
        self._refresh_token = response["refresh_token"]

    def _renew_token(self):
        payload = {"refresh_token": self._refresh_token, "grant_type": "refresh_token"}
        return self._auth(payload)

    def _authorization_code(self, code):
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": f"com.lidlplus.app://callback",
            "code_verifier": self._code_verifier,
        }
        return self._auth(payload)

    @property
    def _register_link(self):
        args = {
            "Country": self._country,
            "language": f"{self._language}-{self._country}",
        }
        params = "&".join([f"{key}={value}" for key, value in args.items()])
        return f"{self._register_oauth_client()}&{params}"
    
    @property
    def _login_form_link(self):
        self._form_link = f"https://accounts.lidl.com/Account/Login?ReturnUrl=/connect/authorize/callback?client_id=LidlPlusNativeClient&response_type=code&scope=openid profile offline_access lpprofile lpapis&redirect_uri=com.lidlplus.app://callback&code_challenge={self._code_challenge["code_challenge"]}&code_challenge_method=S256&Country={self._country}&language={self._language}-{self._country}"
        return self._form_link

    def _api_link(self, requested):
        url = f"https://appgateway.lidlplus.com/app/v23/{self._country}/{requested}"
        return url

    def _parse_code(self, page):
        with page.expect_response("https://accounts.lidl.com/connect/authorize/**") as response:
                    authlink = response.value.all_headers()["location"]
                    authlink = authlink.replace("&", "?")
                    authlist = authlink.split("?")
                    authcode = authlist[1].replace("code=", "")
                    return authcode

    #@staticmethod
    #def _accept_legal_terms(browser, wait, accept=True):
    #    wait.until(expected_conditions.visibility_of_element_located((By.ID, "checkbox_Accepted"))).click()
    #    if not accept:
    #        title = browser.find_element(By.TAG_NAME, "h2").text
    #    browser.find_element(By.TAG_NAME, "button").click()

    #@staticmethod
    #def _check_input_error(browser):
    #    if errors := browser.find_elements(By.CLASS_NAME, "input-error-message"):
    #        for error in errors:
    #            if error.text:
    #                raise LoginError(error.text)

    def _check_login_error(self, response):
        regx = re.search(r"https:\/\/accounts.lidl.com\/Account\/Login.*", response.request.redirected_from.redirected_to.url)
        if not regx:
                raise Exception("LoginError")

    #def _check_2fa_auth(self, browser, wait, verify_mode="phone", verify_token_func=None):
    #    if verify_mode not in ["phone", "email"]:
    #        raise ValueError(f'Unknown 2fa-mode "{verify_mode}" - Only "phone" or "email" supported')
    #    response = browser.wait_for_request(f"https://accounts.lidl.com/Account/Login.*", 10).response
    #    if "/connect/authorize/callback" not in response.headers.get("Location"):
    #        element = wait.until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, verify_mode)))
    #        element.find_element(By.TAG_NAME, "button").click()
    #        verify_code = verify_token_func()
    #        browser.find_element(By.NAME, "VerificationCode").send_keys(verify_code)
    #        self._click(browser, (By.CLASS_NAME, "role_next"))

    def login(self, email, password, **kwargs):
        """Simulate app auth"""
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=False)
            page = browser.new_page()
            response = page.goto(self._register_link)
            page.wait_for_timeout(random.randint(476, 975))
            page.get_by_test_id("button-primary").click()
            page.wait_for_timeout(random.randint(476, 975))
            page.get_by_test_id("input-email").fill(email)
            page.wait_for_timeout(random.randint(476, 975))
            page.get_by_test_id("login-input-password").click()
            page.wait_for_timeout(random.randint(476, 975))
            page.get_by_test_id("login-input-password").fill(password)
            page.wait_for_timeout(random.randint(476, 975))
            page.get_by_test_id("button-primary").click()
            self._check_login_error(response)
            authcode = self._parse_code(page)
            browser.close()
            self._authorization_code(authcode)

    def _default_headers(self, requiresCountryAndStoreID=False, store_id="", iscoupons=False, ishome=False, requiresStoreIDs=False):
        if (not self._token and self._refresh_token) or datetime.now(timezone.utc) >= self._expires:
            self._renew_token()
        if not self._token:
            raise MissingLogin("You need to login!")
        if requiresCountryAndStoreID:
            return {
                "Authorization": f"Bearer {self._token}",
                "App-Version": "16.43.4",
                "Operating-System": "Android",
                "App": "com.lidl.eci.lidlplus",
                "Accept-Language": self._language,
                "User-Agent": "okhttp/5.3.2",
                "OS-Version": "16",
                "Model": "sdk_gphone64_x86_64",
                "Brand": "Google",
                "deviceid": "f7a31c44276c0651",
                "country": self._country,
                "store-id": store_id
            }
        elif iscoupons:
            return {
                "Authorization": f"Bearer {self._token}",
                "App-Version": "16.43.4",
                "Operating-System": "Android",
                "App": "com.lidl.eci.lidlplus",
                "Accept-Language": self._language,
                "User-Agent": "okhttp/5.3.2",
                "OS-Version": "16",
                "Model": "sdk_gphone64_x86_64",
                "Brand": "Google",
                "deviceid": "f7a31c44276c0651",
                "country": self._country,
                "action-location": "app_couponslist"
            }
        elif ishome:
            return {
                "Authorization": f"Bearer {self._token}",
                "App-Version": "16.43.4",
                "Operating-System": "Android",
                "App": "com.lidl.eci.lidlplus",
                "Accept-Language": self._language,
                "User-Agent": "okhttp/5.3.2",
                "OS-Version": "16",
                "Model": "sdk_gphone64_x86_64",
                "Brand": "Google",
                "deviceid": "f7a31c44276c0651",
                "homeId": "mainHome",
                "currentDate": datetime.now().isoformat(),
                "Host": "home.lidlplus.com",
                "isOptionalUpdate": "false",
                "IsPushEnabled": "false",
                "IsOneApp": "false",
                "SessionId": str(uuid.uuid4())
            }
        elif requiresStoreIDs:
            return {
                "Authorization": f"Bearer {self._token}",
                "App-Version": "16.43.4",
                "Operating-System": "Android",
                "App": "com.lidl.eci.lidlplus",
                "Accept-Language": self._language,
                "User-Agent": "okhttp/5.3.2",
                "OS-Version": "16",
                "Model": "sdk_gphone64_x86_64",
                "Brand": "Google",
                "deviceid": "f7a31c44276c0651",
                "storesIds": store_id
            }
        else:
            return {
                "Authorization": f"Bearer {self._token}",
                "App-Version": "16.43.4",
                "Operating-System": "Android",
                "App": "com.lidl.eci.lidlplus",
                "Accept-Language": self._language,
                "User-Agent": "okhttp/5.3.2",
                "OS-Version": "16",
                "Model": "sdk_gphone64_x86_64",
                "Brand": "Google",
                "deviceid": "f7a31c44276c0651",
                "Date": datetime.now(ZoneInfo("Europe/Budapest")).strftime("%a, %d %b %Y %H:%M:%S GMT")
            }

    def receipts(self, only_favorite=False, pageNumber=1):
        #url = f"https://tickets.lidlplus.com/api/v2/{self._country}/tickets"
        #kwargs = {"headers": self._default_headers(), "timeout": 10}
        #ticket = requests.get(f"{url}?pageNumber=1&onlyFavorite={only_favorite}", **kwargs).json()
        #tickets = ticket["tickets"]
        #for i in range(2, int(ticket["totalCount"] / ticket["size"] + 2)):
        #    tickets += requests.get(f"{url}?pageNumber={i}", **kwargs).json()["tickets"]
        #return tickets
        url = f"https://tickets.lidlplus.com/api/v2/{self._country}/tickets?pageNumber={pageNumber}&onlyFavorite={only_favorite}"
        kwargs = {"headers": self._default_headers(), "timeout": 10}
        return requests.get(url, **kwargs).json()

    def receipt(self, ticket_id):
        url = f"https://tickets.lidlplus.com/api/v3/{self._country}/tickets/{ticket_id}"
        kwargs = {"headers": self._default_headers(), "timeout": 10}
        return requests.get(url, **kwargs).json()

    def coupons(self, store_id):
        url = "https://coupons.lidlplus.com/app/api/v4/promotionslist"
        kwargs = {"headers": self._default_headers(requiresCountryAndStoreID=True, store_id=store_id), "timeout": 10}
        return requests.get(url, **kwargs).json()

    def activate_coupon(self, coupon_id):
        url = f"https://coupons.lidlplus.com/app/api/v2/promotions/{coupon_id}/activation" # id in response
        kwargs = {"headers": self._default_headers(iscoupons=True), "timeout": 10}
        return requests.post(url, json={"articleSelection":[]}, **kwargs).status_code == 200

    def deactivate_coupon(self, coupon_id):
        url = f"https://coupons.lidlplus.com/app/api/v2/promotions/{coupon_id}/activation"
        kwargs = {"headers": self._default_headers(iscoupons=True), "timeout": 10}
        return requests.delete(url, **kwargs).status_code == 200
    def start_couponplus(self, promotion_id="1870d40b-4249-42c0-a3b0-ea28c0df895e"):
        url = f"https://couponplus.lidlplus.com/api/v4/{self._country}/user/promotions/{promotion_id}/start"
        kwargs = {"headers": self._default_headers(), "timeout": 10}
        return requests.patch(url, **kwargs)
    def couponplus(self, store_id):
        url = f"https://coupons.lidlplus.com/app/api/v2/promotions/titles?ids=4a770579-87b8-4e28-a8d0-22bc8d10b533&ids=38cff59c-72e8-43f6-9eee-b0b198946109&ids=05d8879d-b557-48f5-b028-330becd5df3e&ids=5ef13122-7427-47cf-bd75-ad1733eea001"
        kwargs = {"headers": self._default_headers(requiresCountryAndStoreID=True, store_id=store_id), "timeout": 10}
        return requests.get(url, **kwargs).text

    def purchaseLottery_details(self, coupon_id):
        url = f"https://purchaselottery.lidlplus.com/api/v1/{self._country}/lotteries/{coupon_id}"
        kwargs = {"headers": self._default_headers(), "timeout": 10}
        return requests.get(url, **kwargs).json()

    def redeem_purchaseLottery(self, coupon_id):
        url = f"https://purchaselottery.lidlplus.com/api/v1/{self._country}/lotteries/{coupon_id}/redeemed"
        kwargs = {"headers": self._default_headers(), "timeout": 10}
        return requests.patch(url, **kwargs).status_code == 202

    def purchaseLottery_status(self, coupon_id):
        url = f"https://purchaselottery.lidlplus.com/api/v1/{self._country}/lotteries/{coupon_id}/redeemed/status"
        kwargs = {"headers": self._default_headers(), "timeout": 10}
        return requests.get(url, **kwargs).text

    @property
    def loyalty_id(self, store_id=""):
        url = f"https://profile.lidlplus.com/api/v1/upsertProfile" # or https://profile.lidlplus.com/api/v1/updateCountryInfo
        kwargs = {"json": {"country_code": self._country, "language": self._country, "store_id": store_id}, "headers": self._default_headers(), "timeout": 10}
        return requests.post(url, **kwargs).json()["loyaltyId"]

    def generate_loyalty_qr(self):
        img = qrcode.make(self.loyalty_id)
        img.save("loyalty_id.png")

    def get_stores(self):
        url = f"https://stores.lidlplus.com/api/v4/{self._country}"
        return requests.get(url).json()

    def offers(self, store_id):
        url = f"https://offers.lidlplus.com/app/api/v4/{self._country}/{store_id}/offers"
        kwargs = {"headers": self._default_headers(), "timeout": 10}
        return requests.get(url, **kwargs).json()

    def brochures(self, store_id):
        url = f"https://brochures.lidlplus.com/api/v2/{self._country}/Brochures?store={store_id}"
        kwargs = {"headers": self._default_headers(), "timeout": 10}
        return requests.get(url, **kwargs).json()

    def translations(self):
        url = f"https://profile.lidl.com/api/translations?country={self._language}&language={self._language}-{self._country}"
        return requests.get(url).json()
    
    def activecoupons_count(self, store_id):
        url = "https://coupons.lidlplus.com/app/api/v1/promotionscount"
        kwargs = {"headers": self._default_headers(requiresCountryAndStoreID=True, store_id=store_id), "timeout": 10}
        return requests.get(url, **kwargs).json()

    def home(self, store_id):
        url = f"https://home.lidlplus.com/api/v2/{self._country}/home/logged"
        kwargs = {"headers": self._default_headers(ishome=True), "timeout": 10}
        return requests.post(url,json={"storeId":store_id,"modules":[{"moduleName":"homeMessage","aggregateVersion":1},{"moduleName":"usualStoreV2","aggregateVersion":1},{"moduleName":"businessModels","aggregateVersion":1},{"moduleName":"tipcards","aggregateVersion":1},{"moduleName":"banners","aggregateVersion":1},{"moduleName":"selfScanningSession","aggregateVersion":1},{"moduleName":"clickAndPickOrderStatus","aggregateVersion":1},{"moduleName":"clickAndPick","aggregateVersion":1},{"moduleName":"stampCardLottery","aggregateVersion":1},{"moduleName":"stampCardRewards","aggregateVersion":1},{"moduleName":"stampCardBenefits","aggregateVersion":2},{"moduleName":"purchaseLottery","aggregateVersion":1},{"moduleName":"openGift","aggregateVersion":1},{"moduleName":"couponPlus","aggregateVersion":3},{"moduleName":"promotions","aggregateVersion":4},{"moduleName":"bannersVideo","aggregateVersion":1},{"moduleName":"offers","aggregateVersion":4},{"moduleName":"WorldOfNeeds","aggregateVersion":1},{"moduleName":"digitalLeafletv2_combined","aggregateVersion":1},{"moduleName":"partnersBenefits","aggregateVersion":1},{"moduleName":"featuredProducts","aggregateVersion":1},{"moduleName":"recipes","aggregateVersion":1},{"moduleName":"homeLegalDisclaimer","aggregateVersion":1},{"moduleName":"usualStoreHeader","aggregateVersion":1}]}, **kwargs).json()
    
    def store_schedule(self, store_id):
        url = f"https://stores.lidlplus.com/api/v3/schedule/{store_id}?date={datetime.now().strftime("%Y-%m-%d")}"
        kwargs = {"headers": self._default_headers(), "timeout": 10}
        return requests.get(url, **kwargs).json()
    def store_details(self, store_id):
        url = f"https://stores.lidlplus.com/api/v5/{self._country}/details"
        kwargs = {"headers": self._default_headers(requiresStoreIDs=True, store_id=store_id), "timeout": 10}
        return requests.get(url, **kwargs).json()
    
    #def get_coupon_details(self, coupon_id):
    #    url = f"https://coupons.lidlplus.com/app/api/v4/promotionsdetails/{coupon_id}"
    #    kwargs = {"headers": self._default_headers(requiresCountryAndStoreID=True), "timeout": 10}
    #    return requests.get(url, **kwargs).text
