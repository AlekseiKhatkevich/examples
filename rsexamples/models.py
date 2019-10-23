from django.db import models


class BoatModel(models.Model):

    SLOOP = "SL"
    KETCH = "KE"
    YAWL = "YA"
    CAT_KETCH = "CK"
    CUTTER = "CU"

    CHOICES = (
        (None, "Please choose  the rigging type"),
        (SLOOP, "Sloop"),
        (KETCH, "Ketch"),
        (YAWL, "Yawl"),
        (CAT_KETCH, "Cat Ketch"),
        (CUTTER, "Cutter")
    )

    boat_name = models.CharField(max_length=20, unique=True, db_index=True,
                                 verbose_name="Boat model",
                                 help_text="Please input boat model")

    boat_length = models.FloatField(null=False, blank=False, verbose_name="Boat water-line "
                                "length", help_text="Please input boat water-line length",)

    boat_description = models.TextField(blank=True, verbose_name="Boat description",
                                        help_text="Please describe the boat", )

    boat_mast_type = models.CharField(max_length=10, choices=CHOICES,
                                      verbose_name="Boat rigging type",
                                      help_text="Please input boat rigging type")

    boat_price = models.PositiveIntegerField(verbose_name="price of the boat",
                                                  help_text="Please input boat price", )

    boat_sailboatdata_link = models.URLField(max_length=100, blank=True,
                                             verbose_name="URL to Sailboatdata",
                                             help_text="Please type in URL to Sailboatdata "
                                                       "page for this boat")

    boat_keel_type = models.CharField(max_length=50, verbose_name="Boat keel type",
                                      help_text="Please specify boat's keel type")

    boat_publish_date = models.DateTimeField(auto_now_add=True)

    first_year = models.PositiveSmallIntegerField(blank=True, null=True,
                                    verbose_name="first manufacturing year of the model")
    last_year = models.PositiveSmallIntegerField(blank=True, null=True,
                                    verbose_name="Last manufacturing year of the model")
    change_date = models.DateTimeField(db_index=True, editable=False, auto_now=True)

    class Meta:
        verbose_name = "Boats primary data"
        verbose_name_plural = "Boats primary data"
        ordering = ["-boat_publish_date"]
        models.CheckConstraint(check=models.Q(first_year__gte=1950), name='first_year__gte=1950')

    def __str__(self):
        return self.boat_name


class ArticleManager(models.Manager):
    """Менеджер прямой связи . Показываем только не удаленные статьи"""
    def get_queryset(self):
        return models.Manager.get_queryset(self).exclude(show=False)


class Article(models.Model):

    foreignkey_to_boat = models.ForeignKey(BoatModel, on_delete=models.CASCADE,                                  verbose_name="Parent boat for article", help_text="Please choose the boat",
                                           blank=True, null=True)
    title = models.CharField(max_length=50, verbose_name="Article title",
                             help_text="Please add a title")
    content = models.TextField(verbose_name='Description of the article',
                               blank=True, help_text="Please briefly describe the article")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Published"
                                                                                     " at")
    url_to_article = models.URLField(max_length=100, unique=True, verbose_name="URL to the "
                                        "article",help_text="Please insert URL of the article")
    show = models.BooleanField(default=True, blank=False, null=False, verbose_name="deleted mark",
                               help_text='Marked articles are shown everywhere, unmarked'
                                         'considered as deleted ones')
    change_date = models.DateTimeField(blank=True, null=True, auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ["-created_at"]


class Comment(models.Model):
    foreignkey_to_article = models.ForeignKey(Article, blank=True, null=True,
                                on_delete=models.CASCADE, verbose_name="Article",                                                       help_text='Please choose the article to comment on')
    foreignkey_to_boat = models.ForeignKey(BoatModel, blank=True, null=True,
                                           on_delete=models.CASCADE, verbose_name="Boat",
                                           help_text="Please choose the boat to comment on")
    content = models.TextField(verbose_name="Comment text", help_text="Please type in comment "
                                                                      "here")
    is_active = models.BooleanField(default=True, db_index=True,
                                    verbose_name="Published", help_text="publish?")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Publish "
                                                                                     "date")
    change_date = models.DateTimeField(db_index=True, editable=False, auto_now=True)

    def __str__(self):
        return "%s - %s" % ((self.foreignkey_to_article.title if self.foreignkey_to_article
                             else self.foreignkey_to_boat.boat_name), self.content[: 25])

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["-created_at", ]

