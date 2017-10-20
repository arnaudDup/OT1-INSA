from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt


def search(request):
    return HttpResponse(get_template('search.html').render())

def fetchDoc(docId):
    with open('banana/articles/'+str(docId), 'rb') as articleFile:
        contents=articleFile.read()
        headline=contents.split('<headline>')[1].split('</headline>')[0].strip().replace('<p>',' ').replace('</p>',' ')
        if len(headline)>200:
            headline=headline[:200]+'...'
        text=contents.split('<text>')[1].split('</text>')[0]
    return headline, text
        

@csrf_exempt
def results(request):
    if request.method != 'POST':
        return redirect('/')
    if 'query' not in request.POST:
        return HttpResponseBadRequest("Error : Query does not exist.")

    topresults = manage_request_with_encoded_pl(request.POST['query'],10)
    results=[]
    for score, doc_id in topresults:
        title, content = fetchDoc(doc_id)
        results.append({'articleId':str(doc_id),
                        'title':title.replace('\n',' '),
                        'preview':content.replace('<p>',' ').replace('</p>',' ')})
         
    context = {'results':results,
               'query':request.POST['query']}
    return HttpResponse(get_template('results.html').render(context))

def viewArticle(request):
    if 'id' not in request.GET:
        return HttpResponseBadRequest("Error : No article ID specified.")
    doc_id = request.GET['id']
    title, content = fetchDoc(doc_id)
    article = {'id':doc_id,
               'title':mark_safe(title.replace('\n','<br/>')),
               'contents':mark_safe(content)}
    context = {'article':article}
    return HttpResponse(get_template('viewArticle.html').render(context))
