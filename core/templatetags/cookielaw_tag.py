import warnings

from django import template
from classytags.helpers import InclusionTag
from django.template.loader import render_to_string

register = template.Library()


class cookielawBanner(InclusionTag):
    """
    Displays cookie law banner only if user has not dismissed it yet.
    """

    template = 'cookielaw/banner.html'

    def render_tag(self, context, **kwargs):
        template = self.get_template(context, **kwargs)
        
        if 'request' not in context:
            warnings.warn('No request object in context. '
                          'Are you sure you have django.core.context_processors.request enabled?')
            return ''

        elif context['request'].COOKIES.get('cookielaw_accepted', False):
            return ''

        data = self.get_context(context, **kwargs)
        output = render_to_string(template, data, getattr(context, 'request', None))
        return output

register.tag(cookielawBanner)

# from django import template

# register = template.Library()

# @register.inclusion_tag('cookielaw/banner.html')
# def cookielawbanner():
#     pass