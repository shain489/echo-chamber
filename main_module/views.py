from django.shortcuts import *

def search_view(request):
    return render(request, 'main_module/search.html')
    # return HttpResponse('hello')

def search_results(request):
    query = request.GET.get('query', '')
    # Process the query here
    # For now, we'll just pass it back to the template
    return render(request, 'main_module/search_results.html', {'query': query})