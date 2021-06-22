import praw
import csv
import re
import time
from datetime import date
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4


reddit = praw.Reddit()


class Scrapper:
    def __init__(self, sub, sort='hot', lim=100):
        self.sub = sub
        self.sort = sort
        self.lim = lim

    def get_sort(self):
        if self.sort == 'new':
            return reddit.subreddit(self.sub).new(limit=self.lim)
        elif self.sort == 'top':
            return reddit.subreddit(self.sub).top(limit=self.lim)
        elif self.sort == 'hot':
            return reddit.subreddit(self.sub).hot(limit=self.lim)
        else:
            self.sort = 'hot'
            print('Sort method was not recognized, defaulting to hot.')
            return reddit.subreddit(self.sub).hot(limit=self.lim)

    def get_tickers(self):

        stocks = {}
        with open('stock_tickers.csv', mode='r') as f:
            reader = csv.reader(f)
            for row in reader:
                stocks[row[0]] = 0

        subreddit = self.get_sort()

        print(f'Loading information from r/{self.sub}')

        start_time = time.time()
        for submission in subreddit:
            if submission.link_flair_text != 'Meme':
                for ticker in stocks.keys():
                    self.find_ticker(stocks, ticker, submission.selftext)
                    self.find_ticker(stocks, ticker, submission.title)
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments.list():
                        self.find_ticker(stocks, ticker, comment)

        end_time = time.time()
        print('Done!')
        print(f'Time taken: {(end_time - start_time)/60.0 :.2f} minutes')

        self.save_tickers(stocks)

    @staticmethod
    def find_ticker(stocks, ticker, text):
        if re.search(r'\s+\$?' + ticker + r'\$?\s+', str(text).upper()):
            stocks[ticker] += 1

    @staticmethod
    def save_tickers(stocks):
        stocks = dict(sorted(stocks.items(), key=lambda item: item[1], reverse=True)[:10])
        today = date.today()

        canvas = Canvas('top10.pdf', pagesize=A4)
        textobject = canvas.beginText()
        textobject.setTextOrigin(10, 730)
        textobject.setFont('Times-Roman', 12)
        textobject.textLine(text=str(today))

        for key, value in stocks.items():
            textobject.textLine(text=f'{key} : {value}')

        canvas.drawText(textobject)
        canvas.save()


if __name__ == '__main__':
    Scrapper('wallstreetbets', sort='hot', lim=10).get_tickers()
