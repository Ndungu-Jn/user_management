from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from .forms import (
    UserRegisterForm, UserUpdateForm, ProfileUpdateForm, CustomPasswordChangeForm
)

# Create your views here.
def home(request):
    return render(request, 'users/home.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)

login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})

# CRUD operations for User model (admin only)
class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_superuser
    

class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/user_create.html'
    success_url = reverse_lazy('user_list')
    
    def test_func(self):
        return self.request.user.is_superuser
        
    def form_valid(self, form):
        messages.success(self.request, f'User has been created!')
        return super().form_valid(form)    
    
class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = User
    template_name = 'users/user_detail.html'
    
    def test_func(self):
        return self.request.user.is_superuser   

class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'users/user_update.html'
    success_url = reverse_lazy('user_list')
    
    def test_func(self):
        return self.request.user.is_superuser
        
    def form_valid(self, form):
        messages.success(self.request, f'User has been updated!')
        return super().form_valid(form)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['p_form'] = ProfileUpdateForm(self.request.POST, instance=self.object.profile)
        else:
            context['p_form'] = ProfileUpdateForm(instance=self.object.profile)
        return context
        
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        p_form = ProfileUpdateForm(request.POST, instance=self.object.profile)
        
        if form.is_valid() and p_form.is_valid():
            return self.form_valid(form, p_form)
        else:
            return self.form_invalid(form, p_form)
            
    def form_valid(self, form, p_form):
        form.save()
        p_form.save()
        messages.success(self.request, f'User has been updated!')
        return redirect(self.success_url)
        
    def form_invalid(self, form, p_form):
        return self.render_to_response(
            self.get_context_data(form=form, p_form=p_form)
        )     
    
class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'users/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')
    
    def test_func(self):
        return self.request.user.is_superuser
        
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, f'User has been deleted!')
        return super().delete(request, *args, **kwargs)    