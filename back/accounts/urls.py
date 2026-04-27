from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('reviews/', views.review_list, name='review_list'),
    path('reviews/<int:review_id>/', views.review_detail, name='review_detail'),
    path('reviews/<int:review_id>/like/', views.review_like, name='review_like'),
    path('reviews/<int:review_id>/comments/', views.comment_create, name='comment_create'),
    path('comments/<int:comment_id>/', views.comment_delete, name='comment_delete'),
    path('ai-recommendations/', views.get_ai_recommendations, name='ai_recommendations'),
]