import json

from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse

from lots.models import Lot


def index(request):
    return HttpResponse("Hello, world. You're at the lots index.")

def search(request):
    pass

def search_ajax(request):
    q = request.GET.get('term')
    results = Lot.objects.select_related('owner').filter(Q(name__icontains=q) | Q(address__icontains=q) | Q(owner__name__icontains=q)).values('name', 'address', 'owner__name')
    return HttpResponse(json.dumps(list(results)))
