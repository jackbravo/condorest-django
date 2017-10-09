from datetime import datetime

from django.shortcuts import render

from revenue.models import Fee


def index(request):
    Fee.objects.filter(date__year=datetime.now().year)