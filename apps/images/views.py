from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import (
    EmptyPage,
    PageNotAnInteger,
    Paginator,
)
from django.http import (
    HttpResponse,
    JsonResponse,
)
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.http import require_POST

import redis
from apps.actions.utils import create_action

from .forms import ImageCreateForm
from .models import Image


# Соединить с redis.
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
)


@login_required
def image_create(request):
    if request.method == 'POST':
        # форма отправлена.
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # Данные в форме валидны.
            form.cleaned_data
            new_image = form.save(commit=False)
            # Назначить текущего пользователя элементу
            new_image.user = request.user
            new_image.save()
            create_action(request.user, 'bookmarked image', new_image)
            messages.success(
                request,
                'Image added successfully',
            )
            # Перенаправить к представлению детальной
            # информации о только что созданном элементе
            return redirect(new_image.get_absolute_url())
    else:
        # Скомпоновать форму с данными,
        # предоставленными букмарклетом методом GET
        form = ImageCreateForm(data=request.GET)
    return render(
        request, 'images/image/create.html',
        {
            'section': 'images',
            'form': form,
        },
    )


def image_detail(request, id, slug): # noqa
    image = get_object_or_404(Image, id=id, slug=slug)
    # Увеличить общее число просмотров изображения на 1.
    total_views = r.incr(f'image:{image.id}:views')
    # Увеличить рейтинг изображения на 1.
    r.zincrby('image_ranking', 1, image.id)
    return render(
        request,
        'images/image/detail.html',
        {
            'section': 'images',
            'image': image,
            'total_views': total_views,
        },
    )


@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом,
        # то доставить первую страницу
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            # Если AJAX-запрос и странница вне диапазона,
            # то вернуть пустую страницу.
            return HttpResponse('')
        # Если страница вне диапазона,
        # то вернуть последнюю страницу результатов
        images = paginator.page(paginator.num_pages)
    if images_only:
        return render(
            request,
            'images/image/list_images.html',
            {
                'section': 'images',
                'images': images,
            },
        )
    return render(
        request,
        'images/image/list.html',
        {
            'section': 'images',
            'images': images,
        },
    )


@login_required
def image_ranking(request):
    # Получить словарь рейтинга изображений.
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking] # noqa
    # Получить наиболее просматриваемые изображения.
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(
        request,
        'images/image/ranking.html',
        {
            'section': 'images',
            'most_viewed': most_viewed,
        },
    )
