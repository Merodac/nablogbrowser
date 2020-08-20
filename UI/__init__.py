from typing import cast
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, ObjectProperty
from kivy.graphics import Color, Rectangle
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.app import App
from rss_parser import get_parser, Item
from rss_parser.nablog import NaBlogItem


class MainApp(App):
  def build(self):
    root = self.root

  def on_pause(self):
    return True


class MyAsyncImage(AsyncImage):
  state = StringProperty("Initialized.")

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.state = "Loading."

  def on_load(self, *args):
    self.state = "Loaded."


class RootLayout(BoxLayout):
  def start_load_button(self):
    self.ids.status_label.text = "Pressed!"
    parser = get_parser('https://www.naughtyblog.org/category/clips/feed/')
    result = parser.parse()
    first_item = cast(NaBlogItem, result.items[0])

    self.ids.async_image.source = str(first_item.title_picture_thumburl)

