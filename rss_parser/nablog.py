from time import struct_time

import feedparser
from . import Item, Url, Channel
from . import BaseParser
from typing import Union, Any, List, Optional, cast
from datetime import datetime
from pyquery import PyQuery
import re


class NaBlogItem(Item):
  title_picture_url: Url
  release_date: str
  preview_thumburl: Url
  preview_linkurl: Url
  size: str
  duration: str
  video: str
  audio: str
  downloadlinks: List[Url]

  def __init__(self,
               title: str,
               link: Optional[Url],
               thumb_url: Optional[Url],
               comments: Optional[str],
               pubDate: datetime,
               guid: Optional[str],
               description: Optional[str],
               content_raw: Optional[str],
               link_picture_url: Url,
               release_date: str,
               preview_thumburl: Url,
               preview_linkurl: Url,
               size: str,
               duration: str,
               video: str,
               audio: str,
               downloadlinks: List[Url]
               ):
    super().__init__(title, link, thumb_url, comments, pubDate, guid, description, content_raw)
    self.title_picture_url = link_picture_url
    self.release_date = release_date
    self.preview_thumburl = preview_thumburl
    self.preview_linkurl = preview_linkurl
    self.size = size
    self.duration = duration
    self.video = video
    self.audio = audio
    self.downloadlinks = downloadlinks


class Parser(BaseParser):
  def __init__(self, remote_url: str):
    super().__init__(remote_url=remote_url)

  def get_title(self) -> str:
    return "NABlog"

  def get_updated_parsed(self, feed: feedparser.FeedParserDict) -> struct_time:
    return feed['updated_parsed']

  def get_link(self, feed: feedparser.FeedParserDict) -> Url:
    return Url(feed['href'])

  def get_channel(self, feed: feedparser.FeedParserDict) -> feedparser.FeedParserDict:
    return feed['channel']

  def get_description(self, feed: feedparser.FeedParserDict) -> str:
    return feed['description']

  def get_title_field(self, feed: feedparser.FeedParserDict) -> str:
    return feed['title']

  def get_item_title(self, parserdict: feedparser.FeedParserDict) -> str:
    return parserdict['title']

  def get_item_link(self, parserdict: feedparser.FeedParserDict) -> Url:
    return Url(parserdict['link'])

  def get_item_comments(self, parserdict: feedparser.FeedParserDict) -> str:
    return parserdict['comments']

  def get_item_updated(self, parserdict: feedparser.FeedParserDict) -> struct_time:
    return parserdict['published_parsed']

  def get_item_guid(self, parserdict: feedparser.FeedParserDict) -> str:
    return parserdict['guid']

  def get_item_description(self, parserdict: feedparser.FeedParserDict) -> str:
    return parserdict['description']

  def get_item_content_raw(self, parserdict: feedparser.FeedParserDict) -> str:
    return parserdict['content'][0].value

  def create_item(self,
                  title: str,
                  link: Optional[Url],
                  comments: Optional[str],
                  pubDate: datetime,
                  guid: Optional[str],
                  description: Optional[str],
                  content_raw: Optional[str]) -> Item:

    pq = PyQuery(content_raw)
    thumb_url = self.get_title_picture_thumburl(pq)
    title_picture_url = self.get_title_picture_url(pq)
    release_date = self.get_release_date(pq)
    preview_linkurl, preview_thumburl = self.get_preview_urls(pq)
    size, duration, video, audio = self.get_video_info(pq)
    downloadlinks = self.get_downloadlinks(pq)

    return NaBlogItem(title=title,
                      link=link,
                      thumb_url=thumb_url,
                      comments=comments,
                      pubDate=pubDate,
                      guid=guid,
                      description=description,
                      content_raw=content_raw,
                      link_picture_url=title_picture_url,
                      release_date=release_date,
                      preview_thumburl=preview_thumburl,
                      preview_linkurl=preview_linkurl,
                      size=size,
                      duration=duration,
                      video=video,
                      audio=audio,
                      downloadlinks=downloadlinks)

  def get_title_picture_url(self, pq) -> Url:
    return Url(pq('a')[0].attrib['href'])

  def get_title_picture_thumburl(self, pq) -> Url:
    return Url(pq('a > img')[0].attrib['src'])

  def get_release_date(self, pq) -> str:
    return [em.text for em in pq('em') if 'Released' in em.text][0]  # TODO cut "Release: and only leave the date"

  def get_preview_urls(self, pq) -> [Url, Url]:
    content = pq('p')
    for paragraph in content.items():
      header = paragraph.find('strong')
      if not header.text() == 'Preview:':
        continue
      link = paragraph.find('a').attr('href')
      thumb = paragraph.find('img').attr('src')
      return Url(link), Url(thumb)

  def get_video_info(self, pq) -> [str, str, str, str]:
    size_content = pq('strong:contains(Size\:)')
    duration_content = pq('strong:contains(Duration\:)')
    video_content = pq('strong:contains(Video\:)')
    audio_content = pq('strong:contains(Audio\:)')

    if not (size_content.parent() == duration_content.parent() == video_content.parent() == audio_content.parent()):
      raise RuntimeError("Size, Duration, Video and Audio not in same parent.")

    parent_html = size_content.parent().outer_html()
    size_html = size_content.outer_html()
    duration_html = duration_content.outer_html()
    video_html = video_content.outer_html()
    audio_html = audio_content.outer_html()

    pattern = ".*" + re.escape(size_html) + "(.*)" + re.escape(duration_html) + "(.*)" + re.escape(
      video_html) + "(.*)" + re.escape(audio_html) + "(.*)"

    match = re.search(pattern, parent_html)
    size = match.group(1)
    duration = match.group(2)
    video = match.group(3)
    audio = match.group(4)

    closing_tag = '</' + size_content.parent()[0].tag + ">"

    size = _clean_video_info(size, closing_tag)
    duration = _clean_video_info(duration, closing_tag)
    video = _clean_video_info(video, closing_tag)
    audio = _clean_video_info(audio, closing_tag)

    return size, duration, video, audio

  def get_downloadlinks(self, pq) -> List[Url]:
    return []


def _clean_video_info(str_input: str, closing_tag) -> str:
  closing_tag_index = str_input.find(closing_tag)
  if closing_tag_index > -1:
    str_input = str_input[:closing_tag_index]
  pipe_index = str_input.find('|')
  if pipe_index > -1:
    str_input = str_input[:pipe_index]
  return str_input.strip()
