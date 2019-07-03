from selenium import webdriver
import bs4, requests
import time
import xlsxwriter
#setting constants
topic = input("Enter the search topic:")
main_url = "https://play.google.com/store/search?q={}&c=apps&hl=en".format(topic)

#opening selenium
driver = webdriver.Firefox()
driver.get(main_url)
print("Retrieving urls...")

#getting all urls
SCROLL_PAUSE_TIME = 1
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	time.sleep(SCROLL_PAUSE_TIME)
	new_height = driver.execute_script("return document.body.scrollHeight")
	if new_height == last_height:
		break
	last_height = new_height

app_urls = [i.get_attribute('href') for i in driver.find_elements_by_class_name('JC71ub')]
print("Retrieved {} urls!!".format(len(app_urls)))

#Getting mail-ids from each site
objs=[]
print('Getting data from:')
for url in app_urls:
	try:
		print(url)
		page = requests.get(url)
		soup = bs4.BeautifulSoup(page.text,"lxml")
		elem = soup.find('a',{'class':'hrTbp euBY6b'})
		app = {}
		app['mail']=elem['href'][7:]
		app['name'] = soup.find('h1',{'class':'AHFaub'}).find('span').text
		rating= soup.find('div',{'class':'dNLKff'}).find('div',{'class':'pf5lIe'})
		if rating:
			rating_str=rating.find('div',{'role':'img'})['aria-label']
			app['rating'] = rating_str[ rating_str.find('.')-1:rating_str.find('.')+2]
		else:
			app['rating'] = '0.0'
		l = soup.find_all('div',{'class':'hAyfc'})
		for i in l:
			valname = i.find('div',{'class':'BgcNfc'})
			val = i.find('div',{'class':'IQ1z0d'}).find('span',{'class':'htlgb'}).text
			if valname is not None:
				app[valname.text] = val
		objs.append(app)
	except:
		f=open('excepted_url','a+')
		f.write(url+'\n')
		f.close()
		continue
dataset = []
for i in objs:
	if(float(i['rating'])!=0.0):
		if(float(i['rating'])>=3.0):
			dataset.append([i['name'],i['mail'],i['rating'],i['Installs']])


book = xlsxwriter.Workbook(topic+".xlsx")
worksheet = book.add_worksheet()
n=1
for data in dataset:
	c='A'
	for x in data:
		cell=c+str(n)
		worksheet.write(cell, x)
		c=chr(ord(c)+1)
	n+=1
book.close()
