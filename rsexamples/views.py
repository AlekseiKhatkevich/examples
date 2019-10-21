from examples.utilities import custom_lru_cache, spider
import os

from django.views.decorators.gzip import gzip_page
from django.http import FileResponse
from django.conf import settings
from django.views.generic.base import TemplateView


@gzip_page
def map_show(request, name_of_the_boat):
    places = spider(name_of_the_boat)[-1]
    custom_lru_cache(places, name_of_the_boat)
    local_path = os.path.join(settings.BASE_DIR, "templates", "maps",  name_of_the_boat + ".html")
    return FileResponse(open(local_path, "rb"), content_type="text/html")


class IndexView(TemplateView):
    template_name = "index.html"
