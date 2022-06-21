from django.urls import path
from ecommerce import views
from ecommerce import seller_views
from ecommerce import analytics_views
 
urlpatterns = [ 
    path('stores',views.stores_api),
    path('stores/<store_id>',views.store_api),
    path('categories',views.categories_api),
    path('items',views.items_api),
    path('items/<item_id>',views.item_api),
    path('image/<file_id>', views.image_api),
    path('user/orders', views.user_orders_api),
    path('seller/orders/<store_id>', seller_views.seller_orders_api),
    path('seller/<owner_id>/stores', seller_views.seller_stores_api),
    path('recommend/items', analytics_views.product_recommend_api),
]