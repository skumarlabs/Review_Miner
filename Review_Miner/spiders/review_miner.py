import scrapy
from pprint import  pprint
import json
from .review import Review

class ReviewMinerSpider(scrapy.Spider):
    name = 'review_miner'
    DEFAULT_APPID = 'in.org.npci.upiapp'


    GOOGLE_PLAYSTORE_HOME = 'https://play.google.com/store/apps/details?id='
    #DATA_LOAD_MORE_SECTION_ID = 'div.data-load-more-section-id' # name of attribute identifying review panel having prev page button, review div and next page button
    #REVIEWS = 'div.reviews' # value of REVIEW_DIV_ATTR in that div
    #EXPAND_PAGES_CONTAINER = 'div.expand-pages-container' # div class which all contains all the reviews loaded at a time for app
    #EXPAND_PAGE = 'div.expand-page' # class of div having review in a single page. Have opacity 0 unless it is visible then 1

    #MULTICOL_COLUMN = 'div.multicol-column' # single column having review in column layout. Have visibility hidden

    SINGLE_REVIEW = 'div.single-review' # individual review div class
    #DEVELOPER_REPLY = 'div.developer-reply' # developer reply div class
    REVIEW_HEADER = 'div.review-header'

    REVIEW_INFO = ['div.review-info span.author-name::text',
                   'div.review-info span.review-date::text',
                   'div.review-info a.reviews-permalink::attr("href")',
                   'div.review-info-star-rating > div::attr("aria-label")']

    REVIEW_BODY = 'div.review-body::text'

    reviews = []

    def start_requests(self):       # returns a list of request or a generator to begin crawling
        #url = ''
        appid = getattr(self, 'appid', self.DEFAULT_APPID)
        if appid is not  None:
            urls = [self.GOOGLE_PLAYSTORE_HOME + appid]
        for url in urls:
            request = scrapy.Request(url=url, callback=self.parse)
            request.meta['appid'] = appid
            yield request


    def parse(self, response):
        appid = response.meta['appid']
        for review in response.css(self.SINGLE_REVIEW):

            new_review = Review()
            if review is not None:
                new_review.author = review.css(self.REVIEW_INFO[0]).extract_first()
                new_review.rating = review.css(self.REVIEW_INFO[3]).extract_first()
                #new_review.perma_link = review.css(self.REVIEW_INFO[2]).extract_first()

                new_review.text = review.css(self.REVIEW_BODY).extract()[1]


                self.reviews.append(new_review)

        filename = 'playstore-review-%s' % appid

        with open(filename, 'w') as f:
            #json.dump(self.reviews, f, default=lambda o: o.__dict__)
            json.dump([ob.__dict__ for ob in self.reviews], f)
            # f.write(response.body)
        self.log('Saved file %s' % filename)




