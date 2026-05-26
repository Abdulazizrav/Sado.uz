from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse, Http404
import json

from news.models import Category, Article, TelegramChannel, TelegramDelivery, ArticleImage

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
            'O\u2019zbek tiliga tarjima',
            'Oddiy sun\'iy intelekt',
            'Keyword filter (kalit so\u2019zlar)',
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
        'target_audience': 'O\u2019rta bizneslar, media sahifalar va SMM jamoalar uchun.',
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
            'White-label (o\u2019z brendingiz bilan)',
            'Premium ko\'maklashish'
        ],
        'best_for': 'Katta media va avtomatlashtirilgan tizimlar'
    },
]


def fetch_delivered_news(request):
    """
    Returns news articles that were successfully delivered to Telegram channels.
    Only status='sent' records are shown (actual DB value).
    Supports optional ?channel_id=<id> filter and ?offset=<n> for pagination.
    """
    channel_id_filter = request.GET.get('channel_id', '')
    offset = int(request.GET.get('offset', 0))
    limit = 12

    try:
        qs = TelegramDelivery.objects.filter(
            status='sent'
        ).select_related(
            'summary__article',
            'telegram_channel'
        ).order_by('-sent_date', '-id')

        if channel_id_filter:
            qs = qs.filter(telegram_channel__channel_id=channel_id_filter)

        total = qs.count()
        deliveries = list(qs[offset: offset + limit])

        # Batch check images to prevent N+1
        article_ids = [
            d.summary.article.id 
            for d in deliveries 
            if d.summary and getattr(d.summary, 'article', None)
        ]
        
        articles_with_images = set(
            ArticleImage.objects.filter(article_id__in=article_ids).values_list('article_id', flat=True)
        )

        news_data = []
        for delivery in deliveries:
            summary = delivery.summary
            article = getattr(summary, 'article', None)
            channel = delivery.telegram_channel

            has_image = article.id in articles_with_images if article else False
            image_url = f"/api/news/image/{article.id}/" if has_image else None

            news_data.append({
                'id': delivery.id,
                'summary_text': summary.summary_text if summary else '',
                'title': article.title if article else '',
                'url': article.url if article else '#',
                'source': article.source if article else '',
                'published_date': str(delivery.sent_date) if delivery.sent_date else '',
                'channel_name': channel.name if channel else '',
                'channel_id': str(channel.channel_id) if channel else '',
                'message_id': delivery.message_id,
                'has_image': has_image,
                'image_url': image_url,
            })

        return JsonResponse({
            'status': 'ok',
            'news': news_data,
            'has_more': (offset + limit) < total,
            'total': total,
        })

    except Exception as e:
        import traceback
        return JsonResponse({'status': 'error', 'message': str(e), 'trace': traceback.format_exc()}, status=500)


def serve_article_image(request, article_id):
    """
    Serves the raw JPEG/PNG image binary data stored in apps_articleimage.
    """
    try:
        img_record = ArticleImage.objects.filter(article_id=article_id).first()
        if not img_record or not img_record.image:
            raise Http404("Image not found")
        
        response = HttpResponse(img_record.image, content_type="image/jpeg")
        response['Cache-Control'] = 'public, max-age=86400'  # Cache for 1 day
        return response
    except Exception as e:
        raise Http404("Image not found")


def fetch_channels(request):
    """Returns the list of Telegram channels that have sent news."""
    try:
        channel_ids = TelegramDelivery.objects.filter(
            status='sent'
        ).values_list('telegram_channel_id', flat=True).distinct()

        channels = TelegramChannel.objects.filter(id__in=channel_ids).values('id', 'name', 'channel_id')

        return JsonResponse({'status': 'ok', 'channels': list(channels)})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def home_view(request):
    from django.shortcuts import render
    return render(request, 'index.html')


def contact_submit(request):
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
    path('api/news/', fetch_delivered_news, name='fetch_delivered_news'),
    path('api/channels/', fetch_channels, name='fetch_channels'),
    path('api/news/image/<int:article_id>/', serve_article_image, name='serve_article_image'),
]