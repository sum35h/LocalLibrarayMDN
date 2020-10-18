from django.shortcuts import render
from catalog.models import Book,Author,BookInstance,Genre
from django.views import generic
from django.shortcuts import get_object_or_404

def index(request):
    """View function for the home page of site"""

    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    num_authors = Author.objects.count()

    context ={
        'num_books':num_books,
        'num_instances':num_instances,
        'num_instances_available':num_instances_available,
        'num_authors':num_authors,
    }

    return render(request,'index.html',context=context)


class BookListView(generic.ListView):
    model=Book
    context_object_name = 'book_list'
    #queryset = Book.objects.filter(title__icontains='the')
    template_name = 'catalog/book_list.html'

    def get_queryset(self):
        return Book.objects.all()

    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)

        context['some_data']='This is just some data'
        return context

class BookDetailView(generic.DetailView):
    model=Book
    # template_name = 'catalog/book_detail.html'
    # context_object_name = 'book'
    # def get_queryset(self):
    #     book = get_object_or_404(Book,pk=primary_key)
    #     return book
