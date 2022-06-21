from django.urls import path
from forum import views 
 
urlpatterns = [ 
    path('forums',views.forums_api),
    path('forums/<forum_id>',views.forum_api),
    path('image/<file_id>/',views.image_api),
    path('forums/<forum_id>/comments',views.comments_api),
    path('forums/<forum_id>/comments/<comment_id>',views.comment_api),
    path('comments/report',views.comment_report_api),
]