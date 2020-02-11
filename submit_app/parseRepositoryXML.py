# 
# Download mysql-connector package : pip install mysql-connector-python
#
import xml.etree.ElementTree as ET

import mysql.connector
from mysql.connector import Error


#
#author : Charan Reddy
#

#Reading data from XML file	
def readXML():
	with open('repository.xml', 'r') as myfile:
		data=myfile.read()
	data = data.replace("&", "&amp;")
	root = ET.fromstring(data)
	return root

#Parse XML file and insert it in given database	
def writeToDatabase(host,user,passwd,database):
	try:
		mydb = mysql.connector.connect(host=host,
				user=user,
				passwd=passwd,
				database=database)
		if mydb.is_connected():
			root = readXML()
			for resource in root.findall('resource'):
				name = resource.attrib["symbolicname"]
				name = name.replace("-", "_")
				name = name.replace(".", "_")
				fullname = resource.attrib["presentationname"]
				details = resource.find('description').text
				#details = base64.b64decode(details)
				active = 1
				has_releases = 1
				mycursor = mydb.cursor()
				sql = """REPLACE INTO apps_app (fullname, details, has_releases, active) VALUES (%s, %s, %s, %s)"""
				val = (fullname, details, int(has_releases), int(active))
				mycursor.execute(sql, val)
				mydb.commit()
			print("Data is inserted/updated in database")	
	except Error as e :
		print ("Error while connecting to MySQL", e)
	finally:
		#closing database connection.
		if(mydb.is_connected()):
			mycursor.close()
			mydb.close()
			print("MySQL connection is closed")
			
def main():
	host = input("Enter the host address : ")
	userName = input("Enter the user name : ")
	password = input("Enter the password : ")
	database = input("Enter the database name : ")
	writeToDatabase(host,userName,password,database)

main()