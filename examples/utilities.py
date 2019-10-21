import os
from urllib.request import urlopen
from urllib.error import HTTPError
import re
from bs4 import BeautifulSoup
import folium
from folium.plugins import MarkerCluster
import geocoder
import random
from django.conf import settings
from django.core.cache import cache

# You can check how it work on web site - https://boatsproject-eu.herokuapp.com/boats/
# Choose a boat.
# Click 'Open list of BLOCKET announcements on a separate page'.
# Click 'Show all on map' yellow button upper right corner.


def coords(city_name, country=', Sweden'):
    """
    Returns coordinates according the city name and country. Sweden default
    Here we trying to get geo coordinates of a city by it's name. Sweden is default as project
    from where this code is taken is targeting Swedish second hand sail-boat market.
    Then we store coords in Redis and when we need to get coords for the same place next time -
    we get it from Redis without requesting OSM(open street maps) geo data provider again.
    Most likely that place will not change its coords often enough to not keep it coords in cache.
    """
    cache_key = 'coordinates+%s%s' % (city_name, country)
    coords_from_cache = cache.get(cache_key)
    if not coords_from_cache:
        coord_from_osm = geocoder.osm(city_name + country).latlng
        if coord_from_osm:
            cache.set(cache_key, coord_from_osm, 60*60*24*30)
        return coord_from_osm
    else:
        return coords_from_cache


def spider(name):
    """
    This web spider gets data of the boat from  www.blocket.se and returns information about boat
    ( by it's name)  which are on display there. From all data here in this example we need
    only last one which is dictionary of {boat_name: city name}, like for example
    {'Najad': 'Stockholm'}. Might have few elements in it, quite often 20+
    ---cities_dict---
    No point cache this function as we always need fresh information form a web site...
    """
    address = "https://www.blocket.se/hela_sverige?q=%s&cg=1060&w=3&st=s&ps=&pe=&c=1062&ca=11&is=1&l=0&md=li" % name.replace(" ", "+").replace("-", "+")
    try:
        html = urlopen(address)
    except HTTPError:
        return {"HTTPError": "www.blocket.se hasn't accepted the search or has other sort of"
                             " HTTP troubles "}, None, None
    else:
        bsObj = BeautifulSoup(html.read(), features="lxml")

        raw_search = bsObj.findAll("a", {"tabindex": "50"})
        url_dict = {}
        for unit in raw_search:

            final_search = bsObj.find("a", {"tabindex": "50", "title": unit.get_text()})
            if final_search:

                url = (re.findall(r"http(?:s)?://\S+", str(final_search)))
                title = final_search.get_text()
                url_dict.update({title: url[0][: -1]})
            else:
                url = (re.findall(r"http(?:s)?://\S+", str(unit)))
                title = unit.get_text()
                if not title.isspace():
                    url_dict.update({title: url[0][: -1]})

        prices = bsObj.findAll("p", {"itemprop": "price"})
        pricelist = []
        for price in prices:

            digits = ''.join(filter(lambda x: x.isdigit(), price.get_text()))
            pricelist.append(int(digits)) if digits else pricelist.append(0)

        places = bsObj.find_all("header", {"itemprop": "itemOffered"})
        cities_dict = {}
        for place, boat in zip(places, url_dict.keys()):

            text = place.get_text().strip().split()[-1]
            cities_dict.update({boat: text})

        if pricelist and url_dict:
            result_list, result_dict, = zip(*sorted(zip(pricelist, url_dict.items())))
            result_list, result_dict = list(result_list), dict(result_dict)
        else:
            result_list = result_dict = {}

        if 0 in result_list:
            for cnt, price in enumerate(result_list):
                if price == 0:
                    result_list[cnt] = None
        return result_dict, result_list, cities_dict  # we take cities_dict from here


def map_folium(places: dict, name_of_the_boat: str):
    """
    This function creates map and puts geo tags on it with boats names.
    At the end of the function we put in cache for a week  incoming data of the function in order
    to not run this function again if we have same incoming data next time. If quantity of the
    boats, and their geo coords haven't changed we can reuse same map we have on disc already.
    """
    map = folium.Map(location=[59.20, 18.04], zoom_start=7)
    marker_cluster = MarkerCluster().add_to(map)
    known_coordinates = {}
    for boat_name, place in places.items():

            if list(known_coordinates.keys()).count(place) == 1:
                location = known_coordinates.get(place)
                if location:
                    location = [c + random.uniform(- 0.05, 0.05) for c in location]
            else:

                if place not in known_coordinates.keys():
                    langalt = coords(place)
                    known_coordinates.update({place: langalt})
                location = known_coordinates.get(place)
            try:
                folium.Marker(location=location, radius=1, popup=" %s, location - %s " %
                (boat_name, place), icon=folium.Icon(color='gray')).add_to(marker_cluster)
            except TypeError:
                pass
    if not os.path.exists(os.path.join(settings.BASE_DIR, "templates", "maps")):
        os.mkdir(os.path.join(settings.BASE_DIR, "templates", "maps"))
    map.save(os.path.join(settings.BASE_DIR, "templates", "maps",  name_of_the_boat + ".html"))

    cache.set("map_folium+%s" % name_of_the_boat, places, 60 * 60 * 24 * 7)


def custom_lru_cache(places, name_of_the_boat):
    """
    Here we check if we have stored in cache geo coords incoming data of the function
    'map_folium' from above and if so, and data are the same - we reuse map we have on disc
    already. If not -we create map from scratch (time consuming).
    """
    local_path = os.path.join(settings.BASE_DIR, "templates", "maps", name_of_the_boat +".html")
    arguments = cache.get("map_folium+%s" % name_of_the_boat)
    if not arguments or (arguments != places) or not os.path.exists(local_path):
        map_folium(places, name_of_the_boat)
    return None
