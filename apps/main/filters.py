import django_filters
from apps.main.models import Product, Category, Size


class ProductFilter(django_filters.FilterSet):
    # Фильтр по категориям (множественный выбор)
    category = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.all(),
        field_name='category',
        widget=django_filters.widgets.forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label='Категории'
    )
    
    # Фильтр по размерам (множественный выбор)
    sizes = django_filters.ModelMultipleChoiceFilter(
        queryset=Size.objects.all(),
        field_name='productsize__size',
        widget=django_filters.widgets.forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label='Размеры',
        distinct=True  # Чтобы избежать дублирования при JOIN
    )
    
    # Фильтр по цене (диапазон)
    price_min = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        widget=django_filters.widgets.forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Минимальная цена'
        }),
        label='Цена от'
    )
    
    price_max = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        widget=django_filters.widgets.forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Максимальная цена'
        }),
        label='Цена до'
    )
    
    # Или используй RangeFilter для диапазона цен
    # price = django_filters.RangeFilter(
    #     field_name='price',
    #     widget=django_filters.widgets.RangeWidget(attrs={
    #         'class': 'form-control'
    #     }),
    #     label='Диапазон цен'
    # )
    
    # Фильтр по цвету
    color = django_filters.CharFilter(
        field_name='color',
        lookup_expr='icontains',
        widget=django_filters.widgets.forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по цвету'
        }),
        label='Цвет'
    )
    
    # Фильтр по товарам со скидкой
    status_discount = django_filters.BooleanFilter(
        field_name='status_discount',
        widget=django_filters.widgets.forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Только со скидкой'
    )
    
    # Поиск по названию
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        widget=django_filters.widgets.forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по названию'
        }),
        label='Название товара'
    )
    
    # Сортировка
    ordering = django_filters.OrderingFilter(
        fields=(
            ('price', 'price'),
            ('created_at', 'created_at'),
            ('name', 'name'),
        ),
        field_labels={
            'price': 'Цене',
            '-price': 'Цене (убывание)',
            'created_at': 'Дате создания',
            '-created_at': 'Дате создания (новые)',
            'name': 'Названию',
            '-name': 'Названию (Z-A)',
        },
        label='Сортировка'
    )

    class Meta:
        model = Product
        fields = ['category', 'sizes', 'price_min', 'price_max', 'color', 'status_discount', 'name']