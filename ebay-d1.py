import argparse
import requests
from bs4 import BeautifulSoup 
import json
import csv



#status looks like name
#shipping easier
def parse_itemssold(text):
 
    numbers = ''
    for char in text:
        if char in '1234567890':
            numbers += char
    if 'sold' in text:
        return int(numbers)
    else:
        return 0

def parse_price(text):
 
    '''
    >>> parse_price('$3.00 to $5.39')
    300
    >>> parse_price('$123.40')
    12340
    >>> parse_price('$23.46')
    2346
    '''
    price2 = ''
    newprice = ''
 
    if 'to' in text:
        splittext = text.split('to', 1)
        newprice = splittext[0]
   
        for char in newprice:
            if char == '.':
                price2 += ''
            elif char == ',':
                price2 += ''
            else:
                price2 += char
    else:
        for char in text:
            if char == '.':
                price2 += ''
            elif char == ',':
                price2 += ''
            elif char == '$':
                price2 == ''
            else:
                price2 += char
   
    return int(price2[1:])
 
def parse_shipping(text):
    '''
    >>> parse_shipping('+$15.95 shipping estimate')
    1595
    >>> parse_shipping('Free shipping')
    0
    >>> parse_shipping('+$9.35 shipping')
    935
    '''
 
    if 'Free' in text:
        return 0
 
    if 'not specified' in text:
        return None
 
    else:
        ship = ''
        for char in text:
            if char == '.':
                ship += ''
            elif char == '+':
                ship += ''
            elif char == '$':
                ship += ''
            else:
                ship += char
        ship = ship.replace('shipping','')
        ship = ship.replace('estimate','')
 
    return int(ship[1:])
 

# get command line arguments
parser = argparse.ArgumentParser(description='Download information from ebay and convert to JSON.')
parser.add_argument('search_term')
parser.add_argument('--num_pages', default=10)
parser.add_argument('--csv', action = 'store_true')
args = parser.parse_args()
print('args.search_term=', args.search_term)
 
#lists of all items found in all ebay webpages
items = []
 

#loop over the ebay webpages
for page_number in range(1, args.num_pages+1):
 
    # build the url
    url = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw='
    url += 'Nike+sneakers&_sacat=0&_pgn='
    url += str(page_number)
    url += '&rt=nc'
    #print('url=', url)
   
    # download the html
    r = requests.get(url)
    status = r.status_code
    #print('status=', status)
 
    html = r.text
    #print('html=', html[:50])
 
    # process the html
   
    soup = BeautifulSoup(html, 'html.parser')
 
    tags_items = soup.select('.s-item')
    for tag_item in tags_items:
 
        #extract the name
        tags_name = tag_item.select('.s-item__title')
        name = None
        for tag in tags_name:
            name = tag.text
 
        #extract the free returns
        freereturns = False
        tags_freereturns = tag_item.select('.s-item__free-returns')
        for tag in tags_freereturns:
            freereturns = True
 
        #extract items sold
        items_sold = None
        tags_itemssold = tag_item.select('.s-item__hotness')
        for tag in tags_itemssold:
            items_sold = parse_itemssold(tag.text)
 
        status = None
        # extract status
        tags_status = tag_item.select('.SECONDARY_INFO')
        for tag in tags_status:
            status = tag.text
 
        # extract shipping
        shipping = None
        tags_shipping = tag_item.select('.s-item__shipping')
        for tag in tags_shipping:
            shipping = parse_shipping(tag.text)
 
         #extract price
        price = None
        tags_price = tag_item.select('.s-item__price')
        for tag in tags_price:
            price = parse_price(tag.text)
 
        item = {
            'name': name,
            'free_returns': freereturns,
            'items_sold': items_sold,
            'status': status,
            'price': price,
            'shipping': shipping,
        }
        items.append(item)


if args.csv:
    titles = ['name', 'price', 'status', 'shipping', 'free_returns', 'items_sold']
    filename = args.search_term+'.csv'
    with open(filename, 'w', encoding='utf-8') as c:
        csv_writer = csv.DictWriter(c, titles)
        csv_writer.writeheader()
        csv_writer.writerows(items)

else:
    filename = args.search_term+'.json'
    with open(filename, 'w', encoding='ascii') as f:
        f.write(json.dumps(items))

'''
if args.csv == True:
    filename = args.search_term +'.csv'
    with open(filename,'w', newline ='') as f:
        fieldnames = ['price', 'status', 'items_sold', 'shipping', 'name', 'free_returns']
        csvwriter = csv.DictWriter(f, fieldnames = fieldnames)
        csvwriter.writeheader()
        for element in items:
            csvwriter.writerow(element)
'''


