import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.http import FormRequest
from bs4 import BeautifulSoup

# from scrapy.utils.markup import remove_tags
import newspaper
import json
from scrapy_selenium import SeleniumRequest


class Epaper(scrapy.Spider):
    name = "epaper"

    start_urls = ["https://epaper.thehindu.com/Login"]

    # def parse(self, response):
    #     request_token = response.xpath(
    #         '//*[@id="sectiNionA"]/div[1]/div/form/input[1]/@value'
    #     ).extract_first()
    #     print("here", request_token)
    #     return FormRequest.from_response(
    #         response,
    #         formdata={
    #             "Email": "shivam.jaiswal.18001@iitgoa.ac.in",
    #             "Password": "84662f",
    #             "__RequestVerificationToken": request_token,
    #             "hiddenTab": "https://epaper.thehindu.com/Login/LandingPage",
    #         },
    #         callback=self.get_all_page,
    #     )
    def parse(self, response):
        for date in ['%s/05/2020'%(i) for i in range(1, 30)] :
            yield scrapy.Request(
            url= "http://epaper.thehindu.com/Home/GetAllpages?editionid=115&editiondate=%s" % date,
            callback=self.after_login,
                cb_kwargs={
                    "date": date,
                },
            )
        # scrapy.fetch('http://epaper.thehindu.com/Home/GetAllpages?editionid=1&editiondate=07%2F09%2F2020')

    def after_login(self, response, date):
        print("hii shivam ", response)
        for i in json.loads(response.text):
            new_url = (
                "https://epaper.thehindu.com/Home/getStoriesOnPage?pageid=%s"
                % i["PageId"]
            )
            yield scrapy.Request(url=new_url,
                                 callback=self.get_all_stories,
                                 cb_kwargs={
                                     "date": date,
                                 },
                                 )

    def get_all_stories(self, response, date):
        for i in json.loads(response.text):
            complete_url = (
                "https://epaper.thehindu.com/User/ShowArticleView?OrgId=%s" % i["OrgId"]
            )
            full_article_url = (
                "https://epaper.thehindu.com/Home/ShareArticle?OrgId=%s&imageview=0"
                % i["OrgId"]
            )
            yield scrapy.Request(
                url=complete_url,
                callback=self.in_each_stories,
                cb_kwargs={
                    "storyid": i["storyid"],
                    "orgid": i["OrgId"],
                    "date": date,
                    "title": i["storyTitle"],
                    "link": full_article_url,
                    "summary": i["Summary"],
                },
            )

    def in_each_stories(self, response, storyid, date, orgid, title, link, summary):

        # print(
        #     "response = ",
        #     response,
        #     "storyid = ",
        #     storyid,
        #     "date = ",
        #     date,
        #     "orgid = ",
        #     orgid,
        #     "title = ",
        #     title,
        #     "summary = ",
        #     summary,
        # )

        x = json.loads(response.text)
        # print()

        yield {
            "response = ": response,
            "storyid = ": storyid,
            "date = ": date,
            "orgid = ": orgid,
            "title = ": title,
            "link = ": link,
            "page Number = ": x["PageNumber"],
            "summary = ": summary,
            "total news": BeautifulSoup(x["StoryContent"][0]["Body"]).getText(),
        }


# class Hinduepaper(scrapy.Spider):
#     name = "epaper"
#     request_with_cookies = scrapy.Request(
#         url="https://epaper.thehindu.com/Home/Mindex",
#     )

#     print(k)


class Chahal_Academy(scrapy.Spider):
    name = "chahal"

    # chahal = newspaper.build("")
    # print("category_urls")
    # for category in chahal.category_urls():
    #     print(category)
    # print("category_urls")

    start_urls = ["https://chahalacademy.com/important-monthly-editorial/5/2020"]

    def parse(self, response):
        # print("here", type(response))
        # link of all the newspaper
        request = scrapy.Request(
            response.url,
            callback=self.inside_website,
            cb_kwargs={"base_url": "https://chahalacademy.com/"},
        )
        request.cb_kwargs["site"] = "The Hindu"
        yield request
        # x = response.css(
        #     "#academyNav > div.classy-menu.m-auto > div.classynav > ul > li:nth-child(4) > ul li a::attr(href)"
        # ).getall()
        # for i in x:
        #     request = scrapy.Request(
        #         response.url + i,
        #         callback=self.inside_website,
        #         cb_kwargs={"base_url": response.url},
        #     )
        #     if "hindu" in i:
        #         # print(i, "hindu")
        #         request.cb_kwargs["site"] = "The Hindu"
        #     elif "indian-express" in i:
        #         request.cb_kwargs["site"] = "Indian-Express"
        #     else:
        #         request.cb_kwargs["site"] = "unknown - site"
        #     yield request

    def inside_website(self, response, base_url, site):

        cards = response.css(".row .blog-item").getall()
        # print("base_url ", base_url, " extension = ", response.url)
        for i in cards:
            sel = Selector(text=i)
            date = sel.xpath(
                "//div[contains(@class,'blog-item')]/div[contains(@class,'card-content')]/div[contains(@class,'card-desc')]/div/span[2]/text()"
            ).extract()[1]
            link = sel.xpath("//a/@href").extract()[0]
            # print("here", base_url + link)
            yield scrapy.Request(
                base_url + link,
                callback=self.each_date,
                cb_kwargs={"base_url": base_url, "date": date, "site": site},
            )
            # print("shiby ")

        return

    def each_date(self, response, base_url, date, site):
        print("response", response)

        if "important-current-affairs" in response.url:
            pageno = response.xpath(
                '//*[@id="blog-detail"]/div/div/div/div/div/p | //*[@id="blog-detail"]/div/div/div/div/div/table'
            )
            count = 0
            data = []
            lastpage = 0
            for i in range(len(pageno)):

                # print(Selector(text=pageno[i].get()))

                table = Selector(text=pageno[i].get()).xpath("boolean(//table)")
                # print(
                #     "checking element ",
                #     pageno[i],
                #     table.get(),
                #     pageno[i].css("p ::text").get(),
                #     "count = ",
                #     count,
                # )
                if (
                    table.get() == "0"
                    and pageno[i].css("p ::text").get() != "\xa0"
                    and "PAGE" in pageno[i].css("p ::text").get()
                ):

                    lastpage = pageno[i].css("p ::text").get()
                    # print("taking page no ", lastpage)
                    count = 1
                if table.get() == "1" and count == 1:
                    row = Selector(text=pageno[i].get()).xpath("//table//tr").getall()
                    table_data = []
                    # print("inside the table", (i, lastpage))
                    for j in range(len(row)):
                        # print(Selector(text=j).get())

                        # print(
                        #     "here",
                        #     (
                        #         Selector(text=j)
                        #         .xpath("//td/p/span/span/span/span/text()")
                        #         .getall()
                        #     ),
                        # )

                        # if len(table_data) != 0:
                        if j != 0:
                            # news = Selector(text=row[j].xpath(
                            #     "boolean(//td/p/span/span/span/span/)"
                            # )
                            table_data.append(
                                {
                                    "row no": j,
                                    "row-data": Selector(text=row[j])
                                    .xpath("//td/p/span/span/span/span/text()")
                                    .getall(),
                                }
                            )
                            h = " ".join(
                                Selector(text=row[j])
                                .xpath("//td/p/span/span/text()")
                                .getall()
                            )[0:]
                            table_data[j]["row-data"].insert(1, h)

                            if len(table_data[j]["row-data"]) == 2:
                                h = (
                                    Selector(text=row[j])
                                    .xpath("//td/p/span/span/a/span/span/text()")
                                    .getall()
                                )
                                table_data[j]["row-data"].append(h)

                        elif j == 0:
                            table_data.append(
                                {
                                    "row no": "heading",
                                    "row-data": Selector(text=row[j])
                                    .xpath("//td/p/span/span/strong/span/span/text()")
                                    .getall(),
                                }
                            )

                        # print("table data ", table_data)
                    data.append({"page_no": lastpage, "table": table_data})

            # print("data ", data)
            yield {"site": site, "url": response.url, "date": date, "data": data}


class NewsPaper_library(scrapy.Spider):
    name = "newspaper"
    start_urls = [
        "https://www.thehindu.com/opinion/lead/differential-impact-of-covid-19-and-the-lockdown/article32416854.ece"
    ]

    def parse(self, response):
        article = newspaper.Article(response.url, fetch_images=False)
        # print("author ", article.authors)
        article.download()
        article.parse()
        paper = newspaper.build(
            "https://www.thehindu.com/opinion/lead/differential-impact-of-covid-19-and-the-lockdown/article32416854.ece"
        )
        for article in paper.articles:
            print("marker", article.url)
        yield {
            "description": article.title,
            "summary": article.text,
        }


class from_response(scrapy.Spider):
    name = "from_response"

    start_urls = ["https://epaper.thehindu.com/Home/getstorydetail?Storyid=3823879/"]

    def parse(self, response):
        k = json.loads(response.text)
        print("here1", k)
        x = k["StoryContent"][0]
        print("lenght", len(k["StoryContent"]))
        for i in k["StoryContent"][0]:
            yield {i: k["StoryContent"][0][i]}


class CivilsDaily(scrapy.Spider):
    name = "civils"

    start_urls = ["https://www.civilsdaily.com/"]

    def parse(self, response):
        sources = response.css(".entry-title a::attr(href)").getall()
        for i in sources:
            yield scrapy.Request(i, callback=self.inside_website)

    def inside_website(self, response):
        y = response.url
        source1 = response.css(".meta-text a::attr(href)").getall()
        source2 = response.css(".meta-text a::attr(data-content)").extract_first()
        if source2 is not None:
            sel = Selector(text=source2)
            source2 = sel.css("iframe ::attr(src)").get()
        source = []
        # print("hello")
        # print("source 1 = ", source1, "source 2 = ", source2)
        CivilsDaily = re.compile(r"^https?:\/\/(www\.)?(civilsdaily.com/)")
        for i in source1:
            if not CivilsDaily.match(i):
                source.append(i)
        # print(type(source2))
        if type(source2) != str and source2 is not None:
            for i in source2:
                if not CivilsDaily.match(i):
                    source.append(i)
        else:
            if source2 is not None and not CivilsDaily.match(source2):
                source.append(source2)

        # print("source = ",source)
        try:
            for i in source:
                # print("here",type(source))
                yield scrapy.Request(i, callback=self.source_website)
        except:
            print("exception big ", source)

    def source_website(self, response):
        y = response.url
        # print(y)
        india_express_regex = re.compile(
            r"https?:\/\/(www\.)?(indianexpress.com/)\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
        )
        the_hindu_regex = re.compile(r"^https?:\/\/(www\.)?(thehindu.com/)")

        site_name = ""
        # print("site name ", str(y))
        if india_express_regex.match(str(y)):
            site_name = "indian express"
        elif the_hindu_regex.match(str(y)):
            site_name = "the hindu"
        else:
            site_name = "none"
        # print("site name ", site_name)
        details = 0
        try:
            if site_name == "the hindu":
                details = response.css(".paywall p::text").getall()
            elif site_name == "indian express":
                details = response.css(".full-details p::text").getall()
        except:
            print(response.url)
        article = newspaper.build(
            response.url, memoize_articles=False, fetch_images=False
        )
        article.download()
        article.parse()
        # print("author ", article.authors)
        yield {"content": article.feed_urls()}
        # yield {
        #     "site name": site_name,
        #     "url": y,
        #     "information": details,
        # }
        return

class PostsSpider(scrapy.Spider):
    name = "posts"

    def __init__(self, group=None, *args, **kwargs):
        super(PostsSpider, self).__init__(*args, **kwargs)
        for i in range(1, 32):
            base = (
                "https://www.insightsonindia.com/2020/01/%s/insights-daily-current-affairs-pib-summary-%s-january-2020/"
                % (str(i), str(i))
            )
            self.start_urls.append(base)

    rules = []

    def parse(self, response):

        sources = response.xpath(
            "/html/body/div[1]/div/div[1]/div/div/main/div/div[1]/div/div[1]/article/div/div/p/span/em/a/@href"
        ).getall()
        # print(sources)
        yield {"len ": len(sources), "sources": sources}
        for i in sources:
            yield scrapy.Request(i, callback=self.subsite)
        #     response.follow(i, self.subsite)

        # if next_page is not None:
        #     next_page = response.urljoin(next_page)
        #     yield scrapy.Request(next_page, callback=self.parse)

    def subsite(self, response):
        y = response.url

        # print("response y", y)

        india_express_regex = re.compile(
            r"https?:\/\/(www\.)?(indianexpress.com/)\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
        )
        the_hindu_regex = re.compile(r"^https?:\/\/(www\.)?(thehindu.com/)")

        site_name = ""
        print("site name ", str(y))
        if india_express_regex.match(str(y)):
            site_name = "indian express"
        elif the_hindu_regex.match(str(y)):
            site_name = "the hindu"
        else:
            site_name = "none"
        print("site name ", site_name)
        details = 0
        if site_name == "the hindu":
            details = response.css(".paywall p::text").getall()
        elif site_name == "indian express":
            details = response.css(".full-details p::text").getall()

        yield {
            "site name": site_name,
            "url": y,
            "information": details,
        }
        return
        # information_all = dict()
        # if site_name == "the hindu":
        #     information_all[site_name] = site_name
        # elif site_name == "indian express":
        #     information_all[site_name] = site_name

        # full-details
