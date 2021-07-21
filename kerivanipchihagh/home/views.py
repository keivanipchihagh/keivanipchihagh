from django.shortcuts import render

def index(request):
    ''' Index view '''

    return render(request, template_name = 'home/index.html', context = None)