from examples.utilities import custom_lru_cache, spider
import os
from django.shortcuts import render
from django.views.decorators.gzip import gzip_page
from django.http import FileResponse
from django.conf import settings
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.core.cache import cache
from .models import BoatModel, Article, Comment
from django.utils.decorators import method_decorator
from django.core.cache import cache
from fancy_cache import cache_page
from django.core.cache.utils import make_template_fragment_key


@gzip_page
def map_show(request, name_of_the_boat):
    """View for showing map with boats"""
    places = spider(name_of_the_boat)[-1]
    custom_lru_cache(places, name_of_the_boat)
    local_path = os.path.join(settings.BASE_DIR, "templates", "maps",  name_of_the_boat + ".html")
    return FileResponse(open(local_path, "rb"), content_type="text/html")


class IndexView(TemplateView):
    """View for index html"""
    template_name = "index.html"


def vary_on_database(request):
    """
    This function construct unique cache key prefix for view bellow(BoatListView).
    it takes timestamp of last modified object from DB table related to boats, count of all
     objects in this DB table , and information from REQUEST object whether or not current user
      is authenticated, and constructs
      unique string from it to be used as a key_prefix (key in cache). Then this key_prefix is
       used in  BoatListView ( as a cache key) in order co cache RESPONSE object which this VIEW
        returns. When changes in DB occurs, we have different timestamp or count or both, so
        that key_prefix we have is different to old one and as VIEW cant find it in cache - it
         forced to pull data from dB and retrieves updated data as a result.

    As a next step we store in cache data_obj, that is unique string of DB table state in
     order to not retrieve it (timestamp + count) from DB each and every time .
     cache_key = "BoatListView"
     In order to invalidate this cache we  use Django signals in rsexamples/signals.py which
      would delete this cache_key when data gets created/updated or deleted.
    """
    cache_key = "BoatListView"
    data_obj = cache.get(cache_key)
    if not data_obj:
        timestamp = BoatModel.objects.all().values_list("change_date", flat=True).latest(
                "change_date").timestamp()
        boats_count = BoatModel.objects.all().count()
        data_obj = "%s+%s" % (timestamp, boats_count)
        cache.set(cache_key, data_obj, 60*60*24)
    return "BoatListView+%s+%s" % (str(data_obj), str(request.user.is_authenticated))


@method_decorator(cache_page(60*60*24, key_prefix=vary_on_database), name="dispatch")
class BoatListView(ListView):
    """View shows list of a boats."""
    model = BoatModel
    template_name = "boats.html"
    paginate_by = 10


@method_decorator(cache_page(60*60*24), name="dispatch")
class BoatListView_2(ListView):
    """
    Similar to view above but uses simple cache invalidation in signals rsexamples/signals.py".
     Its ok for our example but if you have ,for example, complex SQL or any other code which
     causes delays , it would invalidate whole page and you would need to get all data and
     calculations again. It uses URL as cache identification.
    In this cases you might want to use semi-custom method with key_prefix where you can store
    different functions in cache separately and invalidate only one of them and use rest from
     cache.
    """
    model = BoatModel
    template_name = "boats.html"
    paginate_by = 10


def boat_detail_view(request, pk):
    """
    This views displays page with 3 objects: boat, article on boat and comment on boat.
    In this case we can use template cache in order to divide page in 3 sections and cache them
     separately in order to have possibility to invalidate only 1 section when DB changes
      occurs and retrieve other sections from cache.
      Cache itself defined in templates/boat_detail.html. Please have a look there.

    Next step: We need to invalidate this cache when changes in DB occurs in 1 ore more models
    (boats, articles or comment). For doing this we ,as in the example above ,construct unique
     cache object(this is not a key) and pass these objects(one for each model) into template
     context. If data changed in DB ,as a result we have different cache object, and Django
     knows that fresh data needed to be pulled from DB.

    Next step: In order to not construct this cache objects every time we can store it in cache
     and retrieve it when needed( every load of the page). To find out when this cache is
     stale, we use django signals rsexamples/signals.py to invalidate it when changes in one or
      more then one model has happened.

    """
    current_boat = BoatModel.objects.prefetch_related("article_set", "comment_set",).get(pk=pk)
    comments = current_boat.comment_set.all()
    articles = current_boat.article_set.all()

    data_obj = cache.get("boat_detail_view", version=current_boat.pk)  # get cache object from cache
    if not data_obj:  # if not, we run DB queries to check DB state
        eq_current_boat = BoatModel.objects.filter(pk=pk).\
            values_list(
            "change_date",
            flat=True).latest("change_date").timestamp()

        eq_articles = (articles.values_list("change_date", flat=True).latest(
            "change_date").timestamp() if articles else None, articles.count())

        eq_comments = (comments.values_list("change_date", flat=True).latest(
            "change_date").timestamp() if comments else None, comments.count())

        EQ = {
              "eq_current_boat": eq_current_boat,
              "eq_articles": eq_articles,
              "eq_comments": eq_comments
              }  # unique DB state object
        cache.set("boat_detail_view", EQ, 60 * 60 * 24, version=current_boat.pk)  # put result in cache
    else:
        EQ = data_obj  # use cached unique object if we have it in cache

    context = {"current_boat": current_boat,
               "comments": comments,
               "articles": articles,
               "EQ": EQ}

    return render(request, "boat_detail.html", context)
