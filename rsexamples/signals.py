from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import BoatModel, Article, Comment
from django.shortcuts import reverse
from fancy_cache.memory import find_urls
from django.urls import NoReverseMatch


@receiver([post_save, post_delete], sender=BoatModel)
def invalidate_by_BoatModel(sender, instance, **kwargs):
    # invalidates cache for BoatListView
    cache_key = "BoatListView"
    cache.delete(cache_key)
    # invalidates cache for evaluation queryset in template caching example when boat data is
    # changed
    cache_key_2 = "boat_detail_view"
    cache.delete(cache_key_2, version=instance.pk)

    # invalidates cache for BoatListView_2
    try:
        url = reverse('boats_version_2')
        list(find_urls([url, ], purge=True))
    except NoReverseMatch:
        pass


@receiver([post_save, post_delete], sender=Article)
def invalidate_by_Article(sender, instance, **kwargs):
    # invalidates cache for evaluation queryset in template caching example when article data is
    # changed
    cache_key_2 = "boat_detail_view"
    cache.delete(cache_key_2, version=instance.foreignkey_to_boat_id)


@receiver([post_save, post_delete], sender=Comment)
def invalidate_by_Comment(sender, instance, **kwargs):
    # invalidates cache for evaluation queryset in template caching example when comment data is
    # changed
    cache_key_2 = "boat_detail_view"
    cache.delete(cache_key_2, version=instance.foreignkey_to_boat_id)
