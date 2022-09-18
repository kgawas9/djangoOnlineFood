from django.shortcuts import HttpResponse

def home(request):
    return HttpResponse('This is our home page..')
