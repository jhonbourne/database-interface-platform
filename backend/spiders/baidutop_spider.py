from lxml import etree
import time
from backend.utils.spider_utils import SpiderRequest, SqlPipeline

get_BaiduTopsearch_url = ("https://top.baidu.com/board?",{'tab':'realtime'})

class Xpaths(object):
    extract_topics = '//div[@class="category-wrap_iQLoo horizontal_1eKyQ"]'
    # xpath under topics:
    extract_content = '//div[@class="content_1YWBm"]'
    extract_hot_index = '//div[@class="hot-index_1Bl1a"]'
    # xpath under a content:
    extract_title = '//div[@class="c-single-text-ellipsis"]'
    extract_abstracts_large = '//div[contains(@class,' \
    '"hot-desc_1m_jR large_nSuFU ")]' # All long abstracts

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
        self.title = ""
        self.abstract = ""
        self.hot_index = 0

    def output_data(self):
        return tuple(self.__dict__.keys()), tuple(self.__dict__.values())
    
    @classmethod
    def dtype4sql(cls):
        # Corresponding to each attribute
        return {'title':'varchar(40) not null'
                ,'abstract':'varchar(200)'
                ,'hot_index':'int unsigned not null'}

class Spider(object):
    def __init__(self, url, **kwargs):
        self.url = url
        self.kwargs = kwargs
            
    def work(self):
        response = SpiderRequest.Put_Request(url=self.url, method='get', **self.kwargs)
        # print(response.url)
        # self.save_html(response)
        header_names, dat_list = self.parse(response)

        pipline = SqlPipeline()
        realtime = time.strftime("%Y_%b_%d__%H_%M_%S", time.localtime())
        tbl_name = 'BaiduTopsearch_'+realtime
        pipline.create_table(tbl_name,
                             column_setting=Item.dtype4sql(),
                             add_id_col=True, id_name='top_rank')
        pipline.write_data(tbl_name, header_names, dat_list)
        print(pipline.dial.select(tbl_name))
        # pipline.dial.delete_table(tbl_name)

    def parse(self, response, top_rank=10):
        html_string = response.text
        root = etree.HTML(html_string)
        # Get topic list of top search
        div_list = Xpaths.Parse(root, Xpaths.extract_topics
                                , is_sub=False, get_text=False, unpack=False)
        # Parse content of each top search
        dat_list = []
        for i, div in enumerate(div_list):
            if i < top_rank:
                item = Item()
                content = Xpaths.Parse(div, Xpaths.extract_content
                                       , get_text=False)
                item.title = Xpaths.Parse(content, Xpaths.extract_title).strip()
                item.abstract = Xpaths.Parse(content, Xpaths.extract_abstracts_large
                                             ,unpack=False)
                item.abstract = max(item.abstract,key=len).strip() # Filter different segments of a content
                item.hot_index = int(Xpaths.Parse(div,Xpaths.extract_hot_index))
                # Organize the data
                dat_row = item.output_data()[1]
                dat_list.append(dat_row)
                if i == 0:
                    header_names = item.output_data()[0]
                    header_names = header_names
                # if not dat_row[0] or not dat_row[1]:
                #     print(dat_row)
        return header_names, dat_list
    
    def save_html(self, response):
        html_string = response.text
        with open('BaiduTop.html', 'w', encoding='utf8') as f:
            f.write(html_string)

if __name__ == '__main__':
    spider = Spider(url=get_BaiduTopsearch_url[0]
                    ,**get_BaiduTopsearch_url[1])
    spider.work()