from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns=[
    path('register-student/',views.register_student,name='register-student'),
    path('register-lect/',views.register_lect,name='register-lect'),
    path('login/',views.login_user,name='login'),
    path('logout/',views.logout_user,name='logout'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_form.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_done.html'), name='password_reset_complete'),
    path('add-user/', views.add_user, name='add_user'),
    path('delete-user/', views.delete_user, name='delete_user'),
    path('change-role/', views.change_user_role, name='change_user_role'),


]