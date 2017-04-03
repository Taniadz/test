from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page

from .forms import CommentForm
from .models import Product, Votes, Comment


def get_comments_by_product_id(product):
    comments = Comment.objects.filter(product=product, added_at__gt=datetime.now() - timedelta(hours=24))
    return comments.order_by('-added_at')


def paginate(request, qs):
    try:
        limit = int(request.GET.get('limit', 10))
    except ValueError:
        limit = 10
    if limit > 100:
        limit = 10
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        raise Http404
    paginator = Paginator(qs, limit)
    try:
        page = paginator.page(page)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page, paginator


@login_required
def product_vote(request, pk, slug):
    obj, created = Votes.objects.get_or_create(user_id=request.user.id, product_id=pk)
    if created:
        messages.success(request, 'Thanks for vote')
    else:
        messages.error(request, 'Your have already voted for this product some time ago')
    return HttpResponseRedirect(reverse(product_detail, kwargs={'slug': slug}))


@cache_page(60 * 15)
def product_list(request):
    if request.GET.get("sort_by"):
        products = Product.objects.all().order_by('-votes')
    else:
        products = Product.objects.all().order_by('-created_at')
    page, paginator = paginate(request, products)
    paginator.baseurl = reverse('product')
    return render(request, 'product.html', {
        'products': page.object_list,
        'paginator': paginator,
        'page': page,
    })


@cache_page(60 * 15, key_prefix='product_detail')
def product_detail(request, slug):
    one_product = get_object_or_404(Product, slug=slug)
    comments = get_comments_by_product_id(one_product.pk)
    if request.method == "GET":
        form = CommentForm(initial={'product': one_product.id, 'slug': one_product.slug})
        return render(request, 'product_detail.html', {
            'one_product': one_product,
            "form": form,
            "comments": comments,
        })


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            url = "/"
            return HttpResponseRedirect(url)
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {
        'form': form
    })


def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat(timespec='minutes')
    else:
        raise TypeError


def comment_add(request):
    form = CommentForm(request.POST)
    if form.is_valid():
        form._user = request.user
        comment = form.save()
        messages.success(request, "The object has been modified.")
        if request.is_ajax():
            data = {
                "text": comment.text,
                "user": str(comment.author),
                "time": comment.added_at,
                "messages": render_to_string("messages.html", request=request),
                "comments": render_to_string("comments.html", request=request,
                                             context=dict(comments=get_comments_by_product_id(form['product'].data))),
            }
            return JsonResponse(data, content_type="application/json")
        return HttpResponseRedirect(reverse(product_detail, kwargs={'slug': form['slug'].data}))
