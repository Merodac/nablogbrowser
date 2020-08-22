import pathlib
import abc, importlib, sys
from lxml import etree
from typing import Union, Any, List, Optional, cast
from datetime import datetime
from time import mktime, struct_time
import feedparser



def _format_datetime(timestruct: struct_time) -> datetime:
  return datetime.fromtimestamp(mktime(timestruct))


class Url:
  target: str

  def __init__(self, target: str):
    self.target = target

  def __str__(self):
    return self.target


class Item:
  title: str
  link: Optional[Url]
  thumb_url: Optional[Url]
  comments: Optional[str]
  pubDate: datetime
  guid: Optional[str]
  description: Optional[str]
  content_raw: Optional[str]
  categories: List[str]

  def __init__(self,
               title: str,
               link: Optional[Url],
               thumb_url: Optional[Url],
               comments: Optional[str],
               pubDate: datetime,
               guid: Optional[str],
               description: Optional[str],
               content_raw: Optional[str]):
    self.title = title
    self.link = link
    self.thumb_url = thumb_url
    self.comments = comments
    self.pubDate = pubDate
    self.categories = []
    self.guid = guid
    self.description = description
    self.content_raw = content_raw


class Channel:
  title: str
  link: Url
  description: str
  items: List[Item]
  updated: datetime

  def __init__(self, title: str, updated: datetime, link: Url, description: str):
    self.title = title
    self.updated = updated
    self.link = link
    self.description = description
    self.items = []


class BaseParser(abc.ABC):
  remote_url: str

  def __init__(self, remote_url: str):
    self.remote_url = remote_url

  @abc.abstractmethod
  def get_title(self) -> str:
    pass

  def get_feed(self) -> feedparser.FeedParserDict:
    return feedparser.parse(self.remote_url)

  @abc.abstractmethod
  def get_updated_parsed(self, feed: feedparser.FeedParserDict) -> struct_time:
    pass

  @abc.abstractmethod
  def get_link(self, feed: feedparser.FeedParserDict) -> Url:
    pass

  @abc.abstractmethod
  def get_channel(self, feed: feedparser.FeedParserDict) -> feedparser.FeedParserDict:
    pass

  @abc.abstractmethod
  def get_description(self, feed: feedparser.FeedParserDict) -> str:
    pass

  @abc.abstractmethod
  def get_title_field(self, feed: feedparser.FeedParserDict) -> str:
    pass

  @abc.abstractmethod
  def get_item_title(self, parserdict: feedparser.FeedParserDict) -> str:
    pass

  @abc.abstractmethod
  def get_item_link(self, parserdict: feedparser.FeedParserDict) -> Url:
    pass

  @abc.abstractmethod
  def get_item_comments(self, parserdict: feedparser.FeedParserDict) -> str:
    pass

  @abc.abstractmethod
  def get_item_updated(self, parserdict: feedparser.FeedParserDict) -> struct_time:
    pass

  @abc.abstractmethod
  def get_item_guid(self, parserdict: feedparser.FeedParserDict) -> str:
    pass

  @abc.abstractmethod
  def get_item_description(self, parserdict: feedparser.FeedParserDict) -> str:
    pass

  @abc.abstractmethod
  def get_item_content_raw(self, parserdict: feedparser.FeedParserDict) -> str:
    pass

  def parse(self) -> Channel:
    feed = self.get_feed()

    updated_parsed_struct = self.get_updated_parsed(feed)
    updated_parsed = _format_datetime(updated_parsed_struct)
    link = self.get_link(feed)

    parsed_channel = self.get_channel(feed)
    title = self.get_title_field(parsed_channel)

    description = self.get_description(parsed_channel)

    channel = Channel(title=title, updated=updated_parsed, link=link, description=description)

    for item in feed['entries']:
      title = self.get_item_title(item)
      link = self.get_item_link(item)
      comments = self.get_item_comments(item)
      pubDate_struct = self.get_item_updated(item)
      pubDate_parsed = _format_datetime(pubDate_struct)
      guid = self.get_item_guid(item)
      description = self.get_item_description(item)
      content_raw = self.get_item_content_raw(item)

      parsed_item = self.create_item(title=title, link=link, comments=comments, pubDate=pubDate_parsed, guid=guid, description=description, content_raw=content_raw)
      if not parsed_item:
        continue
      channel.items.append(parsed_item)

    return channel

  @abc.abstractmethod
  def create_item(self,
                  title: str,
                  link: Optional[Url],
                  comments: Optional[str],
                  pubDate: datetime,
                  guid: Optional[str],
                  description: Optional[str],
                  content_raw: Optional[str]) -> Item:
    pass


def get_parser(url: str) -> Optional[BaseParser]:

  current_dir = pathlib.Path(__file__).parent.absolute()
  parser_plugins = [x.name for x in current_dir.iterdir() if x.is_file() and not x.match('*'+__file__)]
  for pp in parser_plugins:
    packagename = pp.split('.')[0]
    parser = get_parser_from_package('.' + packagename, url)
    if parser:
      print(f"Found parser: {parser.get_title()}")
      return parser


def get_parser_from_package(packagename: str, url: str):
  package = importlib.import_module(packagename, package='rss_parser')
  if package.can_parse(url):
    return package.Parser(url)
  if sys.getrefcount(package) < 5:  # TODO optimize
    del package
  pass


