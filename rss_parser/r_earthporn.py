from datetime import datetime
from time import struct_time
from typing import Optional

import feedparser

from . import Item, Url, Channel
from . import BaseParser


class Parser(BaseParser):
  def __init__(self, remote_url: str):
    super().__init__(remote_url)

  def get_title(self) -> str:
    return "Earth Porn"

  def get_updated_parsed(self, parserdict: feedparser.FeedParserDict) -> struct_time:
    return parserdict['feed']['updated_parsed']

  def get_link(self, parserdict: feedparser.FeedParserDict) -> Url:
    return Url(parserdict['href'])

  def get_channel(self, parserdict: feedparser.FeedParserDict):
    return parserdict['feed']

  def get_description(self, parserdict: feedparser.FeedParserDict):
    return parserdict['subtitle']

  def get_title_field(self, parserdict: feedparser.FeedParserDict) -> str:
    return parserdict['title']

  def get_item_title(self, parserdict: feedparser.FeedParserDict) -> str:
    return parserdict['title']

  def get_item_link(self, parserdict: feedparser.FeedParserDict) -> str:
    return parserdict['link']

  def get_item_comments(self, parserdict: feedparser.FeedParserDict) -> str:
    return ""

  def get_item_updated(self, parserdict: feedparser.FeedParserDict) -> struct_time:
    return parserdict['updated_parsed']

  def get_item_guid(self, parserdict: feedparser.FeedParserDict) -> str:
    return parserdict['id']

  def get_item_description(self, parserdict: feedparser.FeedParserDict) -> str:
    return ""

  def get_item_content_raw(self, parserdict: feedparser.FeedParserDict) -> str:
    return parserdict['content'][0]

  def create_item(self,
                  title: str,
                  link: Optional[Url],
                  comments: Optional[str],
                  pubDate: datetime,
                  guid: Optional[str],
                  description: Optional[str],
                  content_raw: Optional[str]) -> Item:
    pass