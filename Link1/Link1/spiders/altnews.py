import scrapy
import os
import csv

class AltnewsSpider(scrapy.Spider):
    name = "altnews"
    allowed_domains = ["altnews.in"]
    start_urls = ["https://altnews.in"]

    def __init__(self):
        self.data = {
            'articles': [],
            'a_text': [],
            'time_text': [],
            'span_text': [],
            'h_text': [],
            'videos': [],
        }

    def parse(self, response):

        a_s = response.css('a')
        imgs = response.css('img')
        times = response.css('time')
        spans = response.css('span')

        for div in a_s:
            link = div.css('::attr(href)').get()
            if link and not link.startswith(('javascript:', 'tel:', 'mailto:')):
                self.data['a_text'].append(div.css('::text').get())
                absolute_url = response.urljoin(link)
                yield response.follow(url=absolute_url, callback=self.articleparse)

        for img in imgs:
            image_url = img.css('::attr(src)').get()
            if image_url:
                yield scrapy.Request(url=image_url, callback=self.save_image)

        for time in times:
            self.data['time_text'].append(time.css('::text').get())

        for span in spans:
            self.data['span_text'].append(span.css('::text').get())

        yield response.css('div.pbs-vars.hidden', callback=self.parse)

    def save_image(self, response):
        folder_path = 'images'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        ext = response.url.split("/")[-1]
        filename = os.path.join(folder_path, f'downloaded_image.{ext}')

        with open(filename, 'wb') as f:
            f.write(response.body)

    def articleparse(self, response):
        h1 = response.css('h1')
        paras = response.css('p')
        imgs = response.css('img')
        videos = response.css('a.css-4rbku5.css-18t94o4.css-1dbjc4n.r-1loqt21')
        videos_iframe = response.css('iframe')

        for h in h1:
            self.data['h_text'].append(h.css('::text').get())

        for para in paras:
            self.data['articles'].append(para.css('::text').get())

        for img in imgs:
            image_url = img.css('::attr(src)').get()
            if image_url:
                yield scrapy.Request(url=image_url, callback=self.save_image)

        for video in videos:
            self.data['videos'].append(video.css('::attr(href)').get())

        for video in videos_iframe:
            self.data['videos'].append(video.css('::attr(src)').get())

        yield self.data

    def closed(self, reason):
        with open('scraped_data.csv', 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.data.keys())
            writer.writeheader()
            writer.writerow(self.data)

