import csv
import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
from playwright.sync_api import TimeoutError as PTimeout

import ScraperDefs

Choices = ["Upload Data from Store", "Upload Images from Store", "Scrape data from Coles", "Scrape images from Coles",
           "Scrape data from Woolworths", "Scrape images from Woolworths"]

ColesURL = "https://www.coles.com.au"  # These are the directories that will be in use for the program
ColesDataPath = ""  # Store directories cannot be merged, they must be kept separate
ColesImgPath = ""

WoolworthsURL = "https://www.woolworths.com.au"
WoolworthsDataPath = ""
WoolworthsImgPath = ""


def Choose(List):
	print("Current working directories are:\n"
	      f"Coles Data Directory: {ColesDataPath}\n"
	      f"Coles Image Directory: {ColesImgPath}\n"
	      f"Woolworths Data Directory: {WoolworthsDataPath}\n"
	      f"Woolworths Image Directory: {WoolworthsImgPath}\n")

	if ColesDataPath == "" or ColesImgPath == "" or WoolworthsDataPath == "" or WoolworthsImgPath == "":
		print("You must specify a file path for all data routes.")
		raise Exception

	print("Choose number from the following:")
	for Index, Item in enumerate(List):
		print(f'{Index + 1}) {Item}')

	while True:  # Some verification
		try:
			Answer = int(input("What do you choose: "))
			if Answer < 1 or Answer > len(List):
				print("That's not an option.")
				continue
			else:
				return Answer
		except ValueError:
			print("That's not an option.")
			continue


Choice = Choose(Choices)

# ----------------------------------------------------------------------------------------------------------------------

if Choice == 1:
	Directory = None
	Stores = ["Coles", "Woolworths"]
	StoreChoice = Choose(Stores)

	if StoreChoice == 1:
		Directory = ColesDataPath
	elif StoreChoice == 2:
		Directory = WoolworthsDataPath

	Files = (File for File in os.listdir(Directory)  # This will get the files in the directory and exclude any folders
	         if os.path.isfile(os.path.join(Directory, File)))
	for Filename in Files:
		ScraperDefs.DataUploader(Filename, Directory, StoreChoice)

# ----------------------------------------------------------------------------------------------------------------------

elif Choice == 2:
	Directory = None
	Stores = ["Coles", "Woolworths"]
	StoreChoice = Choose(Stores)

	if StoreChoice == 1:
		Directory = ColesImgPath
	elif StoreChoice == 2:
		Directory = WoolworthsImgPath

	for Filename in os.listdir(
		Directory):  # Go through all files in the image directory and upload to respective directory (No distinction for image files)
		print("Starting...")
		ScraperDefs.ImageUploader(Filename, Directory, StoreChoice, Stores)
		print("Done")

# ----------------------------------------------------------------------------------------------------------------------

elif Choice == 3:
	Options = Options()
	Options.add_experimental_option("excludeSwitches", ["enable-automation"])
	Options.add_experimental_option('useAutomationExtension', False)
	Driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=Options)
	stealth(Driver, languages=["en-GB", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.",
	        renderer="Intel Iris OpenGL Engine", fix_hairline=True)  # Permits greater scope of exploration/protection

	Driver.get(ColesURL + "/browse")
	SiteSoup = BeautifulSoup(Driver.page_source, "html.parser")
	SelectCategories = ScraperDefs.ChooseCategories(SiteSoup)

	for Category in SelectCategories:  # Go through every category we want to scrape
		CategoryLink = ColesURL + (Category.get("href"))
		Filename = Category.text + ".csv"  # Create data file
		Filepath = ColesDataPath + Filename
		if os.path.exists(Filepath):  # Duplicates will not be created automatically, they will be replaced
			os.remove(Filepath)

		if CategoryLink is not None:  # Since we have a category specifier, we need to manually set for now
			CategoryID = None
			if ("Bakery" == Category.text) or ("Pantry" == Category.text):
				CategoryID = 1
			elif "Household" == Category.text:
				CategoryID = 2
			elif "Fruit & Vegetables" == Category.text:
				CategoryID = 3
			elif "Dairy, Eggs & Fridge" == Category.text:
				CategoryID = 4
			elif "Drinks" == Category.text:
				CategoryID = 5
			elif "Frozen" == Category.text:
				CategoryID = 6
			elif "Liquor" == Category.text:
				CategoryID = 7
			elif ("Meat & Seafood" == Category.text) or ("Deli" == Category.text):
				CategoryID = 8

			Driver.get(CategoryLink)
			while True:
				PageSoup = BeautifulSoup(Driver.page_source, "html.parser")
				Products = PageSoup.find_all("header", class_="product__header")

				with open(Filepath, "a", newline="") as Sheet:
					Writer = csv.writer(Sheet)
					for CurrentProduct in Products:  # Write every product's detail into the category data file
						ScraperDefs.ColesDataExtractor(CurrentProduct, Writer, CategoryID)

					try:  # Because Coles is cringe, we have to determine pages from the pagination element...
						Pagination = PageSoup.find("ul", class_="coles-targeting-PaginationPaginationUl")
					except:
						break

					Pages = Pagination.find_all("li")  # ...and then calculate using this... god help me
					FinalPage = Pages[-2].text
					for Page in range(2, int(FinalPage) + 1):  # Go through rest of the pages for the category
						Driver.get(f"{CategoryLink}?page={Page}")
						PageSoup = BeautifulSoup(Driver.page_source, "html.parser")
						Products = PageSoup.find_all("header", class_="product__header")
						for CurrProduct in Products:
							ScraperDefs.ColesDataExtractor(CurrProduct, Writer, CategoryID)
						print("Page complete, moving on...")

					if Page == int(FinalPage):
						break

	print("Time to import")

# ----------------------------------------------------------------------------------------------------------------------

elif Choice == 4:
	Options = Options()
	Options.add_experimental_option("excludeSwitches", ["enable-automation"])
	Options.add_experimental_option('useAutomationExtension', False)
	Driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=Options)
	stealth(Driver, languages=["en-GB", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.",
	        renderer="Intel Iris OpenGL Engine", fix_hairline=True)  # See above

	Driver.get(ColesURL + "/browse")
	SiteSoup = BeautifulSoup(Driver.page_source, "html.parser")
	selectCategories = ScraperDefs.ChooseCategories(SiteSoup)

	for Category in selectCategories:
		CategoryLink = ColesURL + (Category.get("href"))

		if CategoryLink is not None:
			Driver.get(CategoryLink)
			while True:
				PageSoup = BeautifulSoup(Driver.page_source, "html.parser")
				Products = PageSoup.find_all("header", class_="product__header")

				for CurrentProduct in Products:
					ScraperDefs.ColesImageExtractor(CurrentProduct, ColesImgPath)

				try:
					Pagination = PageSoup.find("ul", class_="coles-targeting-PaginationPaginationUl")
				except:
					break

				Pages = Pagination.find_all("li")
				FinalPage = Pages[-2].text
				for Page in range(2, int(FinalPage) + 1):
					Driver.get(f"{CategoryLink}?page={Page}")
					PageSoup = BeautifulSoup(Driver.page_source, "html.parser")
					Products = PageSoup.find_all("header", class_="product__header")
					for CurrProduct in Products:
						ScraperDefs.ColesImageExtractor(CurrProduct, ColesImgPath)
					print("Page complete, moving on...")

				if Page == int(FinalPage):
					break

	print("Time to import")

# ----------------------------------------------------------------------------------------------------------------------

elif Choice == 5:
	UrlPieces = []
	ScraperDefs.WooliesCategoryFetch(WoolworthsURL, UrlPieces)
	UrlPieces = " ".join(UrlPieces).replace("/shop/browse/", "").split()

	for Fragment in UrlPieces:
		CategoryUrl = f"{WoolworthsURL}/shop/browse/{Fragment}"
		PageCount = ScraperDefs.PageCounter(CategoryUrl)

		CategoryID = None
		if ("bakery" in Fragment) or ("pantry" == Fragment):
			CategoryID = 1
		elif "household" == Fragment:
			CategoryID = 2
		elif "fruit-veg" == Fragment:
			CategoryID = 3
		elif "dairy-eggs-fridge" == Fragment:
			CategoryID = 4
		elif "drinks" == Fragment:
			CategoryID = 5
		elif "freezer" == Fragment:
			CategoryID = 6
		elif "liquor" == Fragment:
			CategoryID = 7
		elif "meat-seafood-deli" == Fragment:
			CategoryID = 8

		Filename = Fragment + ".csv"  # Naming conventions will be different but the store for some reason alters the setup constantly, thus ruining things
		Filepath = WoolworthsDataPath + Filename
		if os.path.exists(Filepath):
			os.remove(Filepath)
		with open(Filepath, "a", newline="") as Sheet:
			Writer = csv.writer(Sheet)
			for i in range(int(PageCount)):
				FocusedUrl = f"{CategoryUrl}?pageNumber={i + 1}"
				try:
					ScraperDefs.GetWooliesProducts(FocusedUrl, Writer, CategoryID)
					print("Page complete, moving on...")
				except PTimeout:
					continue

	print("Time to import")

# ----------------------------------------------------------------------------------------------------------------------

elif Choice == 6:
	UrlPieces = []
	ScraperDefs.WooliesCategoryFetch(WoolworthsURL, UrlPieces)
	UrlPieces = " ".join(UrlPieces).replace("/shop/browse/", "").split()

	for Fragment in UrlPieces:
		CategoryUrl = f"{WoolworthsURL}/shop/browse/{Fragment}"
		PageCount = ScraperDefs.PageCounter(CategoryUrl)

		for i in range(int(PageCount)):
			FocusedUrl = f"{CategoryUrl}?pageNumber={i + 1}"
			try:
				ScraperDefs.GetWooliesImages(FocusedUrl, WoolworthsImgPath)
				print("Page complete, moving on...")
			except PTimeout:
				continue

	print("Time to import")
