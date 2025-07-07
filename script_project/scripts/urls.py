# script/urls.py
from django.urls import path
from . import views  # 引入 views.py 中的视图函数

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),  # 登录页面
    path('register/', views.register_view, name='register'),  # 注册页面
    path('logout/', views.logout_view, name='logout'),  # 定义主页路由
    path('script/', views.script_view, name='script_view'), # 定义剧本视图路由
    path('script/overview/', views.script_overview, name='script_overview'),
    path('api/wordcloud/', views.get_wordcloud_data, name='get_wordcloud_data'),
    path('api/relationship-data/', views.get_relationship_data, name='get_relationship_data'),
    path('api/show_comments/', views.show_comments, name='show_comments'),
    path('upload_comment/', views.upload_comment, name='upload_comment'),
    path('script/overview/get_sentiment_stats/', views.get_sentiment_stats, name='get_sentiment_stats'),
]
