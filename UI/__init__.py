from typing import cast, Optional
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.graphics import Color, Rectangle
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.app import App
from rss_parser import get_parser, Item
from kivy.uix.widget import Widget


def _get_root(widget: Optional[Widget]) -> Optional[Widget]:
  if not widget:
    return None

  local_parent = widget.parent
  if type(local_parent) is not Widget:
    return widget

  if local_parent is None:
    return widget
  return _get_root(local_parent)


def hide_widget(wid, dohide=True):
  if hasattr(wid, 'saved_attrs'):
    if not dohide:
      wid.height, wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
      del wid.saved_attrs
  elif dohide:
    wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
    wid.height, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, 0, True


class MainApp(App):
  def build(self):
    root = self.root

  def on_pause(self):
    return True


class MyItemLayout(BoxLayout):
  def __init__(self, item: Item, **kwargs):
    super().__init__(**kwargs)

    label = Label()


class MyAsyncImage(AsyncImage):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)

  def on_load(self, *args):
    _get_root(self).state = "Loaded."


class MyPage(GridLayout):
  def __init__(self, index, **kwargs):
    super().__init__(**kwargs)
    self.index = index
    self.rows = 5
    self.cols = 3

  def is_full(self):
    return len(self.children) >= self.rows * self.cols

  def set_background(self):
    self.canvas.clear()
    self.canvas.add(Color(0.8, 0.15, 0.15))
    filling_rectangle = Rectangle()
    filling_rectangle.pos = self.pos
    filling_rectangle.size = self.size
    self.canvas.add(filling_rectangle)


class MyCenterLayout(PageLayout):
  current_grid = ObjectProperty()
  index = NumericProperty(-1)
  index_str = StringProperty()

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self._current_grid_fillcount = 0
    self.current_grid = None
    self.swipe_threshold = 0.5

  def add_item(self, item: Item):
    if not self.current_grid:
      self.add_new_page()
    image = AsyncImage()
    image.source = str(item.thumb_url)
    self.current_grid.add_widget(image)

  def add_new_page(self) -> MyPage:
    self._current_grid_fillcount = 0
    self.index = self.index + 1
    self.current_grid = MyPage(self.index)
    self.add_widget(self.current_grid)
    self.current_grid.size = self.size
    self.current_grid.pos = self.pos
    self.current_grid.set_background()
    self.index_str = str(self.index)
    return self.current_grid


class RootLayout(BoxLayout):
  state = StringProperty("Initialized.")
  title = StringProperty("RSS Viewer")

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.parser = get_parser('https://www.reddit.com/r/EarthPorn/.rss')
    # self.parser = get_parser('https://www.naughtyblog.org/category/clips/feed/')
    self.title = self.parser.get_title()
    self.is_loaded = False

  def start_load_button_pressed(self):
    if self.is_loaded:
      self.cycle_pages()
      return
    self.is_loaded = True
    self.ids.status_label.text = "Pressed!"

    result = self.parser.parse()

    cast(MyCenterLayout, self.ids.center_page).clear_widgets()

    for parsed_item in result.items:
      if self.ids.center_page.current_grid is None or self.ids.center_page.current_grid.is_full():
        newPage = self.ids.center_page.add_new_page()
      self.ids.center_page.add_item(parsed_item)

  def cycle_pages(self):
    pages_layout = cast(MyCenterLayout, self.ids.center_page)
    pages_layout.page = 0
