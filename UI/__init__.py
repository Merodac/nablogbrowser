from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty
from kivy.graphics import Color, Rectangle
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.app import App


class MainApp(App):
  def build(self):
    root = self.root

  def on_pause(self):
    return True


