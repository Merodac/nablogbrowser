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
  comments: Optional[str]
  pubDate: datetime
  guid: Optional[str]
  description: Optional[str]
  content_raw: Optional[str]
  categories: List[str]

  def __init__(self,
               title: str,
               link: Optional[Url],
               comments: Optional[str],
               pubDate: datetime,
               guid: Optional[str],
               description: Optional[str],
               content_raw: Optional[str]):
    self.title = title
    self.link = link
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
  site: Optional[str]
  items: List[Item]
  updated: datetime

  def __init__(self, title: str, updated: datetime, link: Url, description: str, site: Optional[str]):
    self.title = title
    self.updated = updated
    self.link = link
    self.description = description
    self.site = site
    self.items = []


class BaseParser:
  remote_url: str

  def __init__(self, remote_url: str):
    self.remote_url = remote_url

  def parse(self) -> Channel:
    parse_result = feedparser.parse(self.remote_url)

    updated_parsed_struct = parse_result['updated_parsed']
    updated_parsed = _format_datetime(updated_parsed_struct)
    link = Url(parse_result['href'])

    parsed_channel = parse_result['channel']
    title = parsed_channel['title']

    description = parsed_channel['description']
    site = parsed_channel['site']
    channel = Channel(title=title, updated=updated_parsed, link=link, description=description, site=site)

    for item in parse_result['entries']:
      title = item['title']
      link = Url(item['link'])
      comments = item['comments']
      pubDate_struct = item['published_parsed']
      pubDate_parsed = _format_datetime(pubDate_struct)
      guid = item['guid']
      description = item['description']
      content_raw = item['content'][0].value

      parsed_item = self.create_item(title=title, link=link, comments=comments, pubDate=pubDate_parsed, guid=guid, description=description, content_raw=content_raw)
      channel.items.append(parsed_item)

    return channel

  def create_item(self,
                  title: str,
                  link: Optional[Url],
                  comments: Optional[str],
                  pubDate: datetime,
                  guid: Optional[str],
                  description: Optional[str],
                  content_raw: Optional[str]) -> Item:
    return Item(title=title, link=link, comments=comments, pubDate=pubDate, guid=guid, description=description, content_raw=content_raw)


def get_parser(url: str) -> BaseParser:
  if 'nablog' in url or 'naughtyblog' in url:
    from .nablog import Parser
    return Parser(url)
