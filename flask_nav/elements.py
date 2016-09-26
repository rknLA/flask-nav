from flask import url_for, request, current_app
from markupsafe import Markup

from . import get_renderer


class NavigationItem(object):
    """Base for all items in a Navigation.

    Every item inside a navigational view should derive from this class.
    """

    #: Indicates whether or not the item represents the currently active route
    active = False

    def render(self, renderer=None, **kwargs):
        """Render the navigational item using a renderer.

        :param renderer: An object implementing the :class:`~.Renderer`
                         interface.
        :return: A markupsafe string with the rendered result.
        """
        return Markup(get_renderer(current_app, renderer)(**kwargs).visit(
            self))


class Link(NavigationItem):
    """An item that contains a link to a destination and a title."""

    def __init__(self, text, dest):
        self.text = text
        self.dest = dest

    def get_url(self):
        return self.dest


class RawTag(NavigationItem):
    """An item usually expressed by a single HTML tag.

    :param title: The text inside the tag.
    :param attribs: Attributes on the item.
    """

    def __init__(self, content, **attribs):
        self.content = content
        self.attribs = attribs


class View(Link):
    """Application-internal link.

    The ``endpoint``, ``*args`` and ``**kwargs`` are passed on to
    :func:`~flask.url_for` to get the link.

    :param text: The text for the link.
    :param endpoint: The name of the view.
    :param args: Extra arguments for :func:`~flask.url_for`
    :param kwargs: Extra keyword arguments for :func:`~flask.url_for`
    """

    def __init__(self, text, endpoint, *args, **kwargs):
        self.text = text
        self.endpoint = endpoint
        self.url_for_args = args
        self.url_for_kwargs = kwargs

    def get_url(self):
        """Return url for this item.

        :return: A string with a link.
        """
        return url_for(self.endpoint, *self.url_for_args,
                       **self.url_for_kwargs)

    @property
    def active(self):
        # this is a better check than checking for request.endpoint
        # because it takes arguments to the view into account
        return request.path == self.get_url()


class ImageView(View):
    """A View link with an image instead of text.

    The ``endpoint``, ``*args`` and ``**kwargs`` are passed on to
    :func:`~flask.url_for` to get the link.

    :param img_info: A dictionary of parameters for the image tag.  Valid
                     keys include `src`, `alt`, `width`, `height`, `class`,
                     and `id`.
    :param endpoint: The name of the view.
    :param args: Extra arguments for :func:`~flask.url_for`
    :param kwargs: Extra keyword arguments for :func:`~flask.url_for`
    """

    def __init__(self, img_info, endpoint, *args, **kwargs):
        self.text = None
        self.img_src = img_info.get("src", None)
        self.img_alt = img_info.get("alt", None)
        self.img_width = img_info.get("width", None)
        self.img_height = img_info.get("height", None)
        self.img_class = img_info.get("class", None)
        self.img_id = img_info.get("id", None)
        self.endpoint = endpoint
        self.url_for_args = args
        self.url_for_kwargs = kwargs

    def get_img_tag(self):
      """Return the image tag for this item.

      :return: A dominate image tag
      """
      img = tags.img(src=self.img_sr,
          alt=self.img_alt,
          _class=self.img_class,
          _id=self.img_id)
      return img



class Separator(NavigationItem):
    """Separator.

    A seperator inside the main navigational menu or a Subgroup. Not all
    renderers render these (or sometimes only inside Subgroups).
    """
    pass


class Subgroup(NavigationItem):
    """Nested substructure.

    Usually used to express a submenu.

    :param title: The title to display (i.e. when using dropdown-menus, this
                  text will be on the button).
    :param items: Any number of :class:`.NavigationItem` instances  that
                  make up the navigation element.
    """

    def __init__(self, title, *items):
        self.title = title
        self.items = list(items)

    @property
    def active(self):
        return any(item.active for item in self.items)


class Text(NavigationItem):
    """Label text.

    Not a ``<label>`` text, but a text label nonetheless. Precise
    representation is up to the renderer, but most likely something like
    ``<span>``, ``<div>`` or similar.
    """

    def __init__(self, text):
        self.text = text


class Navbar(Subgroup):
    """Top level navbar."""
    pass
