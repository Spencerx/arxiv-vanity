import os
from bs4 import BeautifulSoup
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views import static
from django.views.generic import ListView
from .models import Paper, Render

class PaperListView(ListView):
    model = Paper
    paginate_by = 25


def paper_detail(request, pk):
    paper = get_object_or_404(Paper, pk=pk)
    try:
        r = paper.renders.latest()
    except Render.DoesNotExist:
        raise Http404("Paper is not rendered")
    filename = os.path.join(settings.MEDIA_ROOT, "render-output", str(r.pk), "index.html")
    with open(filename) as fh:
        soup = BeautifulSoup(fh, "lxml")
    styles = soup.head.find_all('style')
    scripts = soup.head.find_all('script')
    return render(request, "papers/paper_detail.html", {
        "paper": paper,
        "render": r,
        "styles": ''.join(e.prettify() for e in styles),
        "scripts": ''.join(e.prettify() for e in scripts),
        "body": soup.body.encode_contents(),
    })


def paper_serve_static(request, pk, path):
    paper = get_object_or_404(Paper, pk=pk)
    try:
        r = paper.renders.latest()
    except Render.DoesNotExist:
        raise Http404("Paper is not rendered")
    if path == "":
        path = "index.html"
    document_root = os.path.join(settings.MEDIA_ROOT, "render-output", str(r.pk))
    return static.serve(request, path, document_root=document_root)
