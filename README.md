# Review_Miner
A simple crawler to fetch review from play store. There are two scripts. Choose either of them.


## For simple small 10-20 review corpus, choose below.

This is a simple web crawler implemented in python to fetch user reviews from playstore for a given appid.

1)  Requirements: Python 3, Scrapy

2)  To run the script execure below command from the root of the project:
   
    $scrapy crawl review_miner -a appid=xxx.xxxx.xxx 
 
    where xxx.xxxx.xxx is the appid of your app. 
   
## For large review corpus, follow below.
  
1)  cd to /Review_Miner/Review_Miner/spiders/ and run playstore_reviews.py. See usage by
  
    $python playstore_reviews.py --help

2) Then, read the created text file having list of reviews using something like below:
    
      
      with open('reviews.txt') as f:
      
           reviews_list = json.loads(f.read())  
   
Please use this script for educational purpose only.
