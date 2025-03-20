from django import forms
from .models import Expense, Category



class ExpenseSearchForm(forms.ModelForm):
    # 1. Szukanie danych za pomocą dat. (od/do)
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type':'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type':'date'}))

    # 2. Wyszukiwanie po kategoriach
    categories = forms.ModelMultipleChoiceField(
        queryset = Category.objects.all(),
        required = False,
        widget = forms.CheckboxSelectMultiple
    )

    # 3. Sortowanie po dacie / kategorii (rosnąco lub malejąco)
    sort_by = forms.ChoiceField(
        choices = (
            ('', 'Default'),
            ('category', 'Category (ASC)'),
            ('-category', 'Category (DESC)'),
            ('date', 'Date (ASC)'),
            ('-date', 'Date (DESC)')
        ),
        required = False
    )

    class Meta:
        model = Expense
        fields = ('name', 'date_from', 'date_to', 'categories', 'sort_by')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False

