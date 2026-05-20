from django.shortcuts import render

def docs_index(request):
    return render(request, 'docs/index.html')

def docs_authentication(request):
    return render(request, 'docs/authentication.html')

def docs_summariser(request):
    return render(request, 'docs/summariser.html')