# -*- coding: utf-8 -*-

# Scrapy settings for crawl project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import os

BOT_NAME = 'crawl'

SPIDER_MODULES = [
    'crawl.spiders.common.crawlers',
    'crawl.spiders.openlaw.crawlers'
]
NEWSPIDER_MODULE = 'crawl.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'crawl (+http://www.yourdomain.com)'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML' \
             ', like Gecko) Chrome/80.0.3987.163 Safari/537.36'
# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 5  # 最大并发请求数量
DOWNLOAD_TIMEOUT = 10  # 下载请求超时
# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 1  # 下载延时
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#     'crawl.middlewares.CrawlSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'crawl.middlewares.CrawlDownloaderMiddleware': 543,
    'crawl.middlewares.CustomProxyMiddleware': 500,
    'crawl.middlewares.CustomRetryMiddleware': 510,
    # 'crawl.middlewares.FaxinVerifyMiddleware': 520,
    # 'crawl.middlewares.PuppeteerDownloaderMiddleware': 530  # pypeteer驱动
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'crawl.pipelines.CustomTwistedMongoDBPipline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

os.environ.setdefault("SETTINGS_MODULE", "crawl.settings")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
STATICS_DIR = os.path.join(BASE_DIR, "statics")
if not os.path.exists(STATICS_DIR):
    os.makedirs(STATICS_DIR)

DEBUG = False
LOG_LEVEL = 'INFO'
LOG_ENABLED = True
# '[%(asctime)s][%(thread)d][%(filename)s][line: %(lineno)d][%(levelname)s] ## %(message)s'
LOG_FORMAT = '[%(asctime)s][%(filename)s][line: %(lineno)d][%(levelname)s] ## %(message)s'
LOG_PATH = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)
# LOG_FILE = os.path.join(LOG_PATH, 'scrapy-log.log')

RETRY_TIMES = 5  # 下载中间件最大重试次数

REDIRECT_ENABLED = False  # 禁止重定向

DATABASES = {
    "es": {
        "timeout": 60,
        "type": "es",
        "http_auth": [
        ],
        "hosts": [
        ]
    },
    "redis": {
        "host": "",
        "port": 6379,
        "redis_max_connection": 50,
        "db": 0
    },
    "mysql": {
        "host": "",
        "port": 3306,
        "user": "",
        "passwd": "",
        "database": ""
    },
    "mongodb": {
        "host": "",
        "port": 10040,
        "user": "",
        "password": "",
        "db": ""
    },
}
