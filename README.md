# Crawl wikipedia pages and save them to sql and mongo db
Please follow the given steps to setup and execute everything -
  
Change mode of all the provided scripts with the following command -

chmod 755 SCRIPTNAME (where SCRIPTNAME will be Install.sh, MainScript.sh )

1. Run the Install.sh script with the command -
    ./Install.sh
    It will install all the packages required for the assignment.

2. Execute the steps given in the ReadMeForRunningSQLServer.txt to run the SQL server.

3. Execute the steps given in the ReadMeForRunningMongoDB.txt to run MongoDb.

4. Execute the MainScript.sh. Command to run the script is-
      python MainScript.py --num_pages NUM_PAGES --doc_num DOC_NUM --pattern PATTERN --num_pages_to_mongodb NUM_PAGES_TO_MONGODB
      
      Arguments to MainScript.

    optional arguments:
  
    --num_pages NUM_PAGES                        Number of Wiki pages to be downloaded
                        
    --doc_num DOC_NUM                            Wiki doc number to be retieved from SQL database
    
    --pattern PATTERN                            Pattern to be searched in the database
    
    --num_pages_to_mongodb NUM_PAGES_TO_MONGODB  Pages to be saved to mongodb from SQL db

    This script downloads NUM_PAGES Wikipedia pages and stores them to sql database. Then, it searches  the Title column of the stored wikipedia pages for PATTERN (leading wildcard search). If the pattern is present,
    the corresponding title/s are written to PageLeading.txt. The result of the same search is stored in PageReversed.txt with every word of the result reversed.The script
    also stores NUM_PAGES_TO_MONGODB pages from the sql database to mongodb.

5. Execute the following SQL query from the sql> to allow leading wild card search

SELECT * FROM WikiTable WHERE Wiki_Title LIKE '%PATTERN' where PATTERN is the string/pattern to be searched

                                        OR

SELECT * FROM WikiTable WHERE reverse(Wiki_Title) LIKE reverse('%PATTERN') where PATTERN is the string/pattern to be searched

Note: The trailing wildcard search will run comparitively faster in case text to be searched for the pattern is very large because the leading wildcard serach has to go through all the text to search for the pattern.



