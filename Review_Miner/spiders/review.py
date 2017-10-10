class Review:
    '''A class for review fetched from Playstore.'''
    def __init__(self):
        ''' Initialize an empty review. '''
        self.appid = ''
        self.author_name = ''
        self.review_rating = -1
        self.review_date = ''
        self.review_text = ''

    def __init__(self, appid, author_name, review_rating, review_date, review_text):
        ''' Initialize a review with parameter.
        'author_name' is the name of reviewer
        'review_rating' is the rating given by reviewer
        'review_date' is the date of review posted
        'review_text' is the actual text content of review
         '''
        self.appid = appid
        self.author_name = author_name
        self.review_rating = review_rating
        self.review_date = review_date
        self.review_text = review_text

    def __str__(self):
        return self.appid + '\t' + \
               self.author_name + '\t' + \
               self.review_rating + '\t' + \
               self.review_text + '\t' + \
               self.review_date
