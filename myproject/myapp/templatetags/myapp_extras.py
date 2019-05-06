from django import template
import itertools

register = template.Library()

# Template tags: https://docs.djangoproject.com/en/dev/howto/custom-template-tags/
# SO solution: https://stackoverflow.com/questions/2415865/iterating-through-two-lists-in-django-templates


@register.filter(name='zip')
def zip_lists(a, b):
    return itertools.zip_longest(a, b)
