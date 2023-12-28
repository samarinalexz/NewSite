import random
from django import forms
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import CreateView, UpdateView, TemplateView

from bulletin_board import settings
from .forms import LoginUserForm, RegisterUserForm, ProfileUserForm, UserPasswordChangeForm, OneTimeCode
from .mixins import UserIsNotAuthenticated

User = get_user_model()
a = '123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
ls = list(a)
random.shuffle(ls)
one_time_code = ''.join([random.choice(ls) for x in range(5)])


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация'}


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('users:login'))


class RegisterUser(UserIsNotAuthenticated, CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация'}
    success_url = reverse_lazy('users:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация на сайте'
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        # Функционал для отправки письма и генерации токена
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_url = reverse_lazy('users:confirm_email', kwargs={'uidb64': uid, 'token': token})
        current_site = '127.0.0.1:8000'
        send_mail(
            'Подтвердите свой электронный адрес',
            f'Пожалуйста, перейдите по следующей ссылке, чтобы подтвердить свой адрес электронной почты: http://{current_site}{activation_url}| Код для активации {one_time_code}',
            'samarinization@yandex.ru',
            [user.email],
            fail_silently=False,
        )
        return redirect('users:email_confirmation_sent')


class UserConfirmEmailView(View):
    def get(self, request, uidb64, token, backend='django.contrib.auth.backends.ModelBackend'):
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('users:email_confirmed')
        else:
            return redirect('users:email_confirmation_failed')


class EmailConfirmationSentView(TemplateView):
    template_name = 'users/email_confirmation_sent.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Письмо активации отправлено'
        return context


class EmailConfirmedView(LoginView):
    fields = ['one_time_code']
    labels = {
        'one_time_code': 'Одноразовый код',
    }
    widgets = {
        'one_time_code': forms.TextInput(attrs={'class': 'form-input'}),
    }
    template_name = 'users/email_confirmed.html'
    form_class = OneTimeCode

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ваш электронный адрес активирован'
        return context


class EmailConfirmationFailedView(TemplateView):
    template_name = 'users/email_confirmation_failed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ваш электронный адрес не активирован'
        return context


class ProfileUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {'title': 'Профиль пользователя',
                     'default_image': settings.DEFAULT_USER_IMAGE,
                     }

    def get_success_url(self):
        return reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'