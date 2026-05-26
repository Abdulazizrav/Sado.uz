from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")
    icon = models.CharField(max_length=10, blank=True, verbose_name="Ikonka (Emoji)")
    keywords = models.TextField(verbose_name="Kalit so'zlar")

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

    def __str__(self):
        return f"{self.icon} {self.name}"


class Article(models.Model):
    title = models.TextField(blank=True, null=True, verbose_name="Sarlavha")
    content = models.TextField(blank=True, null=True, verbose_name="Matn")
    url = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True, verbose_name="Manba")
    published_date = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sanasi")
    is_summary = models.BooleanField(default=False)
    owner_id = models.IntegerField(blank=True, null=True)
    last_summarize_attempt = models.DateTimeField(blank=True, null=True)
    summarize_failed_count = models.IntegerField(default=0)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Kategoriyasi"
    )

    class Meta:
        managed = False
        db_table = 'Article'
        verbose_name = "Yangilik"
        verbose_name_plural = "Barcha Yangiliklar"

    def __str__(self):
        return self.title or "Sarlavhasiz"


class ArticleImage(models.Model):
    image = models.BinaryField(verbose_name="Rasm")
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE,
        db_column='article_id', related_name='images'
    )

    class Meta:
        managed = False
        db_table = 'apps_articleimage'
        verbose_name = "Maqola rasmi"
        verbose_name_plural = "Maqola rasmlari"

    def __str__(self):
        return f"Image for Article #{self.article_id}"


class Summary(models.Model):
    """
    Real DB structure:
      id           bigint PK auto_increment
      summary_text longtext
      created_date datetime
      article_id   bigint FK -> Article
    """
    summary_text = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(null=True, blank=True)
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE,
        null=True, blank=True, related_name='summaries',
        db_column='article_id'
    )

    class Meta:
        managed = False
        db_table = 'Summary'

    def __str__(self):
        return str(self.article) if self.article else f"Summary #{self.pk}"


class TelegramChannel(models.Model):
    """Read-only mirror of NewsCrawler's TelegramChannel table."""
    name = models.CharField(max_length=100)
    channel_id = models.BigIntegerField(default=0)
    is_active = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'TelegramChannel'

    def __str__(self):
        return self.name


class TelegramDelivery(models.Model):
    """
    Read-only mirror of NewsCrawler's TelegramDelivery table.
    status='sent' means successfully delivered to Telegram.
    """
    summary = models.ForeignKey(
        Summary, on_delete=models.CASCADE,
        related_name='deliveries', db_column='summary_id'
    )
    telegram_channel = models.ForeignKey(
        TelegramChannel, on_delete=models.CASCADE,
        related_name='deliveries'
    )
    message_id = models.PositiveIntegerField(default=0)
    sent_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=255)
    cost_charged = models.DecimalField(decimal_places=2, max_digits=12)

    class Meta:
        managed = False
        db_table = 'TelegramDelivery'

    def __str__(self):
        return f"Delivery -> {self.telegram_channel.name}"
