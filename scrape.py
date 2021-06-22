import praw
import csv
import re
import time
from fpdf import FPDF

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
        print(f'Time taken: {end_time - start_time}')

        self.save_tickers(stocks)

    @staticmethod
    def find_ticker(stocks, ticker, text):
        if re.search(r'\s+\$?' + ticker + r'\$?\s+', str(text)):
            stocks[ticker] += 1

    @staticmethod
    def save_tickers(stocks):
        dict(sorted(stocks.items(), key=lambda item: item[1], reverse=True)[:10])
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', size=18)

        for key, value in stocks:
            pdf.cell(200, 10, txt=f'{key} : {value}', ln=1, allign='L')

        pdf.output('top10_tickers.pdf')

if __name__ == '__main__':
    Scrapper('wallstreetbets', sort='hot', lim=100).get_tickers()
