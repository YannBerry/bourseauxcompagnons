from django.http import Http404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.utils.translation import get_language
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
    TrigramSimilarity
)
from django.contrib.postgres.aggregates import StringAgg
from django.db.models.functions import Greatest

import functools
import operator
from datetime import datetime
from datetime import date

from outings.models import Outing
from activities.models import Activity
from outings.forms import OutingForm
from profiles.decorators import profile_required


#VIEWS FOR ANONYM WEB SURFERS

class OutingListView(ListView):
    '''
    By default this view displays the current and future outings (start_date or end_date >= today).
    If a search is launched it displays the outings matching the search query.
    If a filter is activated it displays the outings according to the filter.
    '''
    template_name = "outings/outing_list.html"
    nb_of_results = 0

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['all_activities'] = Activity.objects.all()
        context['nb_of_results'] = self.nb_of_results
        context['keywords'] = self.request.GET.get('k', None)
        context['selected_activities'] = self.request.GET.getlist('a', None)
        return context

    def get_queryset(self):
        keywords = self.request.GET.get('k', None)
        activities_in_current_language = 'activities__name_{}'.format(get_language())
        selected_activities = self.request.GET.getlist('a', None)
        start_date = self.request.GET.get('outing_start_date', None)
        if start_date:
            from_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = self.request.GET.get('outing_end_date', None)
        if end_date:
            till_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        if keywords:
            keywords_list = keywords.split()
            language = 'french_unaccent'
            '''
            __unaccent can't be used in SearchVector. Then we defined a "french_unaccent" config based on french and using the postgre unaccent extension
            
            in psql :
            CREATE TEXT SEARCH CONFIGURATION french_unaccent( COPY = french );
            ALTER TEXT SEARCH CONFIGURATION french_unaccent
            ALTER MAPPING FOR hword, hword_part, word
            WITH unaccent, french_stem;
            '''
            search_query = functools.reduce(operator.and_, [SearchQuery(k, config=language) for k in keywords_list])
            search_vector = (
                SearchVector('title', weight='A', config=language) +
                SearchVector('description', weight='B', config=language) +
                SearchVector(StringAgg(f'{ activities_in_current_language }', delimiter=' '), weight='B', config=language)
            )
            search_rank = SearchRank(search_vector, search_query)
            trigram_similarity = Greatest(TrigramSimilarity('title', keywords), TrigramSimilarity('description', keywords))
        
        q = Outing.objects.prefetch_related('activities').filter(start_date__gte=date.today())

        if start_date and end_date:
            q = q.filter(start_date__lte=till_date, end_date__gte=from_date)
        elif start_date:
            q = q.filter(end_date__gte=from_date)
        elif end_date:
            q = q.filter(start_date__lte=till_date)
        
        if keywords:
            q = q.annotate(rank=search_rank+trigram_similarity).filter(rank__gte=0.05).order_by('-rank', 'start_date')
        
        if selected_activities:
            q = q.filter(
                eval(' | '.join(f'Q({ activities_in_current_language }="{ selected_activity }")' for selected_activity in selected_activities))
            )
        
        self.nb_of_results = len(q)

        return q


class OutingDetailView(DetailView):
    model = Outing


#VIEWS FOR AUTHENTICATED PROFILES

@method_decorator([login_required, profile_required], name='dispatch')
class OutingCreateView(SuccessMessageMixin, CreateView):
    form_class = OutingForm
    template_name = 'outings/outing_form.html'
    success_message = "Votre sortie est désormais publiée !"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


@method_decorator([login_required, profile_required], name='dispatch')
class OutingUpdateView(UserPassesTestMixin, UpdateView):
    model = Outing
    form_class = OutingForm

    def test_func(self):
        outing_author = Outing.objects.get(slug=self.kwargs['slug']).author.username
        return self.request.user.username == outing_author


@method_decorator([login_required, profile_required], name='dispatch')
class OutingDeleteView(UserPassesTestMixin, DeleteView):
    model = Outing
    success_url = reverse_lazy('my-profile')

    def test_func(self):
        outing_author = Outing.objects.get(slug=self.kwargs['slug']).author.username
        return self.request.user.username == outing_author
