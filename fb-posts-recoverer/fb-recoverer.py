#README: put this file in /Ultimate-Facebook-Scraper/data/user/ and run it with python3
#	 this program works throught the terminal -withing login- so you will can mine only 1000 posts before facebook blocks your IP
#	 make the changes that you freely consider
#	 some things work only in spanish and I do not know how to make it universal

import urllib.request
import time
import xlsxwriter                 #pip3 install xlsxwriter
from bs4 import BeautifulSoup     #pip3 install beautifulsoup4

from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError

unixDay = str(int(time.time()))
fileXlsx = "posts" +"_" + unixDay + ".xlsx"

wb = xlsxwriter.Workbook(fileXlsx)
ws = wb.add_worksheet()

ws.write(0, 0, "innerId")
ws.write(0, 1, "timest")
ws.write(0, 2, "date")
ws.write(0, 3, "postUrl")
ws.write(0, 4, "socialNet")
ws.write(0, 5, "user")
ws.write(0, 6, "post")
ws.write(0, 7, "shared")
ws.write(0, 8, "day")
ws.write(0, 9, "month")
ws.write(0, 10, "year")
ws.write(0, 11, "tags")
ws.write(0, 14, "hour")
ws.write(0, 15, "minutes")
ws.write(0, 16, "date")

#######################################################################################################################

print("\n\n\n\n  RETRIEVING POSTS FROM FB  \n\n")


fileObj = open('Posts.txt', encoding='UTF8')
sentences = fileObj.read().split('\n')


#######################################################################################################################

def createPost(date, postId, q, sentence):
	postLink = "https://www.facebook.com/" +postId
	innerId = str(q)
	print("\n-----------------------------------------------------------------------------------------------------------------\n\n")
	print(innerId + " - " +date + " - " +postLink)
	q += 1
	excA = "A" + str(q)
	excC = "C" + str(q)
	excD = "D" + str(q)
	excE = "E" + str(q)
	ws.write(excA, innerId)
	ws.write(excC, date)
	ws.write(excD, postLink)
	ws.write(excE, "fb")
	if date.find(','):
		posComma = date.find(',')
		day = date[posComma+2:posComma+4]
		
		posMonth = date.find('de')
		aux = date[posMonth+3:]
		posMonth2 = aux.find(' ')
		month = aux[:posMonth2]
		if month=="enero":
			month = "01"
		elif month=="febrero":
			month = "02"
		elif month=="marzo":
			month = "03"
		elif month=="abril":
			month = "04"
		elif month=="mayo":
			month = "05"
		elif month=="junio":
			month = "06"
		elif month=="julio":
			month = "07"
		elif month=="agosto":
			month = "08"
		elif month=="septiembre":
			month = "09"
		elif month=="octubre":
			month = "10"
		elif month=="noviembre":
			month = "11"
		elif month=="diciembre":
			month = "12"

		pos3 = aux.find('20')
		aux2 = aux[pos3:]
		pos4 = aux2.find(' ')
		year = aux2[:pos4]

		pos5 = aux2.find(':')
		hour = aux2[pos5-2:pos5]
		min = aux2[pos5+1:pos5+3]		

		print("DAY: " +day + " MONTH: " +month + " YEAR: " +year + " HOUR: " +hour + " MIN: " +min +"\n")
		excI = "I" + str(q)
		ws.write(excI, day)
		excJ = "J" + str(q)
		ws.write(excJ, month)
		excK = "K" + str(q)
		ws.write(excK, year)
		excO = "O" + str(q)
		ws.write(excO, hour)
		excP = "P" + str(q)
		ws.write(excP, min)
		excQ = "Q" + str(q)
		ws.write(excQ, day +"/" + month +"/" +year)
		excR = "R" + str(q)
		ws.write(excR, "01/01/1970")
		excS = "S" + str(q)
		ws.write(excS, "=" +excQ +"-" +excR)

		# retrieving post's timestamp
		excB = "B" + str(q)
		ws.write(excB, "=" +excS +"*24*60*60+(" +excO +"+3)*60*60+" +excP +"*60")

	sentence = sentence + ""
	retrievePost(postLink, q, sentence)


def retrievePost(postLink, q, sentence):
	try:
		postHtml = urllib.request.urlopen(postLink).read().decode()
	except HTTPError as e:
		print(e)
	except URLError:
		print("Problems with connection...")

	soup =  BeautifulSoup(postHtml, "html.parser")

	supertags = soup.findAll("div", {"class": "hidden_elem"})

	supertagsStr = str(supertags)
	#print(supertagsStr)
	if supertagsStr.find('<p>') == -1:
		print("POST: empty\n\n")
	else:
		for supertag in supertags:
			supertagStr = str(supertag)
			#print(supertagStr)
			if supertagStr.find('<p>') != -1:
				pos1 = supertagStr.find('<p>')
				pos2 = supertagStr.find('</p>')
				post = supertagStr[pos1+3:pos2]
				#print(post)
				while (post.find('<br />') != -1):
					pos = post.find('<br />')
					post = post[0:pos] +"\n" + post[pos+7:]
				while (post.find('<') != -1):
					pos1 = post.find('<')
					pos2 = post.find('>')
					post = post[0:pos1] + post[pos2+1:]

				#the following is about codification and can be remove
				while (post.find('&quot;') != -1):
					pos = post.find('&quot;')
					post = post[0:pos] +"'" + post[pos+6:]
				while (post.find('&#039;') != -1):
					pos = post.find('&#039;')
					post = post[0:pos] +"'" + post[pos+6:]
				while (post.find('&#064;') != -1):
					pos = post.find('&#064;')
					post = post[0:pos] +"@" + post[pos+6:]

				print("POST: " + post +"\n")
				excG = "G" + str(q)
				ws.write(excG, post)
				if sentence.find('http') != -1:
					pos = sentence.find('http')
					sentence = sentence[pos:]
					pos2 = sentence.find(' ')
					sharedN = sentence[:pos2]
					print("SHARED LINK: " +sharedN +"\n")
					excH = "H" + str(q)
					ws.write(excH, sharedN)



############################################################################################################################		

q = 0

for sentence in sentences:
	#print(sentence)
	if sentence.startswith(('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo')):
		pos = sentence.find('|') - 1
		date = sentence[:pos]
	if sentence.find('|') != -1:
		pos = sentence.find('||')
		postId = sentence[pos+2:]
		if postId.find('|') != -1:
			pos = postId.find('|')
			postId = postId[pos+2:]
			if postId.find('|') != -1:
				pos = postId.find('|')
				postId = postId[pos+2:]
				if postId.find('|') != -1:
					pos = postId.find('|')
					postId = postId[pos+2:]
					if postId.find('|') != -1:
						pos = postId.find('|')
						postId = postId[pos+3:].strip()
						try:
							postId = int(postId)
							postId = str(postId)
							q += 1
							createPost(date, postId, q, sentence)
						except:
							z = 1


##########################################################################################################

wb.close()


print("\n\n\n#####################            Exported to " +fileXlsx +"\n\n\n")



