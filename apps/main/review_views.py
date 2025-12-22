from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Avg, Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse
from apps.main.models import Product
from apps.main.review_models import Review, ReviewImage, ReviewHelpful
from apps.main.review_forms import ReviewForm, ReviewEditForm


@login_required
def review_create(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    print(f"=== REVIEW CREATE DEBUG ===")
    print(f"User: {request.user}")
    print(f"Method: {request.method}")
    print(f"POST data: {request.POST}")
    print(f"FILES: {request.FILES}")
    
    # Проверка на существующий отзыв
    existing_review = Review.objects.filter(product=product, user=request.user).first()
    if existing_review:
        print(f"User already has review: {existing_review.id}")
        messages.warning(request, 'You have already reviewed this product.')
        return redirect('main:product_detail', id=product.id, slug=product.slug)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        
        print(f"Form valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        
        if form.is_valid():
            # Создание отзыва
            review = Review.objects.create(
                product=product,
                user=request.user,
                rating=form.cleaned_data['rating'],
                title=form.cleaned_data['title'],
                content=form.cleaned_data['content']
            )
            print(f"Review created: {review.id}")
            
            # Обработка изображений
            images = request.FILES.getlist('images')
            if images:
                if len(images) > 5:
                    messages.error(request, 'Maximum 5 images allowed.')
                else:
                    max_size = 5 * 1024 * 1024  # 5MB
                    for image in images:
                        if image.size > max_size:
                            messages.error(request, f'{image.name} is too large (max 5MB).')
                            continue
                        if image.content_type not in ['image/jpeg', 'image/png', 'image/webp']:
                            messages.error(request, f'{image.name} is not a supported format.')
                            continue
                        
                        ReviewImage.objects.create(
                            review=review,
                            image=image
                        )
            
            messages.success(request, 'Review submitted successfully!')
            return redirect('main:product_detail', id=product.id, slug=product.slug)
        
        else:
            # При ошибке валидации
            if request.headers.get('HX-Request'):
                return render(request, 'main/partials/review_form.html', {
                    'form': form,
                    'product': product
                })
    
    # GET запрос - показываем форму
    else:
        form = ReviewForm()
    
    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/review_form.html', {
            'form': form,
            'product': product
        })
    
    return redirect('main:product_detail', id=product.id, slug=product.slug)

@require_http_methods(["GET", "POST"])
@login_required
def review_edit(request, review_id):
    review = get_object_or_404(
        Review.objects.select_related('product', 'user'),
        id=review_id
    )
    
    if review.user != request.user:
        messages.error(request, 'You can only edit your own reviews.')
        return redirect('main:product_detail', id=review.product.id, slug=review.product.slug)
    
    if not review.can_edit:
        messages.error(request, 'Reviews can only be edited within 30 days of posting.')
        return redirect('main:product_detail', id=review.product.id, slug=review.product.slug)
    
    if request.method == 'POST':
        form = ReviewEditForm(request.POST, request.FILES, instance=review)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    review.rating = form.cleaned_data['rating']
                    review.title = form.cleaned_data['title']
                    review.content = form.cleaned_data['content']
                    review.save()
                    
                    images = request.FILES.getlist('images')
                    for image in images:
                        ReviewImage.objects.create(
                            review=review,
                            image=image
                        )
                    
                    messages.success(request, 'Your review has been updated successfully!')
                    
                    if request.headers.get('HX-Request'):
                        return render(request, 'main/partials/review_item.html', {
                            'review': review,
                            'user': request.user
                        })
                    
                    return redirect('main:product_detail', id=review.product.id, slug=review.product.slug)
            
            except Exception as e:
                messages.error(request, 'An error occurred while updating your review.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = ReviewEditForm(instance=review)
    
    context = {
        'form': form,
        'review': review,
        'product': review.product
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/review_form.html', context)
    
    return render(request, 'main/review_edit.html', context)


@require_POST
@login_required
def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    if review.user != request.user and not request.user.is_staff:
        if request.headers.get('HX-Request'):
            return HttpResponse(status=403)
        messages.error(request, 'You can only delete your own reviews.')
        return redirect('main:product_detail', id=review.product.id, slug=review.product.slug)
    
    product_id = review.product.id
    product_slug = review.product.slug
    
    review.delete()
    messages.success(request, 'Your review has been deleted.')
    
    if request.headers.get('HX-Request'):
        return HttpResponse(status=200)
    
    return redirect('main:product_detail', id=product_id, slug=product_slug)


@require_POST
@login_required
def review_image_delete(request, image_id):
    image = get_object_or_404(ReviewImage, id=image_id)
    
    if image.review.user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    image.delete()
    
    if request.headers.get('HX-Request'):
        return HttpResponse(status=200)
    
    return JsonResponse({'success': True})


@require_POST
@login_required
def review_helpful(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    if review.user == request.user:
        return JsonResponse({'error': 'Cannot mark own review as helpful'}, status=400)
    
    helpful, created = ReviewHelpful.objects.get_or_create(
        review=review,
        user=request.user
    )
    
    if not created:
        helpful.delete()
        review.helpful_count = max(0, review.helpful_count - 1)
        action = 'removed'
    else:
        review.helpful_count += 1
        action = 'added'
    
    review.save(update_fields=['helpful_count'])
    
    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/review_helpful_button.html', {
            'review': review,
            'user': request.user
        })
    
    return JsonResponse({
        'success': True,
        'action': action,
        'helpful_count': review.helpful_count
    })


def review_list(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    reviews = Review.objects.filter(product=product).select_related(
        'user'
    ).prefetch_related('images')
    
    sort_by = request.GET.get('sort', 'recent')
    rating_filter = request.GET.get('rating')
    
    if rating_filter and rating_filter.isdigit():
        reviews = reviews.filter(rating=int(rating_filter))
    
    if sort_by == 'helpful':
        reviews = reviews.order_by('-helpful_count', '-created_at')
    elif sort_by == 'rating_high':
        reviews = reviews.order_by('-rating', '-created_at')
    elif sort_by == 'rating_low':
        reviews = reviews.order_by('rating', '-created_at')
    else:
        reviews = reviews.order_by('-created_at')
    
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    stats = Review.objects.filter(product=product).aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id'),
        rating_5=Count('id', filter=Q(rating=5)),
        rating_4=Count('id', filter=Q(rating=4)),
        rating_3=Count('id', filter=Q(rating=3)),
        rating_2=Count('id', filter=Q(rating=2)),
        rating_1=Count('id', filter=Q(rating=1)),
    )
    
    context = {
        'product': product,
        'reviews': page_obj,
        'stats': stats,
        'sort_by': sort_by,
        'rating_filter': rating_filter,
        'user': request.user
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'main/partials/review_list.html', context)
    
    return render(request, 'main/review_list.html', context)