#!/usr/bin/python

from requests import get
from requests.exceptions import RequestException
from contextlib import closing

import sys,getopt
import argparse

from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import pickle

import resource
import sys
import os 

import MySQLdb
import json

import pymongo
from pymongo import MongoClient

import sys,getopt
import argparse

from  time import sleep


def queryWikiPagesFromSQLToMongoDB(sqldb,mongodb,sqlTable, numberOfPagesToBeStored):
    """
    This method queries SQL database and
    stores the queried pages into MongoDB

    If the number of pages to be stored is greater than the number
    of pages present in the SQL database, all pages from 
    the SQL databse will be retrieved and stored in MongoDb
    """

    #Open connection with SQL Database
    db = MySQLdb.connect(host="localhost",db='wiki',user="root")
    Cursor = db.cursor()
    
    #Open connection with Mongo DB
    client = MongoClient()
    mongo_db = client[mongodb]


    #mongo_db.create_collection("content")
    #Access the content collection
    mongo_collection = mongo_db.content

    result = Cursor.execute("SELECT  Wiki_Title,Wiki_URL,Wiki_Body,Wiki_References FROM WikiTable LIMIT %d" % (numberOfPagesToBeStored,))
    if result!=0:
        res_tuples = Cursor.fetchall()
        #Insert into Mongo db
        for t in res_tuples:
            #print(t[0], t[1], t[2], t[3])
            mongo_collection.insert_one({
                "title" : t[0],
                "url" : t[1],
                "body" : t[2],
                "references" : t[3]
            }
            )
        print("Data has been stored into Mongodb also")
    else:
        print("Number of rows affected by statement:", result)

  

class DownloadWikiPages(object):
    def __init__(self):
        pass
    
    def simple_get(self,url):
        """
        The method attempts to get the content at `url` by making an HTTP 
        GET request.If the content-type of response is some kind of HTML/XML, 
        return the text content, otherwise return None
        """
        try:
            with closing(get(url, stream=True)) as resp:
                if self.is_good_response(resp):
                    return resp.content
                else:
                    return None

        except RequestException as e:
            self.log_error('Error during requests to {0} : {1}'.format(url, str(e)))
            return None
        
    def is_good_response(self,resp):
        """
        Returns true if the response seems to be HTML, false otherwise
        """
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200 
                and content_type is not None 
                and content_type.find('html') > -1)
        
    def log_error(self,e):
        """ 
        This function just prints them, but you can
        make it do anything.
        """
        print(e)
            
    def getHtml(self,page_url):
        """
        This method parses raw_html returned by simple_get
        and return the html object, the BeautifulSoup object.
        """
        raw_html = self.simple_get(page_url)

        if raw_html == None:
            self.log_error("Provided link is not correct")
            return None;
        else:
            return BeautifulSoup(raw_html, 'html.parser')
                
    def populate_listofPages(self,sqlObject,page_url,pageCount,listOfPages,pageUrls,pagesToBeDownloaded,html=None):
        """
        Paramters: page_url - the URL of the Wikipedia page to be parsed
                    pageCount - 0 is passed during first call to the function. 
                                Keeps on updating with each recursive call
                    listOfPages - Blank dictionary passed during the first call
                                to the function
                    pageUrls - list containing urls of the pages downloaded so far
                                This list is dumped to the system on program exit
                    html - parsed raw_html
        Return value: Return dictionary containing "pagesToBeDownloaded" number of Wikipedia pages.
                    Key = URL of the the wikipedia page
                    Value = List of Title,Body and ReferenceList                 
        """
        print("Passed page URL is ", page_url)
        if pageCount == pagesToBeDownloaded:
            print("Number of pages downloaded = ",pagesToBeDownloaded)
            return # Return when required number of pages have been downloaded

        new_page = '' #Initialize url of the new page to be taken next for parsing

        if html is None:
            html = self.getHtml(page_url)
            if html is None:
                return

        title = html.title.string  #get the Page title
        url = html.find(rel = "canonical").get('href')  #get the Page URL

        body = html.body.text  #Page body

        #Simple cleaning of the page text
        body = body.replace('\n','')
        body = body.replace('\t','')
        
        #Take a part of the text to have a smaller size of the database. 
        #Check can be removed if whole text is required. Datatype of the 
        #column in database needs to be updated accordingly.
        #if len(body) > 1000000: 
         #   body = body[0:999997]

        #Page References
        refer = []
        self.get_references(html,refer)
           
        listOfPages[url] = [title,body,refer]


        if pageCount%20 == 0:
            wiki_list = self.dictionaryToList(listOfPages)

            #Store the data into SQL database
            sqlObject.addPagesToDataBase(wiki_list)
            sleep(3)
            
        #skip_few_links = 0
        for link in html.find_all('a'): # pass through all the anchors one by one till you download required pages
            if link.get('href') is not None:
                if link.get('href').startswith("http") is False: #Its a valid web page
                    if "wiki/" in link.get('href'):  #Its a wiki page as we want to download wikipedia pages only
                        new_page = 'https://en.wikipedia.org' + link.get('href')
                        #skip_few_links = skip_few_links +1 
                        #if skip_few_links < 7:
                            #continue
                    else:
                        continue #If its not wiki page, move on to next link
                else:
                    if "wikipedia.org/" in link.get('href'): #its a proper link to wiki page. No need to prepend anything
                        new_page = link.get('href')
                        #skip_few_links = skip_few_links +1 
                        #if skip_few_links < 7:
                            #continue
                    else:
                        continue
                    
                html = self.getHtml(new_page)
                if html != None:
                    if html.find(rel = "canonical") is None:
                        continue
                    else:
                        new_url = html.find(rel = "canonical").get('href')
                        if new_url not in pageUrls:
                            pageUrls.append(new_url)
                            sleep(2) #Give some rest to wiki server
                            pageCount = pageCount + 1;
                            self.populate_listofPages(sqlObject,new_url,pageCount,listOfPages,pageUrls,pagesToBeDownloaded,html)
                            break
                            
    def get_references(self,html,refer):
        if html is None:
            return
        if html.find('ol',class_= "references") != None:
            for link in html.find('ol',class_= "references").find_all('li'):
                if link.find('span') is not None:
                    if link.find('span').find('a') is not None:
                        if link.find('span').find('a').get('href') is not None:
                            refer.append('https://en.wikipedia.org/wiki/India' + link.find('span').find('a').get('href'))
                else:
                    refer = None
                    break
            else:
                refer = None
        
    
    def dictionaryToList(self,listOfPages):
        """
        This method convert a dictionary into list of lists
        """
        wiki_list = []
        for key, value in listOfPages.iteritems():
            temp_list = []
            temp_list.append(key)
            #print("item1 = ",single_list)
            temp_list.append(value)
            #print("item2 =", single_list)
            wiki_list.append(temp_list)
            #print("wiki_list=",wiki_list)
        return(wiki_list)



class SQLDataBase(object):
    def __init__(self):
        pass
    
    def log_error(e):
        """ 
        This function just prints them, but you can
        make it do anything.
        """
        print(e)
    
    def addPagesToDataBase(self,wiki_list):
        """
        The method attempts to connect to database server. If successfull,
        each page's details are inserted in the database one by one.
        """
        db = MySQLdb.connect(host="localhost",db="wiki",user="root")
        try:
            db = MySQLdb.connect(host="localhost",db="wiki",user="root")
            Cursor = db.cursor()

            for list_temp in wiki_list:
                url = list_temp[0]
                #print("url = ",url)
                title= list_temp[1][0]
                #print("title = ",title)
                body=list_temp[1][1]
                if list_temp[1][2] is not None:
                    refer=",".join(list_temp[1][2])
                else:
                    refer = None
                #print("refer = ",refer)
                #print("url =",url)
                #print("title=", title)
                #print("refer = ",refer)

                url = url.encode('utf-8')
                title = title.encode('utf-8')
                if refer is not None:
                    refer = refer.encode('utf-8')
                body = body.encode('utf-8')

                Cursor.execute("INSERT INTO WikiTable (Wiki_Title, Wiki_URL, Wiki_Body, Wiki_References) VALUES (%s,%s,%s, %s)",(title,url,body,refer))

            db.commit()
            Cursor.close()
            db.close()
            print("Pages have been saved into SQL Database")
        except MySQLdb.Error:
            print("ERROR IN CONNECTION")

    def pageDetails(self,database,table,pageNumber):
        """
        The method returns a row from the table with index=pageNumber
        """
        if pageNumber < 1:
            log_error("Page number not in desired range")
            return
        try:
            db = MySQLdb.connect(host="localhost",db=database,user="root")
            Cursor = db.cursor()
            
            result = Cursor.execute("SELECT * from %s WHERE id = %s" % (table,pageNumber))
            
            if result !=0:
                #print("Rows produced by statement:",result)
                print("Details of page number :",pageNumber)
                print(Cursor.fetchall())
            else:
                print("Number of rows affected by statement:",result)
        except MySQLdb.Error:
            print("ERROR IN CONNECTION") 
            
    def leadingWildCardSearchOnPageTitle(self,database,table,columnName,pattern):
        """
        This method searches the Title column with leading
        wild card search for given pattern and dumps the returned 
        title in a file page.txt
        """
        try:
            db = MySQLdb.connect(host="localhost",db=database,user="root")
            Cursor = db.cursor()
            
            pattern = "%" + pattern
            result = Cursor.execute("SELECT %s FROM %s WHERE %s LIKE '%s'" % (columnName,table,columnName,pattern,))
            #result = Cursor.execute("SELECT (%s) FROM (%s) WHERE reverse(%s) LIKE '(%s)%'"%(columnName,table,columnName,reversePattern))
            if result!=0:
                print("Rows produced by statement:",result)
                f = open('pageWithLeading.txt','w')
                f.write(''.join(Cursor.fetchall()[0]))
                f.close()
                print("Search result has been written into file pageLeading.txt")
                print("Title of the selected page is returned from the query")
            else:
                print("Number of rows affected by statement:",result)
                
        except MySQLdb.Error:
            print("ERROR IN CONNECTION") 
    
    
    def reverseEachWordOfText(self,database,table,pattern,columnName):
        """
        This method searches the Title column with leading
        wildcard search and dumps the wordwise reversed title
        in a file page.txt
        """
        try:
            db = MySQLdb.connect(host="localhost",db=database,user="root")
            Cursor = db.cursor()
            
            pattern = "%" + pattern
            result = Cursor.execute("SELECT %s FROM %s WHERE %s LIKE '%s'" % (columnName,table,columnName,pattern))
            if result != 0:
                print("Rows produced by statement:",result)
                
                temp = ''.join(Cursor.fetchall()[0])
                
                # Spliting the result into words
                words = temp.split(" ")
     
                # Reversing each word and creating
                # a new list of words
                # List Comprehension
                newWords = [word[::-1] for word in words]
     
                # Joining the new list of words
                # to for a new Sentence
                reversedResult = " ".join(newWords)
                print(reversedResult)
                
                f = open('pageReversed.txt','w')
                f.write(reversedResult)
                f.close()
                print("Searched and reversed result has been written into file pageReversed.txt")
                print("Title of the selected page is returned from the query")
            else:
                print("Number of rows affected by statement:",result)
                
        except MySQLdb.Error:
            print("ERROR IN CONNECTION") 
    



def main(args):
    print("URL of the start page = ",args.page_url)
    print("Number of pages to be downloaded = ",args.num_pages)
    print("Doc Number to be retrieved from SQL Database= ",args.doc_num)
    print("Pattern to be searched in the database = ",args.pattern)
    print("Number of pages to be stored in  mongo = ",args.num_pages_to_mongodb)

    downloadPages_obj = DownloadWikiPages()
    saveToSQL_obj = SQLDataBase()

    if os.path.isfile("/home/ec2-user/viometasks_sol/DownloadedPageUrls.pkl"):
        pageUrlsHandle = open( "/home/ec2-user/viometasks_sol/DownloadedPageUrls.pkl", "rb" ) 
        pageUrls = pickle.load(pageUrlsHandle)
        pageUrlsHandle.close()
    else:
        pageUrls = []

    listOfPages = {}
    
    #Download wiki pages

    downloadPages_obj.populate_listofPages(saveToSQL_obj,args.page_url,0,listOfPages,pageUrls,args.num_pages)
    #wiki_list = downloadPages_obj.dictionaryToList(listOfPages)
    
    #Store the data into SQL database and perform queries
    #saveToSQL_obj.addPagesToDataBase(wiki_list)
    #saveToSQL_obj.pageDetails("wiki","WikiTable",args.doc_num)
    #saveToSQL_obj.leadingWildCardSearchOnPageTitle("wiki","WikiTable","Wiki_Title",args.pattern)
    #saveToSQL_obj.reverseEachWordOfText("wiki","WikiTable",args.pattern,"Wiki_Title")
    
    #Query SQL database and store into MongoDB
    #queryWikiPagesFromSQLToMongoDB("wiki","wiki","WikiTable",args.num_pages_to_mongodb)
    
    pageUrlsHandle = open( "/home/ec2-user/viometasks_sol/DownloadedPageUrls.pkl", "wb" ) 
    pickle.dump(pageUrls,pageUrlsHandle)
    pageUrlsHandle.close()
    print("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Arguments to MainScript.')
    parser.add_argument('--page_url', default='https://en.wikipedia.org/wiki/yoga',
                   help='URL of the first wiki page to start downloading')
    parser.add_argument('--num_pages', default=10, type=int,
                   help='Number of Wiki pages to be downloaded')
    parser.add_argument('--doc_num', default=1, type=int,
                   help='Wiki doc number to be retieved from SQL database')
    parser.add_argument('--pattern', default='pattern',
                   help='Pattern to be searched in the database')
    parser.add_argument('--num_pages_to_mongodb', default=5, type=int,
                   help='Pages to be saved to mongodb from SQL db')
    args = parser.parse_args()	
    main(args)
