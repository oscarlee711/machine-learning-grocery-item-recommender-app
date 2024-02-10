# -*- coding: utf-8 -*-
"""
Created on Sat Apr  1 11:47:12 2023

@author: User
"""

from ast import Try
import os

import numpy as np
import pandas as pd
import difflib
import cv2
import matplotlib.pyplot as plt

from skimage.filters import threshold_local
from PIL import Image

import re
import pytesseract
import numpy as np
import matplotlib.pyplot as plt

from pytesseract import Output
from prettytable import PrettyTable

import sys

from sqlalchemy import create_engine
from datetime import datetime


def plot_rgb(image):
    plt.figure(figsize=(16,10))
    return plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

def plot_gray(image):
    plt.figure(figsize=(16,10))
    return plt.imshow(image, cmap='Greys_r')

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

#Convert the image to greyscale
def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#Remove Noise from an image
def noise_removal(image):
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    image = cv2.medianBlur(image, 3)
    return (image)

#find amounts on a receipt
def find_amounts(text):
    amounts = re.findall(r'\d+\.\d{2}\b', text)
    floats = [float(amount) for amount in amounts]
    #find all values split with a ,
    faulty_amounts = re.findall(r'\d+\,\d{2}\b', text)
    fixed_amounts=[]
    float_amounts=[]
    for amount in faulty_amounts:
        #Substitiut , for .
       amount=re.sub(",",".", amount)
       fixed_amounts.append(amount)
   #convert amount to a float
    for amount in fixed_amounts:
        amount=float(amount)
        float_amounts.append(amount)
    #add new list of floats to the start of the existing list
    for amount in float_amounts:
        floats.insert(0,amount)  
    return floats

#Find values between "first" and "last"
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        #print(s[start:end])
        return s[start:end]
    except ValueError:
        return "No match found"

#Find values between "first" and "last", starting from the end of the text
def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""
    
def find_number_of_items_woolies (text):
    #search for the number before SUBTOTAL 
    subtotal_line = r"(\d+)\s+SUBTOTAL"
    match = re.search(subtotal_line, text)
    if match:
        number_of_items = match.group(1)
        #print(number_of_items)
        return number_of_items
    else:
        print('No match found')
        return 0
        
def find_number_of_items_coles (text):
    #search for the number before SUBTOTAL
    subtotal_line = r"Total for+\s(\d+)"
    match = re.search(subtotal_line, text)
    if match:
        number_of_items = match.group(1)
        return number_of_items
    else:
        print('No match found')
        return 0

def sum_of_item_cost(number_of_items, item_costs):
    total =0
    while number_of_items >0:
        total=total + item_costs[number_of_items-1]
        number_of_items=number_of_items-1
    return(total)

#Compare sum of item values, with the total
def verify_total(total,amounts):
    verifyed_total = False
    for value in amounts:
        if total == value:
            verifyed_total = True
            return verifyed_total
        else: 
            verifyed_total = False
    return verifyed_total

def bw_scanner(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    T = threshold_local(gray, 21, offset = 5, method = "gaussian")
    return (gray > T).astype("uint8") * 255

def find_Receipt( s, last ):
    try:
        global first
        global end
        first= re.search(r':\d{2}', s)
        first = first.group()
        start = s.index( first ) + len( first )
        end = s.index( last, int(start) )
        return s[start:end]
    except ValueError:
        return "No match found"
    
def get_Woolies_items(text):
    index =0
    for item in text:
        global start_index
        global end_index
        start_match=re.search("ABN",item)
        end_match=re.search("SUBTOTAL",item)
        if start_match != None:
            #print(match.group()+ str(index))
            start_index = index
        elif end_match != None:
            end_index = index
        index = index + 1
            
    desc = []
    length_of_text = len(text)
    index =0
    for item in text:
        if index > start_index and index < end_index:
            desc.append(item)
            index=index+1
        else:
            index=index+1
    return desc


# Sample file out of the dataset
PyTesLoc = sys.argv[1]
FileNameLoc = sys.argv[2]
#FileNameLoc="Receipts/20230415_132714.jpg"
UserID = sys.argv[3]


#pytesseract.pytesseract.tesseract_cmd = 'D:\Program Files (x86)\Tesseract'
# Sample file out of the dataset
#file_name = '../uploads/ImageToBeProcessed.jpg'
#pytesseract.pytesseract.tesseract_cmd = PyTesLoc
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
file_name = FileNameLoc

img = Image.open(file_name)
#img.thumbnail((800,800), Image.ANTIALIAS)
#img

image = cv2.imread(file_name)

color = [255, 255, 255]
top, bottom, left, right = [300]*4

#Add a border around the image
image_with_border = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
cv2.imwrite("image_with_border.jpg", image_with_border)

# Convert to grayscale for further processing
gray = cv2.cvtColor(image_with_border, cv2.COLOR_BGR2GRAY)
plot_gray(gray)

#invert colour of image
inverted_image = cv2.bitwise_not(gray)
cv2.imwrite("inverted.jpg", inverted_image)

#Apply threshold ot convert to only black and white
thresh, im_bw = cv2.threshold(inverted_image, 150, 255, cv2.THRESH_BINARY)
cv2.imwrite("bw_image.jpg", im_bw)

#Draw boxes around groups of text
img=cv2.imread('bw_image.jpg')
d = pytesseract.image_to_data(img, output_type=Output.DICT)
n_boxes = len(d['level'])
boxes = im_bw
for i in range(n_boxes):
    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
    if  h> 20 and w>5:    
        boxes = cv2.rectangle(boxes, (x, y), (x + w, y + h), (50, 50, 50), 2)
cv2.imwrite("b_Box.jpg", boxes)
plot_rgb(boxes)

#Convert Receipt into a string
extracted_text = pytesseract.image_to_string(im_bw)
#save extracted_text as a .txt doc for troubleshooting purposes
with open("output.txt", "w") as file:
    file.write(extracted_text)


#Find which Supermarket the receipt is from
listword1 = ['woolworth', 'WOOLWORTH', 'Woolworth','Woolworths',"The fresh food people", 'The fresh Food pple']
listword2 = ['coles', 'COLES', 'Coles']
#Search the string for supermarket keywords
try:
    if any(re.search(r'\b{}\b'.format(re.escape(word)), extracted_text) for word in listword1):
        Supermarket = 'Woolworths'
    elif any(re.search(r'\b{}\b'.format(re.escape(word)), extracted_text) for word in listword2):
        Supermarket = 'Coles'
    else:
        Supermarket = ''
except:
    sys.exit(1)
      
#print(Supermarket)
    
#print(extracted_text)

#Look for the date on the receipt
try:
    match = re.search(r'\d{2}/\d{2}/\d{4}', extracted_text)
    date = datetime.strptime(match.group(), '%d/%m/%Y').date()
except AttributeError:
    try:
        match = re.search(r'\d{2}/\d{2}/\d{2}', extracted_text)
        date = datetime.strptime(match.group(), '%d/%m/%y').date()
    except:
        date= datetime.today()

#Find costs on the receipt
amounts =[]
amounts = find_amounts(extracted_text)


#Find number of items on the reciept
items = 0
if Supermarket == 'Coles':
    items=find_number_of_items_coles(extracted_text)
elif Supermarket == 'Woolworths':
    items=find_number_of_items_woolies(extracted_text)
items=int(items)
#Find Total cost of items
try:
    Total_cost=sum_of_item_cost(items,amounts)
except:
    print("Items: "+str(items) + " Amounts: " + str(amounts))

#Verify total cost of items
verifyed_total = False
try:
    verifyed_total = verify_total(Total_cost,amounts)
except:
    pass
if verifyed_total:
    print(Total_cost)
else:
    print("Unable to verify total")
#    sys.exit(4)

#Find data from string
if Supermarket == "Coles":
    # Error in OCR is resulting in - showing as . Full stop in below code may need to be changed to "-" once OCR is improved
    #(For Coles)
    try:
        StoreN = find_between( extracted_text, "Store: ", "." )
        StoreN= StoreN.strip()
    except:
        StoreN = "N/A"
    #print(StoreN)
    
    #Receipt ID (For Coles)
    try:
        Receipt_ID = find_between( extracted_text, "Receipt: ", "Date:" )
    except:
        Receipt_ID = "Receipt_ID not available"
    #print(Receipt_ID)
    
    #Product descriptions and prices (For Coles)
    try:
        desc = find_between( extracted_text, "iption ", "Total" )
    except:
        sys.exit(1)
    
    #Lines to excluse on the receipt
    exclusion_list = ["bank", "total", "promo", "vat", "change", "recyclable"]
    
    #Words to ommit
    remove_list = ["vit", "etc"]
    
    #Extract letters and numbers regex
    regex_line = []
    for line in desc.splitlines():
        if re.search(r".[0-9]|[0-9]*\.[0-9]|[0-9]*\,[0-9]", line):
            regex_line.append(line)
    #print(regex_line)
    
    #Apply exclusion list
    food_item = []
    for eachLine in regex_line:
        found = False
        for exclude in exclusion_list:
            if exclude in eachLine.lower():
                found = True
            
        if found == False:
            food_item.append(eachLine)
    #print(food_item)
    
    #Word ommit
    new_food_item_list = []
    for item in food_item:
        for subToRemove in remove_list:
            item = item.replace(subToRemove, "")
            item = item.replace(subToRemove.upper(), "")
        new_food_item_list.append(item)
    #print(new_food_item_list)
    
    #Food item cost regex
    food_item_cost = []
    for line in new_food_item_list:
        line = line.replace(",", ".")
        cost = re.findall('\d*\.?\d+|\d*\,?\d+|',line)
        
        for possibleCost in cost:
            if "." in possibleCost:
                food_item_cost.append(possibleCost)
    #print(new_food_item_list)
    
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
    #print(only_food_items)
    
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
    #print(food)
    
    unwanted = {"EACH","GRAM","GRAN","NET","eer"}
    
    food = [ele for ele in food if ele not in unwanted]
    food = [x for x in food if "BETTER BAG" not in x]
    
elif Supermarket == "Woolworths":
    try:
        StoreN = find_between( extracted_text, "people", "PH" )
        StoreN=StoreN= StoreN.strip()
        with open("store.txt", "w") as file:
            file.write(StoreN)
    except:
        StoreN=' '
    try:
        Receipt_ID = find_Receipt( extracted_text, "APPROVED")
    except: Receipt_ID = "Receipt_ID not available"
    text= extracted_text.split("\n")
    #Product descriptions and prices (For Woolworths)
    try:
        desc = get_Woolies_items(text)
    except:
        sys.exit(2)
    
    #Lines to excluse on the receipt
    exclusion_list = ["bank", "total", "promo", "vat", "change", "recyclable"]
    
    #Words to ommit
    remove_list = ["vit", "etc"]
    
    #Extract letters and numbers regex
    regex_line = []
    for line in desc:
        if re.search(r".[0-9]|[0-9]*\.[0-9]|[0-9]*\,[0-9]", line):
            regex_line.append(line)
    #print(regex_line)
    
    #Apply exclusion list
    food_item = []
    for eachLine in regex_line:
        found = False
        for exclude in exclusion_list:
            if exclude in eachLine.lower():
                found = True
            
        if found == False:
            food_item.append(eachLine)
    #print(food_item)
    
    #Word ommit
    new_food_item_list = []
    for item in food_item:
        for subToRemove in remove_list:
            item = item.replace(subToRemove, "")
            item = item.replace(subToRemove.upper(), "")
        new_food_item_list.append(item)
    #print(new_food_item_list)
    
    #Food item cost regex
    food_item_cost = []
    for line in new_food_item_list:
        line = line.replace(",", ".")
        cost = re.findall('\d*\.?\d+|\d*\,?\d+|',line)
        
        for possibleCost in cost:
            if "." in possibleCost:
                food_item_cost.append(possibleCost)
    #print(new_food_item_list)
    
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
    #print(only_food_items)
    
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
    #print(food)
    
    unwanted = {"EACH","GRAM","GRAN","NET","eer"}
    
    food = [ele for ele in food if ele not in unwanted]
    food = [x for x in food if "BETTER BAG" not in x]
#print(food)

#Tabulate Food Item and Cost
t = PrettyTable(['Food Item', 'Cost'])
if (len(food)==len(food_item_cost)):
    for counter in range (0,len(food)):
        t.add_row([food[counter], food_item_cost[counter]])
else:
    print("number of food items "+str(len(food)))
    print("number of costs "+str(len(food_item_cost)))


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

#df2.to_csv('output.csv', index=False)

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
  df2['StoreID'] = StoreID
  #data = [{'id':StoreID,'name':Supermarket,'address':StoreN,'postcode':'2000'}]
  #store = store.concat(data,ignore_index=True,sort=False)

df2.to_csv('output.csv', index=False)

try:
    df2.to_sql('ocrtable',con=con, if_exists='append',index=False)
except:
    print("Unable to upload to database")