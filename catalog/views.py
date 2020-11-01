from django.shortcuts import render
from catalog.models import Book,Author,BookInstance,Genre
from django.views import generic
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from catalog.forms import RenewBookModelForm
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author


import datetime  

def index(request):
    """View function for the home page of site"""

    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    num_authors = Author.objects.count()

    num_visits = request.session.get('num_visits',0)
    request.session['num_visits'] = num_visits + 1

    context ={
        'num_books':num_books,
        'num_instances':num_instances,
        'num_instances_available':num_instances_available,
        'num_authors':num_authors,
        'num_visits':num_visits,
    }

    return render(request,'catalog/index.html',context=context)


class BookListView(generic.ListView):
    model=Book
    context_object_name = 'book_list'
    #queryset = Book.objects.filter(title__icontains='the')
    template_name = 'catalog/book_list.html'
    paginate_by = 2

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


class AuthorListView(generic.ListView):
    model=Author
    context_object_name = 'author_list'
    template_name = 'catalog/author_list.html'
    paginate_by = 2

    def get_queryset(self):
        return Author.objects.all()

class AuthorDetailView(generic.DetailView):
    model=Author
    # template_name = 'catalog/author_detail.html'
    # context_object_name = 'author'

  
class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class AllBorrowedBooks(PermissionRequiredMixin,generic.ListView):
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name ='catalog/all_borrowed_books_list.html'
    paginate_by = 10

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookModelForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        #form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})
        form =RenewBookModelForm(initial={'due_back': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(PermissionRequiredMixin,CreateView):
    permission_required = 'catalog.can_create_author'

    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}

class AuthorUpdate(PermissionRequiredMixin,UpdateView):
    permission_required = 'catalog.can_edit_author'

    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(PermissionRequiredMixin,DeleteView):
    permission_required = 'catalog.can_delete_author'

    model = Author
    success_url = reverse_lazy('authors')