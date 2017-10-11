import argparse
import sys
import time
import re

import requests
from bs4 import BeautifulSoup
from review import Review


def get_playstore_review_by_appid(appid, iter, sortOrder):
    ''' Returns a list of reviews for an app in playstore.
        Each review is a object having below attributes:
        1. 'author_name' : The name of reviewer
        2. 'review_rating' : The rating given by reviewer
        3. 'review_date' : The date of review posted
        4. 'review_text' : The actual text content of review

    '''

    page_num = 0
    review_count = 0
    corpus = []

    for i in range(iter):

        payload = {'reviewType': '0',
                   'pageNum': page_num,
                   'id': appid,
                   'reviewSortOrder': sortOrder,  # Newest : 0, Rating: 1, Helpfullnew : 2
                   'xhr': 1,
                   'hl': 'en'
                   }

        headers = {'Host': 'play.google.com',
                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
                   # 'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                   'Connection': 'keep-alive',
                   'Content-Type': 'application/x-www-form-urlencoded;charset=ISO-8859-1',
                   'Referer': 'https://play.google.com/store/apps/details?id=' + appid,
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'en-US,en;q=0.5',
                   'Accept': '*/*'
                   }
        time.sleep(REQUEST_DELAY_TIME)
        # s = requests.Session()
        proxies = {
            'http': 'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050'
        }
        r = requests.post("https://play.google.com/store/getreviews?authuser=0", headers=headers, proxies=proxies,
                   data=payload)

        if r.status_code == 200:
            if r.text != '':
                resp_text = (r.text).replace('\\u003c', '<'). \
                    replace('\\u003d', '='). \
                    replace('\\u003e', '>'). \
                    replace('\\u0026amp;', '&'). \
                    replace('\\"', '"')

                ugly_prefix_index = resp_text.find('<div')
                html_doc = resp_text[ugly_prefix_index:].strip(']').strip()
                if html_doc != '':
                    soup = BeautifulSoup(html_doc, 'html.parser')
                    review_div_list = soup.find_all('div', class_='single-review')

                    for review_div in review_div_list:
                        author_name_tag = review_div.find("span", class_='author-name')
                        review_date_tag = review_div.find("span", class_='review-date')
                        review_rating_tag = review_div.find("div", class_='star-rating-non-editable-container')
                        review_div.find("div", class_="review-link").clear()
                        review_text_tag = review_div.find("div", class_='review-body')

                        author_name = author_name_tag.get_text().strip()
                        review_date = review_date_tag.get_text().strip()

                        review_text = review_text_tag.get_text().strip()
                        review_text = ' '.join(review_text.split())
                        
                        #review_text =  re.sub(r'[^\x00-\x7F]+', r'', review_text)  # use it to convert into all ascii code
                        review_rating = review_rating_tag['aria-label'].strip()
                        review = Review(appid, author_name, review_rating, review_date, review_text)
                        corpus.append(str(review))
                        review_count += 1

                else:  # html has some content
                    break  # else no review
            else:  # returned response has some content
                break  # else no review
        else:  # status code != 200
            if r.status_code == 400:  # if page not found
                break  # no more reviews
            else:  # else something bad happened. show status code
                sys.stdout.write("Something bad happened! status code - %d" % r.status_code)
                sys.exit(STATUS_CODE_NOT_200)

        page_num += 1
        sys.stdout.write('\r Iterations Completed: %s' % str(page_num))
    sys.stdout.write('\n No more reviews found! Total %s reviews added.' % str(review_count))

    return corpus


def main(args):
    if not args.appid:
        sys.stdout.write('app id not given. exiting!')
        sys.exit(APP_ID_NOT_GIVEN)

    appid = args.appid if args.appid else sys.stdout.write('app id not given! exiting..\n')
    iters = args.iters if args.iters else 1000
    order_by = args.order_by if args.order_by else 0
    REQUEST_DELAY_TIME = args.request_delay_time if args.request_delay_time else 0

    corpus = get_playstore_review_by_appid(appid, iters, order_by)
    filename = '%s-reviews.txt' % appid.replace('.', '_')
    with open(filename, mode='w', encoding='utf-8') as f:
        # json.dump(corpus, f)
        f.write('\n'.join(corpus))


if __name__ == "__main__":
    APP_ID_NOT_GIVEN = 1
    STATUS_CODE_NOT_200 = 2
    REQUEST_DELAY_TIME = 0
    parser = argparse.ArgumentParser(description='Get playstore reviews for an app')
    parser.add_argument('--appid', action='store', dest='appid', type=str, help='app id (mandatory)')
    parser.add_argument('--iters', action='store', dest='iters', type=int,
                        help='An integer specifying number of iterations to fetch reviews. Default: All')
    parser.add_argument('--orderby', action='store', dest='order_by', type=int,
                        help='Fetch reviews ordered by: 0 for Newest, 1 for Rating, 2 for Helpfulness. Default 0')
    parser.add_argument('-d', action='store', dest='request_delay_time', type=float,
                        help='Delay in seconds before making new network page request')
    args = parser.parse_args()
    main(args)
