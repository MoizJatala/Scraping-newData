import scrapy
import csv
import os

class PolitifactSpider(scrapy.Spider):
    name = "politifact"
    allowed_domains = ["politifact.com"]
    start_urls = ["https://politifact.com"]

    def __init__(self):
        self.data = {
            'articles': [],
            'a_text': [],
            'time_text': [],
            'span_text': [],
            'h1_text': [],
            'h2_text': [],
            'div_text': [],
            'videos': [],
        }

    def parse(self, response):

        a_s = response.css('div.m-statement__quote a')
        imgs = response.css('img')
        times = response.css('time')
        spans = response.css('span')

        for div in a_s:
            link = div.css('::attr(href)').get()
            if link and link.startswith(('factchecks','article')):
                self.data['a_text'].append(div.css('::text').get())
        
        for img in imgs:
            image_url = img.css('::attr(src)').get()
            if image_url:
                if image_url.startswith(('http:', 'https:')):
                    yield scrapy.Request(url=image_url, callback=self.save_image)
                else:
                    # Handle cases where the URL is missing a scheme
                    absolute_url = response.urljoin(image_url)
                    yield scrapy.Request(url=absolute_url, callback=self.save_image)

        for time in times:
            self.data['time_text'].append(time.css('::text').get())

        for span in spans:
            self.data['span_text'].append(span.css('::text').get())
        view_all= response.css('footer.o-platform__link')
        view = view_all.css('a::attr(href)').get()
        if view is not None:
            absolute_url = response.urljoin(view)
            yield response.follow(url=absolute_url, callback=self.view_func)
        yield self.data

    def view_func(self,response):
        a_s = response.css('div.m-statement__quote a')
        h_a_s = response.css('h3.m-teaser__title a')
        imgs = response.css('img')
        times = response.css('time')
        spans = response.css('span')
        for div in a_s:
            link = div.css('::attr(href)').get()
            if link and not link.startswith(('factchecks','article')):
                self.data['a_text'].append(div.css('::text').get())
                absolute_url = response.urljoin(link)
                yield response.follow(url=absolute_url, callback=self.articleparse)
        
        for div in h_a_s:
            link = div.css('::attr(href)').get()
            if link and not link.startswith(('javascript:', 'tel:', 'mailto:')):
                self.data['a_text'].append(div.css('::text').get())
                absolute_url = response.urljoin(link)
                yield response.follow(url=absolute_url, callback=self.articleparse)

        for img in imgs:
            image_url = img.css('::attr(src)').get()
            if image_url:
                if image_url.startswith(('http:', 'https:')):
                    yield scrapy.Request(url=image_url, callback=self.save_image)
                else:
                    # Handle cases where the URL is missing a scheme
                    absolute_url = response.urljoin(image_url)
                    yield scrapy.Request(url=absolute_url, callback=self.save_image)

        for time in times:
            self.data['time_text'].append(time.css('::text').get())

        for span in spans:
            self.data['span_text'].append(span.css('::text').get())

        next_all = response.css('ul.m-list.m-list--centered li:last-child')
        next_link = next_all.css('a::attr(href)').get()
        if next_link is not None:
            absolute_url = response.urljoin(next_link)
            yield response.follow(url=absolute_url, callback=self.view_func)

        yield self.data

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
        h2 = response.css('h2')
        divs = response.css('div')
        paras = response.css('p')
        imgs = response.css('img')
        videos_iframe = response.css('iframe')

        for h in h1:
            self.data['h1_text'].append(h.css('::text').get())

        for h in h2:
            self.data['h2_text'].append(h.css('::text').get())
        
        for div in divs:
            self.data['div_text'].append(div.css('::text').get())

        for para in paras:
            self.data['articles'].append(para.css('::text').get())

        for img in imgs:
            image_url = img.css('::attr(src)').get()
            if image_url:
                if image_url.startswith(('http:', 'https:')):
                    yield scrapy.Request(url=image_url, callback=self.save_image)
                else:
                    # Handle cases where the URL is missing a scheme
                    absolute_url = response.urljoin(image_url)
                    yield scrapy.Request(url=absolute_url, callback=self.save_image)

        for video in videos_iframe:
            self.data['videos'].append(video.css('::attr(src)').get())

        yield self.data

    def closed(self, reason):
        # Save video data to a CSV file
        with open('video_data.csv', 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.video_data.keys())
            writer.writeheader()
            writer.writerow(self.video_data)

        # Save text data to a CSV file
        with open('text_data.csv', 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.text_data.keys())
            writer.writeheader()
            writer.writerow(self.text_data)


