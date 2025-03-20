from django.urls import reverse_lazy
from django.views.generic.list import ListView
from unicodedata import category
from django.db.models import Count

from .forms import ExpenseSearchForm
from .models import Expense, Category
from .reports import summary_per_category
from django.db.models import Sum
from django.db.models.functions import TruncMonth


def summary_per_category(queryset):
    return {
        category: queryset.filter(category=category).aggregate(Sum('amount'))['amount__sum'] or 0
        for category in Category.objects.all()
    }

def summary_per_month(queryset):
    summary = queryset.annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('-month')
    return summary


class ExpenseListView(ListView):
    model = Expense
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        form = ExpenseSearchForm(self.request.GET)

        if form.is_valid():
            name = form.cleaned_data.get('name', '').strip()
            # 1. Pobranie danych z formularza dat od / do
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')

            # 2. Wyszukiwanie po odpowiedniej kategorii
            categories = form.cleaned_data.get('categories')

            # 3.Sortowanie po dacie / kategorii (rosnąco lub malejąco)
            sort_by = form.cleaned_data.get('sort_by')

            if name:
                queryset = queryset.filter(name__icontains=name)
            if date_from:
                queryset = queryset.filter(date__gte=date_from)
            if date_to:
                queryset = queryset.filter(date__lte=date_to)
            if categories:
                queryset = queryset.filter(category__in=categories)

            if sort_by:
                if sort_by in ['category', '-category']:
                    queryset = queryset.order_by(f'{sort_by}__name') if sort_by.startswith('-') else queryset.order_by('category')
                else:
                    queryset = queryset.order_by(sort_by)
            # 4. Wywołanie funkcji agregacyjnej do obliczenia łącznie wydanej sumy
            total_amount = queryset.aggregate(total=Sum('amount'))['total'] or 0

        return super().get_context_data(
            form=form,
            object_list=queryset,
            summary_per_category = summary_per_category(queryset),
            summary_per_month = summary_per_month(queryset),
            total_amount=total_amount,
            **kwargs)

class CategoryListView(ListView):
    model = Category
    paginate_by = 5
    fields = ['name']
    template_name = 'expenses/category_form.html'
    success_url = reverse_lazy('expenses:category-list')

    def get_queryset(self):
        return Category.objects.annotate(expense_count=Count('expense'))


