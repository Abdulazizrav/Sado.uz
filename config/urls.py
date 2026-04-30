from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.http import JsonResponse
import json

from news.models import Category, Article

PRICING_PLANS = [
    {
        'name': 'Starter Plan',
        'price': "370,000",
        'period': "so'm / oy",
        'popular': False,
        'target_audience': 'Kichik Telegram kanallari, shaxsiy bloglar va boshlovchilar uchun.',
        'features': [
            '1 ta Telegram kanal',
            'Oyiga 150 ta xabar (~350 bayon)',
            'O‘zbek tiliga tarjima',
            'Oddiy sun\'iy intelekt',
            'Keyword filter (kalit so‘zlar)',
            'Avtomatik Telegramga joylash',
            'Standart qo\'llab quvvatlash'
        ],
        'best_for': 'Boshlovchilar va kichik kontent sahifalari'
    },
    {
        'name': 'Growth Plan',
        'price': "1,000,000",
        'period': "so'm / oy",
        'popular': True,
        'target_audience': 'O‘rta bizneslar, media sahifalar va SMM jamoalar uchun.',
        'features': [
            '3 ta Telegram kanal',
            'Oyiga 500 ta xabar (~1300 bayon)',
            'Mukammal kalit so\'z bo\'yicha filterlash',
            'Maxsus kategoriya tanlash',
            'Yaxshilangan sun\'iy intelekt',
            'Prioritet bo\'yicha ajratish',
            'Tezkor yordam'
        ],
        'best_for': 'Faol marketing va kontent yuritayotgan bizneslar'
    },
    {
        'name': 'Business Plan',
        'price': "2,500,000",
        'period': "so'm / oy",
        'popular': False,
        'target_audience': 'Agentliklar, katta media platformalar va professional jamoalar uchun.',
        'features': [
            '2000+ xabar (~8000 bayon)',
            'Cheksiz Telegram kanallar',
            'VIP moslashtirish',
            'Breaking news (tezkor yangiliklar)',
            'Tahliliy dashboard',
            'White-label (o‘z brendingiz bilan)',
            'Premium ko\'maklashish'
        ],
        'best_for': 'Katta media va avtomatlashtirilgan tizimlar'
    },
]

def fetch_news_api(request):
    category_name = request.GET.get('category', '')
    
    try:
        # Get the requested category
        category = Category.objects.filter(name=category_name).first()
        if not category:
            return JsonResponse({'status': 'ok', 'news': []})
        
        # Fetch the articles dynamically (extremely fast)
        # Only return articles that have an AI summary and are manually categorized
        articles = Article.objects.filter(category=category, summary_rel__isnull=False).select_related('summary_rel').order_by('-published_date')[:12]
        
        news_data = []
        for a in articles:
            summary = ''
            if hasattr(a, 'summary_rel') and a.summary_rel:
                summary = a.summary_rel.summary_text
                
            news_data.append({
                'id': a.id,
                'title': a.title,
                'url': a.url,
                'source': a.source,
                'published_date': a.published_date,
                'summary_text': summary
            })
            
        return JsonResponse({'status': 'ok', 'news': news_data})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def home_view(request):
    from django.shortcuts import render
    
    categories = Category.objects.all()
    template_categories = []
    for c in categories:
        template_categories.append({
            'icon': c.icon,
            'label': c.name,
            'value': c.name
        })
        
    return render(request, 'index.html', {
        'plans': PRICING_PLANS,
        'categories': template_categories,
    })


def contact_submit(request):
    from django.views.decorators.http import require_POST

    if request.method != 'POST':
        from django.http import HttpResponseNotAllowed
        return HttpResponseNotAllowed(['POST'])

    try:
        data = json.loads(request.body)
        return JsonResponse({'status': 'ok', 'message': 'Ariza qabul qilindi!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('oferta/', TemplateView.as_view(template_name='oferta.html'), name='oferta'),
    path('privacy/', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    path('contact/', contact_submit, name='contact_submit'),
    path('api/news/', fetch_news_api, name='fetch_news_api'),
]