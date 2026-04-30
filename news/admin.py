from django.contrib import admin
from .models import Category, Article

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'keywords')
    search_fields = ('name', 'keywords')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'published_date', 'category')
    list_editable = ('category',)
    list_filter = ('category', 'source')
    search_fields = ('title', 'content')
    list_select_related = ('category',)
    readonly_fields = ('title', 'content', 'url', 'source', 'published_date', 'is_summary', 'owner_id', 'last_summarize_attempt', 'summarize_failed_count')
    
    def get_queryset(self, request):
        # Only show articles that have been summarized
        qs = super().get_queryset(request)
        return qs.filter(summary_rel__isnull=False)
    
    # Custom action to auto-link categories
    actions = ['auto_link_categories']

    @admin.action(description='Kalit so\'zlar bo\'yicha kategoriyaga avtomatik ulash')
    def auto_link_categories(self, request, queryset):
        categories = Category.objects.all()
        updated_count = 0
        for article in queryset:
            if not article.title:
                continue
            
            matched_category = None
            for cat in categories:
                if not cat.keywords:
                    continue
                keywords = [k.strip().lower() for k in cat.keywords.split(',') if k.strip()]
                title_lower = article.title.lower()
                
                for kw in keywords:
                    if kw in title_lower:
                        matched_category = cat
                        break
                if matched_category:
                    break
            
            if matched_category and article.category != matched_category:
                article.category = matched_category
                article.save(update_fields=['category'])
                updated_count += 1
                
        self.message_user(request, f"{updated_count} ta yangilik avtomatik kategoriyalarga ulandi.")
