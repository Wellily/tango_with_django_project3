from django import template
from rango2.models import Category

register = template.Library()


@register.inclusion_tag('rango2/cats.html')
def get_category_list(cat=None):
    return {'cats': Category.objects.all(),
            'act_cat': cat}
