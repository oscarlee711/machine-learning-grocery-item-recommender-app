# -*- coding: utf-8 -*-
"""T1_2022_OCR_Final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tK3Pos8IevW8GBhbbjVJqFXghFXxGPKa
"""

import numpy as np
import pandas as pd
import difflib
import cv2
import matplotlib.pyplot as plt

from skimage.filters import threshold_local
from PIL import Image

import re
import cv2
import pytesseract
import numpy as np
import matplotlib.pyplot as plt

from skimage.filters import threshold_local
from PIL import Image
from pytesseract import Output
from prettytable import PrettyTable

import sys
import os
import dustutils

# Sample file out of the dataset
#PyTesLoc = sys.argv[1]
FileNameLoc = sys.argv[2]
UserID = sys.argv[3]

#pytesseract.pytesseract.tesseract_cmd = 'Tesseract-OCR/tesseract.exe'
# Sample file out of the dataset
#file_name = '../uploads/wxwg74gj02831.jpg'
PyTesLoc = distutils.spawn.find_executable("tesseract")
if (PyTesLoc):
    pytesseract.pytesseract.tesseract_cmd = PyTesLoc
else:
    #Change to your custom install directory
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

#Remove output csv to ensure that new results are being utilized/outputted for debugging purposes
#Ensure csv file is not open while running
if os.path.isfile('output.csv'):
  os.remove('output.csv')
else:
  print("The output csv does not exist")

file_name = FileNameLoc

img = Image.open(file_name)
img.thumbnail((800,800))
#img.thumbnail((800,800), Image.ANTIALIAS)
#img

def opencv_resize(image, ratio):
    width = int(image.shape[1] * ratio)
    height = int(image.shape[0] * ratio)
    dim = (width, height)
    return cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

def plot_rgb(image):
    plt.figure(figsize=(16,10))
    return plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

def plot_gray(image):
    plt.figure(figsize=(16,10))
    return plt.imshow(image, cmap='Greys_r')

image = cv2.imread(file_name)
# Downscale image as finding receipt contour is more efficient on a small image
resize_ratio = 500 / image.shape[0]
original = image.copy()
image = opencv_resize(image, resize_ratio)

# Convert to grayscale for further processing
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
plot_gray(gray)

# Get rid of noise with Gaussian Blur filter
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
plot_gray(blurred)

# Detect white regions
rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
dilated = cv2.dilate(blurred, rectKernel)
plot_gray(dilated)

edged = cv2.Canny(dilated, 100, 200, apertureSize=3)
plot_gray(edged)

# Detect all contours in Canny-edged image
contours, hierarchy = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
image_with_contours = cv2.drawContours(image.copy(), contours, -1, (0,255,0), 3)
plot_rgb(image_with_contours)

# Get 10 largest contours
largest_contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]
image_with_largest_contours = cv2.drawContours(image.copy(), largest_contours, -1, (0,255,0), 3)
plot_rgb(image_with_largest_contours)

# approximate the contour by a more primitive polygon shape
def approximate_contour(contour):
    peri = cv2.arcLength(contour, True)
    return cv2.approxPolyDP(contour, 0.032 * peri, True)

def get_receipt_contour(contours):    
    # loop over the contours
    for c in contours:
        approx = approximate_contour(c)
        # if our approximated contour has four points, we can assume it is receipt's rectangle
        if len(approx) == 4:
            return approx

get_receipt_contour(largest_contours)

receipt_contour = get_receipt_contour(largest_contours)
image_with_receipt_contour = cv2.drawContours(image.copy(), [receipt_contour], -1, (0, 255, 0), 2)
plot_rgb(image_with_receipt_contour)

def contour_to_rect(contour):
    pts = contour.reshape(4, 2)
    rect = np.zeros((4, 2), dtype = "float32")
    # top-left point has the smallest sum
    # bottom-right has the largest sum
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    # compute the difference between the points:
    # the top-right will have the minumum difference 
    # the bottom-left will have the maximum difference
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect / resize_ratio

def wrap_perspective(img, rect):
    # unpack rectangle points: top left, top right, bottom right, bottom left
    (tl, tr, br, bl) = rect
    # compute the width of the new image
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    # compute the height of the new image
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    # take the maximum of the width and height values to reach
    # our final dimensions
    maxWidth = max(int(widthA), int(widthB))
    maxHeight = max(int(heightA), int(heightB))
    # destination points which will be used to map the screen to a "scanned" view
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")
    # calculate the perspective transform matrix
    M = cv2.getPerspectiveTransform(rect, dst)
    # warp the perspective to grab the screen
    return cv2.warpPerspective(img, M, (maxWidth, maxHeight))

scanned = wrap_perspective(original.copy(), contour_to_rect(receipt_contour))
plt.figure(figsize=(16,10))
plt.imshow(scanned)

def bw_scanner(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    T = threshold_local(gray, 21, offset = 5, method = "gaussian")
    return (gray > T).astype("uint8") * 255

result = bw_scanner(scanned)
image = bw_scanner(scanned)
plot_gray(result)

output = Image.fromarray(result)
#output.save('result.png')

d = pytesseract.image_to_data(image, output_type=Output.DICT)
n_boxes = len(d['level'])
boxes = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2RGB)
for i in range(n_boxes):
    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])    
    boxes = cv2.rectangle(boxes, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
plot_rgb(boxes)

extracted_text = pytesseract.image_to_string(image)
print(extracted_text)

listword1 = ['woolworth', 'WOOLWORTH', 'Woolworth']
listword2 = ['coles', 'COLES', 'Coles']
if any(re.search(r'\b{}\b'.format(re.escape(word)), extracted_text) for word in listword1):
    Supermarket = 'Woolworths'
elif any(re.search(r'\b{}\b'.format(re.escape(word)), extracted_text) for word in listword2):
    Supermarket = 'Coles'
else:
    Supermarket = ''
      

print(Supermarket)

from datetime import datetime

match = re.search(r'\d{2}/\d{2}/\d{4}', extracted_text)
date = datetime.strptime(match.group(), '%d/%m/%Y').date()
print(date)

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

#Store
StoreN = find_between( extracted_text, "Store: ", ";" )
print(StoreN)

#Receipt ID
Receipt_ID = find_between( extracted_text, "Receipt: ", "Date:" )
print(Receipt_ID)

#Product descriptions and prices
desc = find_between( extracted_text, "scription ", "EFT" )

#desc = find_between( desc, ";","Total" )
print(desc)

#extracting grand total
def find_amounts(text):
    amounts = re.findall(r'\d+\.\d{2}\b', text)
    floats = [float(amount) for amount in amounts]
    unique = list(dict.fromkeys(floats))
    return unique

amounts = find_amounts(extracted_text)
amounts

max(amounts)

#Lines to excluse on the receipt
exclusion_list = ["bank", "total", "promo", "vat", "change", "recyclable"]

#Words to ommit
remove_list = ["vit", "etc"]

#Extract letters and numbers regex
regex_line = []
for line in desc.splitlines():
    if re.search(r".[0-9]|[0-9]*\.[0-9]|[0-9]*\,[0-9]", line):
        regex_line.append(line)
print(regex_line)

#Apply exclusion list
food_item = []
for eachLine in regex_line:
    found = False
    for exclude in exclusion_list:
        if exclude in eachLine.lower():
            found = True
        
    if found == False:
        food_item.append(eachLine)
print(food_item)

#Word ommit
new_food_item_list = []
for item in food_item:
    for subToRemove in remove_list:
        item = item.replace(subToRemove, "")
        item = item.replace(subToRemove.upper(), "")
    new_food_item_list.append(item)
print(new_food_item_list)

#Food item cost regex
food_item_cost = []
for line in new_food_item_list:
    line = line.replace(",", ".")
    cost = re.findall('\d*\.?\d+|\d*\,?\d+|',line)
    
    for possibleCost in cost:
        if "." in possibleCost:
            food_item_cost.append(possibleCost)
print(new_food_item_list)

#Remove cost price from food item
count = 0;
only_food_items = []
for item in new_food_item_list:
    only_alpha = ""
    for char in item:
        if char.isalpha() or char.isspace():
            only_alpha += char
            
    only_alpha = re.sub(r'(?:^| )\w(?:$| )', ' ', only_alpha).strip()
    only_food_items.append(only_alpha)
print(only_food_items)

#Removes 2 letter words from food item
#No core food item has two letters (Most cases)
food = []
for item in only_food_items:
    # getting splits
    temp = item.split()

    # omitting K lengths
    res = [ele for ele in temp if len(ele) != 2]

    # joining result
    res = ' '.join(res)
    
    food.append(res)
print(food)

unwanted = {"EACH","GRAM","NET","eer"}
 
food = [ele for ele in food if ele not in unwanted]
food = [x for x in food if "BETTER BAG" not in x]

print(food)

#Tabulate Food Item and Cost
t = PrettyTable(['Food Item', 'Cost'])
for counter in range (0,len(food)):
    t.add_row([food[counter], food_item_cost[counter]])
print(t)

import pandas as pd
df = pd.DataFrame(food, columns=['food'])
df1 = pd.DataFrame(food_item_cost, columns=['Cost'])

df2 = pd.concat([df, df1], axis=1)
df2['Receipt_ID'] = Receipt_ID
df2['Supermarket'] = Supermarket
df2['date'] = date
df2['Store'] = StoreN
df2['Processed'] = 0
df2.dropna(inplace=True)
df2['UserID'] = UserID
df2['StoreID'] = ''
df2.head(15)

import mysql.connector
import pymysql
from sqlalchemy import create_engine

#engine = create_engine('mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}', echo=False)
#con = create_engine('mysql+pymysql://discountmateuser:DMPassword$@discountmate.ddns.net/discountmate')
con = create_engine('mysql+pymysql://discountmateuser:DMPassword$@localhost/discountmate')

store = pd.read_sql('SELECT * FROM shops', con=con)
store.head(10)

StoreID = ''
if store['address'].str.contains(StoreN).any():
    StoreID = store.loc[store['address'] == StoreN, 'id'].iloc[0]  
    
print(StoreID)

max_value = ''
if StoreID == '':
  column = store["id"]
  max_value = column.max()
  StoreID = max_value + 1
  data = [{'id':StoreID,'name':Supermarket,'address':StoreN,'postcode':'2000'}]
  store = store.append(data,ignore_index=True,sort=False)

df2['StoreID'] = StoreID

#store.to_sql("shops",con=con,index=False,if_exists="replace")

df2.head(16)

df2.to_sql("OCRTable",con=con,index=False,if_exists="append")

