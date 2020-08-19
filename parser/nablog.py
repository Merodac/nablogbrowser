from typing import Union, Any, List, Optional, cast


class url:
  target: str

  def __init__(self, target: str):
    self.target = target


class item:
  title: str
  link: Optional[url]
  comments: Optional[str]
  pubDate_raw: str
  guid: Optional[str]
  description: Optional[str]
  content_raw: Optional[str]
  categories: List[str]

  def __init__(self,
               title: str,
               link: Optional[url],
               comments: Optional[str],
               pubDate_raw: str,
               guid: Optional[str],
               description: Optional[str],
               content_raw: Optional[str]):
    self.title = title
    self.link = link
    self.comments = comments
    self.pubDate_raw = pubDate_raw
    self.categories = []
    self.guid = guid
    self.description = description
    self.content_raw = content_raw


class channel:
  title: str
  atomlink: url
  link: url
  description: str
  site: Optional[str]
  items: List[item]

  def __init__(self, title: str, atomlink: url, link: url, description: str, site: Optional[str]):
    self.title = title
    self.atomlink = atomlink
    self.link = link
    self.description = description
    self.site = site
    self.items = []

