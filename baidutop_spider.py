from lxml import etree
import time
from spider_utils import SpiderRequest, SqlPipeline

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
    def __init__(self, url="https://top.baidu.com/board?", **kwargs):
        self.url = url
        if not 'tab' in kwargs.keys():
            kwargs['tab'] = 'realtime'        
        self.kwargs = kwargs
            
    def work(self):
        response = SpiderRequest.Put_Request(url=self.url, method='get', **self.kwargs)
        # print(response.url)
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
        div_list = root.xpath('//div[@class="category-wrap_iQLoo horizontal_1eKyQ"]')
        # Parse content of each top search
        dat_list = []
        for i, div in enumerate(div_list):
            if i < top_rank:
                item = Item()
                content = div.xpath('.//div[@class="content_1YWBm"]')[0]
                item.title = content.xpath('.//div[@class=' \
                '"c-single-text-ellipsis"]/text()')[0].strip()
                item.abstract = content.xpath('.//div[contains(@class,' \
                '"hot-desc_1m_jR large_nSuFU ")]/text()')
                item.abstract = max(item.abstract,key=len).strip()
                item.hot_index = int(div.xpath('.//div[@class="hot-index_1Bl1a"]/text()')[0])
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
    spider = Spider()
    spider.work()