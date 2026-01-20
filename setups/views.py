from django.views.generic import CreateView, DetailView, ListView, View, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

from setups.models import Setup, Genre, Song, Band
from setups.forms import SetupForm, AddGearToSetupForm
from setups.services import SetupService


class SetupCreateView(LoginRequiredMixin, CreateView):
    """Create Setup using Service Layer"""
    model = Setup
    form_class = SetupForm
    template_name = 'setups/create.html'
    
    def form_valid(self, form):
        service = SetupService(user=self.request.user)
        
        try:
            setup = service.create_setup(
                name=form.cleaned_data['name'],
                description=form.cleaned_data.get('description', ''),
                genre=form.cleaned_data.get('genre'),
                band=form.cleaned_data.get('band'),
                song=form.cleaned_data.get('song'),
                is_public=form.cleaned_data.get('is_public', False)
            )
            
            messages.success(
                self.request, 
                f'Setup "{setup.name}" created! Now add gear to the signal chain.'
            )
            return redirect('setups:detail', pk=setup.pk)
            
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class SetupDetailView(LoginRequiredMixin, DetailView):
    """View setup with signal chain"""
    model = Setup
    template_name = 'setups/detail.html'
    context_object_name = 'setup'
    
    def get_object(self):
        service = SetupService(user=self.request.user)
        setup = service.get_setup_with_chain(self.kwargs['pk'])
        
        if not setup:
            from django.http import Http404
            raise Http404("Setup not found")
            
        # Increment views (exclude user enters)
        if self.request.user != setup.user:
            service.increment_views(setup.id)
        
        return setup
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Form for adding gear
        context['add_gear_form'] = AddGearToSetupForm(user=self.request.user)
        
        # Signal chain (already prefetched by service)
        context['signal_chain'] = self.object.signal_chain.all()
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle inline add gear form"""
        self.object = self.get_object()
        form = AddGearToSetupForm(request.POST, user=request.user)
        
        if form.is_valid():
            service = SetupService(user=request.user)
            
            try:
                item = service.add_gear_to_setup(
                    setup_id=self.object.id,
                    owned_gear_id=form.cleaned_data['owned_gear'].id,
                    order=form.cleaned_data.get('order'),
                    settings=form.cleaned_data.get('settings', {}),
                    notes=form.cleaned_data.get('notes', '')
                )
                
                messages.success(
                    request, 
                    f'Added {item.owned_gear} to signal chain!'
                )
                return redirect('setups:detail', pk=self.object.pk)
                
            except ValueError as e:
                messages.error(request, str(e))
        
        # If form invalid, re-render with errors
        context = self.get_context_data()
        context['add_gear_form'] = form
        return self.render_to_response(context)

class SetupUpdateView(LoginRequiredMixin, UpdateView):
    """
    User can only edit their setup
    """
    model = Setup
    form_class = SetupForm
    template_name = 'setups/update.html'

    def get_queryset(self):
        return Setup.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse('setups:detail', kwargs={'pk': self.object.pk})

class RemoveGearFromSetupView(LoginRequiredMixin, View):
    """Remove gear from signal chain"""
    
    def post(self, request, setup_id, item_id):
        service = SetupService(user=request.user)
        
        try:
            service.remove_gear_from_setup(setup_id, item_id)
            messages.success(request, 'Gear removed from signal chain!')
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('setups:detail', pk=setup_id)


class SetupListView(LoginRequiredMixin, ListView):
    """List user's setups"""
    model = Setup
    template_name = 'setups/list.html'
    context_object_name = 'setups'
    
    def get_queryset(self):
        service = SetupService(user=self.request.user)
        return service.get_user_setups()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = SetupService(user=self.request.user)
        context['setup_stats'] = service.get_statistics()
        return context


class CommunitySetupsView(ListView):
    """Community page - public setups"""
    model = Setup
    template_name = 'setups/community.html'
    context_object_name = 'setups'
    paginate_by = 20
    
    def get_queryset(self):
        service = SetupService(user=self.request.user if self.request.user.is_authenticated else None)
        return service.get_public_setups(
            genre=self.request.GET.get('genre'),
            band=self.request.GET.get('band'),
            song=self.request.GET.get('song'),
            search_query=self.request.GET.get('q')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all().order_by('name')
        context['songs'] = Song.objects.select_related('band').all().order_by('band__name', 'title')
        
        context['active_filters'] = {
            'genre': self.request.GET.get('genre'),
            'band': self.request.GET.get('band'),
            'song': self.request.GET.get('song'),
            'search': self.request.GET.get('q'),
        }
        return context


class ToggleSetupFavoriteView(LoginRequiredMixin, View):
    def post(self, request, setup_id):
        service = SetupService(user=request.user)
        
        try:
            setup = service.toggle_favorite(setup_id)
            status = 'added to' if setup.is_favorite else 'removed from'
            messages.success(request, f'Setup {status} favorites!')
        except ValueError as e:
            messages.error(request, str(e))
        
        next_url = request.META.get('HTTP_REFERER', reverse('setups:list'))
        return redirect(next_url)


class ToggleSetupPublicView(LoginRequiredMixin, View):
    """Toggle Public/Private"""
    def post(self, request, setup_id):
        service = SetupService(user=request.user)
        
        try:
            setup = service.setup_repo.toggle_public(setup_id)
            status = 'public' if setup.is_public else 'private'
            messages.success(request, f'Setup is now {status}!')
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('setups:detail', pk=setup_id)

class ToggleSetupSaveView(LoginRequiredMixin, View):
    def post(self, request, setup_id):
        service = SetupService(user=request.user)
        service.toggle_save_setup(setup_id)
        # Back to the site where we where
        return redirect(request.META.get('HTTP_REFERER', 'setups:community'))

class SavedSetupsListView(LoginRequiredMixin, ListView):
    model = Setup
    template_name = 'setups/saved_list.html'
    context_object_name = 'setups'

    def get_queryset(self):
        service = SetupService(user=self.request.user)
        return service.get_saved_setups()
