from django import template
import datetime
from django.utils import timezone
from django.utils.safestring import mark_safe
import json
register = template.Library()

@register.filter
def get_usernames(queryset):
    usernames = [item['user__username'] for item in queryset]
    return mark_safe(json.dumps(usernames))

@register.filter
def get_quantities(queryset):
    if not queryset:
        return mark_safe(json.dumps([]))
    if 'max_quantity' in queryset[0]:
        quantities = [item['max_quantity'] for item in queryset]
    elif 'min_quantity' in queryset[0]:
        quantities = [item['min_quantity'] for item in queryset]
    else:
        quantities = []
    return mark_safe(json.dumps(quantities))


@register.filter
def prettydate(value):
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    return value.strftime('%b %d, %Y %H:%M')

# @register.filter(name="prettydate")
# def prettydate(d):
#     if d is not None:
#         diff = timezone.now() - d
#         s = diff.seconds
#         if diff.days > 30 or diff.days < 0:
#             return d.strftime('Y-m-d H:i')
#         elif diff.days == 1:
#             return 'One day ago'
#         elif diff.days > 1:
#             return '{} days ago'.format(diff.days)
#         elif s <= 1:
#             return 'just now'
#         elif s < 60:
#             return '{} seconds ago'.format(s)
#         elif s < 120:
#             return 'one minute ago'
#         elif s < 3600:
#             return '{} minutes ago'.format(round(s/60))
#         elif s < 7200:
#             return 'one hour ago'
#         else:
#             return '{} hours ago'.format(round(s/3600))
#     else:
#         return None


