from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")
    icon = models.CharField(max_length=10, blank=True, verbose_name="Ikonka (Emoji)")
    keywords = models.TextField(help_text="Vergul bilan ajratilgan kalit so'zlar (masalan: siyosat, jahon). Avtomatik ulash uchun ishlatiladi.", verbose_name="Kalit so'zlar")

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

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kategoriyasi", help_text="Ushbu yangilik qaysi kategoriyaga tegishli ekanligini qo'lda belgilash")

    class Meta:
        managed = False
        db_table = 'Article'
        verbose_name = "Yangilik"
        verbose_name_plural = "Barcha Yangiliklar"

    def __str__(self):
        return self.title or "Sarlavhasiz"

class Summary(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE, primary_key=True, related_name='summary_rel')
    summary_text = models.TextField()

    class Meta:
        managed = False
        db_table = 'Summary'
