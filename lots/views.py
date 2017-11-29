import json

from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse

from lots.models import Lot


@staff_member_required
def index(request):
    q = request.GET.get('q', '')
    queryset = Lot.objects.all().select_related('owner')
    if q:
        queryset = queryset.filter(Q(name__icontains=q) | Q(address__icontains=q) | Q(owner__name__icontains=q))
    queryset = queryset.prefetch_related('contacts')

    paginator = Paginator(queryset, 50)
    page = request.GET.get('page', 1)
    try:
        lots = paginator.page(page)
    except EmptyPage:
        lots = paginator.page(paginator.num_pages)

    return render(request, 'lots/index.html', context={
        'lots': lots,
    })

@staff_member_required
def search_ajax(request):
    q = request.GET.get('term')
    results = Lot.objects.select_related('owner').filter(Q(name__icontains=q) | Q(address__icontains=q) | Q(owner__name__icontains=q)).values('name', 'address', 'owner__name')
    return HttpResponse(json.dumps(list(results)))
