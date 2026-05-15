import requests
import parsel
import csv
import time
import random
import re


class DangdangCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        }
        self.base_url = 'https://category.dangdang.com/cp01.00.00.00.00.00-srsort_sale_amt_desc-page-{}-dd_sale=on.html'

    def fetch_page(self, page):
        url = self.base_url.format(page)
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'gb2312'
            return response.text
        except Exception as e:
            print(f'获取第{page}页失败: {e}')
            return None

    def parse_books(self, html):
        selector = parsel.Selector(html)
        books = []

        # 查找所有商品项
        book_items = selector.css('ul.bigimg li')

        for item in book_items:
            try:
                # 提取书名
                title = item.css('p.name a::attr(title)').get('').strip()
                if not title:
                    continue

                # 提取价格 - 有两种格式
                price = '0'
                # 格式1: span i 里的 "18.97 - ¥0.19"
                price_text = item.css('p.price span i::text').get('')
                if price_text:
                    price_match = re.search(r'([\d.]+)', price_text)
                    if price_match:
                        price = price_match.group(1)
                else:
                    # 格式2: span.search_now_price 里的 "¥38.90"
                    price_list = item.css('p.price span.search_now_price::text').getall()
                    for p in price_list:
                        p = p.strip().replace('¥', '')
                        if p and p != '':
                            price = p
                            break

                # 提取详情链接
                detail_link = item.css('p.name a::attr(href)').get('')
                if detail_link and not detail_link.startswith('http'):
                    detail_link = 'https:' + detail_link

                # 提取评论数
                comment_text = item.css('p.search_star_line a::text').get('')
                comment_match = re.search(r'(\d+)条评论', comment_text)
                comments = comment_match.group(1) if comment_match else '0'

                # 提取作者信息
                author_spans = item.css('p.search_book_author span a::text').getall()
                author = author_spans[0].strip() if author_spans else ''

                # 提取出版社
                publisher_spans = item.css('p.search_book_author span a::text').getall()
                publisher = publisher_spans[1].strip() if len(publisher_spans) > 1 else ''

                # 提取出版日期
                date_text = item.css('p.search_book_author span::text').getall()
                pub_date = ''
                for text in date_text:
                    text = text.strip()
                    if '/' in text:
                        pub_date = text.replace('/', '').strip()
                        break

                book = {
                    '书名': title,
                    '售价': price,
                    '评论数': comments,
                    '作者': author,
                    '出版社': publisher,
                    '出版日期': pub_date,
                    '详情链接': detail_link
                }
                books.append(book)
            except Exception as e:
                print(f'解析书籍信息失败: {e}')
                continue

        return books

    def crawl(self, max_pages=5):
        all_books = []

        for page in range(1, max_pages + 1):
            print(f'正在爬取第{page}页...')
            html = self.fetch_page(page)

            if html:
                books = self.parse_books(html)
                all_books.extend(books)
                print(f'第{page}页爬取完成，获取{len(books)}本书籍')

            time.sleep(random.uniform(1, 2))

        return all_books

    def save_to_csv(self, books, filename='data/dangdang_books.csv'):
        if not books:
            print('没有数据可保存')
            return

        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=books[0].keys())
            writer.writeheader()
            writer.writerows(books)

        print(f'数据已保存到 {filename}，共{len(books)}条记录')
