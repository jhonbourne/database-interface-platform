from lxml import etree
import time
from backend.utils.spider_utils import SpiderRequest, SqlPipeline

get_DoubanTopmovie_url = ("https://movie.douban.com/top250?"
                          ,{'start':0 # Start rank shown in the page. 0 means top1 movie
                            }
                          )

class Xpaths(object):
    extract_movies = '//ol[@class="grid_view"]/li'
    # xpath under list of movies:
    extract_top_rank = '//div[@class="pic"]/em'
    extract_title = '//div[@class="hd"]//span[@class="title"]' # [Chinese title, English title]
    extract_info = '//div[@class="bd"]/p' # [credits, year/country/movie type,'','']
    extract_rating = '//div[@class="bd"]//span[@class="rating_num"]'

    @classmethod
    def Parse(cls, etree_ele, xpath_str, is_sub=True, get_text=True, unpack=True):
        # encapsulated function of get parse content when using lxml
        prefix = '.' if is_sub else ''
        suffix = '/text()' if get_text else ''
        content = etree_ele.xpath(prefix + xpath_str + suffix)
        if unpack:
            content = content[0]
        return content

class Item(object):
    def __init__(self):
        self.title_CN = ""
        self.info = ""
        self.top_rank = 0
        self.rating = 0.0

    def output_data(self):
        return tuple(self.__dict__.keys()), tuple(self.__dict__.values())
    
    @classmethod
    def dtype4sql(cls):
        # Corresponding to each attribute
        return {'title_CN':'varchar(40) not null'
                ,'info':'varchar(200)'
                ,'top_rank':'int unsigned not null'
                ,'rating':'float unsigned'}
    
class Spider(object):
    def __init__(self, url, get_movie_num=100, **kwargs):
        self.url = url
        self.kwargs = kwargs
        self.get_movie_num = get_movie_num
            
    def work(self):
        dat_merge = []
        while len(dat_merge) < self.get_movie_num:
            response = SpiderRequest.Put_Request(url=self.url, method='get', **self.kwargs)
            # print(response.url)
            # print(response.status_code)
            # self.save_html(response)
            header_names, dat_list = self.parse(response)
            # Number of aquired movies should be equal to 'get_movie_num'
            append_len = min(len(dat_list), self.get_movie_num-len(dat_merge))
            dat_merge += dat_list[:append_len]
            self.kwargs['start'] += append_len

            time.sleep(1) # Avoid anti-spider mechanisms
        print(len(dat_merge))

        pipline = SqlPipeline()
        realtime = time.strftime("%Y_%b_%d", time.localtime())
        tbl_name = 'DoubanTopmovies_'+realtime
        pipline.create_table(tbl_name,
                             column_setting=Item.dtype4sql())
        pipline.write_data(tbl_name, header_names, dat_merge)
        print(pipline.dial.select(tbl_name))
        # pipline.dial.delete_table(tbl_name)

    def parse(self, response):
        html_string = response.text
        root = etree.HTML(html_string)
        # Get the list of movies in the current page
        mov_list = Xpaths.Parse(root, Xpaths.extract_movies
                                , is_sub=False, get_text=False, unpack=False)
        # Parse content of each movie
        dat_list = []
        for i, li in enumerate(mov_list):
            item = Item()
            item.top_rank = int(Xpaths.Parse(li,Xpaths.extract_top_rank))
            item.title_CN = Xpaths.Parse(li,Xpaths.extract_title) # Get the 1st element
            info = Xpaths.Parse(li, Xpaths.extract_info, unpack=False)
            # Join the info contents
            info = [s.strip().replace('\xa0',' ') for s in info]
            info = "|".join(info[:2])
            item.info = info
            item.rating = float(Xpaths.Parse(li, Xpaths.extract_rating))
            # Organize the data
            dat_row = item.output_data()[1]
            dat_list.append(dat_row)
            if i == 0:
                header_names = item.output_data()[0]
                header_names = header_names
        return header_names, dat_list

    def save_html(self, response):
        html_string = response.text
        with open('DoubanTop.html', 'w', encoding='utf8') as f:
            f.write(html_string)

if __name__ == '__main__':
    spider = Spider(url=get_DoubanTopmovie_url[0]
                    ,**get_DoubanTopmovie_url[1])
    spider.work()