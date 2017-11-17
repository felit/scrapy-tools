from scrapy.dupefilters import BaseDupeFilter
import logging
from scrapy.utils.request import request_fingerprint

logger = logging.getLogger(__name__)


class DupeFilter(BaseDupeFilter):
    """
    url:
    """

    def __init__(self):
        pass

    @classmethod
    def from_crawler(cls, crawler):
        pass

    @classmethod
    def from_settings(cls, settings):
        pass

    def request_seen(self, request):
        """
        给予请求，查看其是否请求过，即是否过滤掉，
        True:过滤掉
        False:不过滤掉
        :param request:
        :return:
        """
        pass

    def request_fingerprint(self, request):
        pass

    def close(self, reason=''):
        pass