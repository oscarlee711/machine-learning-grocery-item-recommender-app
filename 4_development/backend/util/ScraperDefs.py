import os
import urllib.error
import urllib.request
from datetime import date

import mysql.connector as MySQL
import pandas as Panda
from PIL import Image
from gcloud import storage
from mysql.connector import Error
from playwright.sync_api import sync_playwright, TimeoutError as PTimeout


def ChooseCategories(SiteSoup):
	SelectedCategories = []
	AllCategories = SiteSoup.find_all("a", class_="coles-targeting-ShopCategoriesShopCategoryStyledCategoryContainer")
	for Category in AllCategories:  # This will not yet work for the categories that have precursory screens (e.g. Age restrictions)
		Prompt = f"Do you want to scrape data from the category: {Category.text}\n"
		Response = input(Prompt + "Respond with 'Yes' or 'No'\n")

		if Response == "Yes":
			SelectedCategories.append(Category)
		else:
			continue

	return SelectedCategories  # Every category to be scrapped will be in this array


def ColesDataExtractor(Product, Csv, ID):
	Details = Product.find("h2", class_="product__title")
	Price = Product.find("span", class_="price__value")
	PerPrice = Product.find("span", class_="price__calculation_method")
	ProductLink = Product.find("a", class_="product__link")["href"]
	ProductCode = ProductLink.split("-")[-1]
	ProductPromo = Product.find("span", class_="product_promotion")
	if Details and Price and PerPrice:  # See above
		Details = Details.text.strip()
		Name = Details.split(' | ')[0]
		# Quantity = Details.split(' | ')[1]  # The quantity... if anyone cares
		Price = Price.text.strip()
		PerPrice = PerPrice.text.strip()
		UnitPrice = PerPrice.split(' | ')[0]
		DownPrice = ""
		PromoInfo = ""

		if " | " in PerPrice:
			SpecialPrice = (PerPrice.split(' | ')[1]).split()[:2]
			DownPrice = f"{SpecialPrice[0]} {SpecialPrice[1]}"

		if ProductPromo is not None:
			PromoInfo = ProductPromo.text.strip()

		Csv.writerow([ProductCode, Name, Price, UnitPrice, DownPrice, PromoInfo, ID])


def ColesImageExtractor(Product, Filepath):
	Details = Product.find("h2", class_="product__title")
	Price = Product.find("span", class_="price__value")
	PerPrice = Product.find("span", class_="price__calculation_method")
	ProductLink = Product.find("a", class_="product__link")["href"]
	ProductCode = ProductLink.split("-")[-1]
	ProductImgSrc = f"https://productimages.coles.com.au/productimages/{ProductCode[0]}/{ProductCode}.jpg"
	if Details and Price and PerPrice:  # Ensure item is valid and not out of stock or advertisement
		ImgName = f"{ProductCode}.jpg"
		FullPath = os.path.join(Filepath, ImgName)

		try:
			urllib.request.urlretrieve(ProductImgSrc, FullPath)  # Download the image...
			Img = Image.open(FullPath)
			ImgR = Img.resize((200, 200), Image.ANTIALIAS)  # Resize to 200x200...
			ImgR.save(FullPath)  # and replace the one we downloaded
		except urllib.error.HTTPError as e:
			print(f"HTTPError: {e.code}")


def WooliesCategoryFetch(Url, List):
	with sync_playwright() as playwright:
		Browser = playwright.chromium.launch(headless=False)  # Anti-headless means we cannot be detected
		Page = Browser.new_page()
		Page.goto(Url)

		# Wait for page to load enough
		Page.get_by_text("Browse products").click()
		Page.wait_for_selector("div.category-list")

		Container = Page.locator("a.item")
		Count = Container.count()

		for Item in range(Count):
			Product = Container.nth(Item)
			Prompt = f"Do you want to scrape products from the category: {Product.inner_text()}\n"
			Response = input(Prompt + "Respond with 'Yes' or 'No'\n")

			if Response == "Yes":
				List.append(Product.get_attribute("href"))  # Again... site changes alot, so we can't get normal names
			else:
				continue


def PageCounter(Url):
	with sync_playwright() as playwright:
		Browser = playwright.chromium.launch(headless=False)
		Page = Browser.new_page()
		Page.goto(Url)

		# Wait for page to load enough
		Page.wait_for_selector("span.cartControls-addCart")

		Pages = Page.locator("span.page-count")
		return Pages.inner_text()


def GetWooliesProducts(Url, Sheet, ID):
	with sync_playwright() as playwright:
		Browser = playwright.chromium.launch(headless=False)
		Page = Browser.new_page()
		Page.goto(Url)
		Page.set_default_timeout(15000)  # 15s

		# Wait for the page to load styling
		Page.wait_for_selector("span.cartControls-addCart")
		Container = Page.locator("section.product-tile-v2")
		Count = Container.count()

		for Item in range(Count):
			Product = Container.nth(Item)
			if Product.locator("div.product-tile-unavailable-tag.ng-star-inserted").count() == 0:
				Name = Product.locator("a.product-title-link").inner_text()
				Price = Product.locator("div.primary").inner_text()
				Unit = Product.locator("span.price-per-cup").inner_text()
				PromoInfo1 = ""
				PromoInfo2 = ""
				try:
					if Page.query_selector("div.product-tile-v2--image") is not None:
						ProductImg = Product.locator("div.product-tile-v2--image").get_by_title(Name)
						ImgLink = ProductImg.get_attribute("src")
						ToSelect = ImgLink.split(".jpg")[0]
						Base, Slash, Code = ToSelect.rpartition("/")
				except PTimeout:
					pass
				Page.set_default_timeout(200)  # No need for long times after we get the main stuff
				try:
					if Page.query_selector("span.was-price") is not None:
						DownPrice = Product.locator("span.was-price").inner_text()
						PromoInfo1 = f"WAS {DownPrice}"
				except PTimeout:
					pass

				try:
					if Page.query_selector("div.product-tile-promo-info") is not None:
						PromoInfo2 = Product.locator("div.product-tile-promo-info").inner_text()
						PromoInfo2 = PromoInfo2.split(' - ')[0]
				except PTimeout:
					pass
				Sheet.writerow([Code, Name, Price, Unit, PromoInfo1, PromoInfo2, ID])


def GetWooliesImages(Url, FilePath):
	with sync_playwright() as playwright:
		Browser = playwright.chromium.launch(headless=False)
		Page = Browser.new_page()
		Page.goto(Url)
		Page.set_default_timeout(20000)  # 20s, because images need more time

		Page.wait_for_selector("span.cartControls-addCart")
		Container = Page.locator("section.product-tile-v2")
		Count = Container.count()

		for Item in range(Count):
			Product = Container.nth(Item)
			if Product.locator("div.product-tile-unavailable-tag.ng-star-inserted").count() == 0:
				Name = Product.locator("a.product-title-link").inner_text()
				try:
					if Page.query_selector("div.product-tile-v2--image") is not None:
						ProductImg = Product.locator("div.product-tile-v2--image").get_by_title(Name)
						ImgLink = ProductImg.get_attribute("src")
						ToSelect = ImgLink.split(".jpg")[0]
						Base, Slash, Code = ToSelect.rpartition("/")
						ResizedImg = ImgLink.replace("w=260&h=260", "w=200&h=200")  # Images can be resized by URL
						FullPath = f"{FilePath}{Code}.jpg"

						try:  # We try instead since this will also grab products without images, which we don't want
							urllib.request.urlretrieve(ResizedImg, FullPath)
						except urllib.error.HTTPError as e:
							print(f"HTTPError: {e.code}")
				except PTimeout:
					print("Image Timeout")
					pass


def ImageUploader(Filename, Directory, StoreChoice, Stores):
	os.environ.setdefault("GCLOUD_PROJECT", "sit-22t3-discountmate-46bf512")
	StorageClient = storage.Client.from_service_account_json('creds2.json')
	Bucket = StorageClient.get_bucket("discountmate-item-image")  # Get the right cloud directory
	print("walter")
	Blob = Bucket.blob(f"Storefront/{Stores[StoreChoice - 1]}/{Filename}")
	Blob.upload_from_filename(Directory + Filename)


def DataUploader(Filename, Directory, StoreChoice):
	SQLArgument = None
	if StoreChoice == 1:
		SQLArgument = "INSERT INTO STAGING_COLES_ITEM_PRICE VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
	elif StoreChoice == 2:
		SQLArgument = "INSERT INTO STAGING_WOOLY_ITEM_PRICE VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
	File = f"{Directory}{Filename}"
	Dataframe = Panda.read_csv(File, delimiter=",", usecols=[0, 1, 2, 3, 4, 5, 6], header=None, encoding="cp1252")
	try:
		Connection = MySQL.connect(host="", user="", password="")
		if Connection.is_connected():
			Cursor = Connection.cursor()
			print("Database is connected")
			Cursor.execute("use dcmdb")
			print("Connected to dcmdb")

			rowCount = len(Dataframe.index)

			for i in range(rowCount):
				Df = Dataframe.iloc[i]  # Get row [i]
				ItemID = str(Df[0])
				ItemName = str(Df[1])
				ItemPrice = str(Df[2])
				ItemUnit = str(Df[3])
				ItemWasPrice = str(Df[4])
				ItemPromo = str(Df[5])
				ItemCategory = str(Df[6])
				ItemDate = str(date.today())  # Ideally, we run this right after scraping so having it here is fine
				# Can easily be added during scraping in the case we don't import right after
				Values = (ItemDate, ItemID, ItemName, ItemPrice, ItemUnit, ItemWasPrice, ItemPromo, ItemCategory)
				Cursor.execute(SQLArgument, Values)
				Connection.commit()  # Commit the addition of the row and move on

			Connection.close()
			print("Database connection is closed")
	except Error as e:
		print("Error while connecting to MySQL", e)
