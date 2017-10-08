import argparse
import json

import requests
from bs4 import BeautifulSoup
from review import Review


def unescapematch(matchobj):
    ''' To unescape a unicode value to a unicode character.
        Pass this function to repl parameter of re.sub()  '''
    escapesequence = matchobj.group(0)
    digits = escapesequence[2:]
    ordinal = int(escapesequence, 16)
    char = chr(ordinal)
    return char


def removeUnicode(text):
    ''' To unescape a text into its ascii value.
         '''
    if (isinstance(text, str)):
        return text.decode('utf-8').encode("ascii", "ignore")
    else:
        return text.encode("ascii", "ignore")

    return text


def get_playstore_review_by_appid(appid, iter, sortOrder):
    ''' Returns a list of reviews for an app in playstore.
        Each review is a object having below attributes:
        1. 'author_name' : The name of reviewer
        2. 'review_rating' : The rating given by reviewer
        3. 'review_date' : The date of review posted
        4. 'review_text' : The actual text content of review

    '''
    page_num = 0
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
        r = requests.post("https://play.google.com/store/getreviews?authuser=0", headers=headers, data=payload)
        # print(r.status_code)
        if r.text != '' and r.status_code == 200:

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
                    # review_text = removeUnicode(review_text)
                    # review_text =  re.sub('\\\\u[\w]{4}', '', review_text, re.UNICODE)
                    review_rating = review_rating_tag['aria-label'].strip()
                    review = Review(author_name, review_rating, review_date, review_text)
                    corpus.append(review.__dict__)

            else:
                break
        else:
            break
        page_num += 1
        print('page number ' + str(page_num) + " done")

    return corpus


def main(args):
    appid = args.appid if args.appid else 'in.org.npci.upiapp'
    iters = args.iters if args.iters else 1
    order_by = args.order_by if args.order_by else 0

    print(appid, iters, order_by)
    corpus = get_playstore_review_by_appid(appid, iters, order_by)
    filename = '%s-reviews.txt' % appid
    with open(filename, mode='w', encoding='utf-8') as f:
        json.dump(corpus, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get playstore reviews for an app')
    parser.add_argument('--appid', action='store', dest='appid', type=str, help='App Id. Default in.org.npci.upiapp')
    parser.add_argument('--iters', action='store', dest='iters', type=int,
                        help='An integer specifying number of iterations to fetch reviews. Default 5')
    parser.add_argument('--orderby', action='store', dest='order_by', type=int,
                        help='Fetch reviews ordered by: 0 for Newest, 1 for Rating, 2 for Helpfulness. Default 0')
    args = parser.parse_args()
    main(args)