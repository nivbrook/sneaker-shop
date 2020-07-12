from django.urls import path
from main import views

urlpatterns = [
    path('', views.index),
    path('browse', views.catalog_page),
    path('admin/add_shoe_page', views.add_shoe_page),
    path('admin/add_shoe', views.add_shoe),
    path('admin/shoe_list', views.shoe_list),
    path('admin/update_inv', views.update_inv),
    path('admin/update_img', views.update_img),
    path('admin/update_price', views.update_price),
    path('shoe/<int:shoe_id>', views.shoe_page),
    path('add_to_cart', views.add_to_cart),
    path('cart', views.cart),
    path('update_quantity', views.update_quantity),
    path('checkout', views.checkout),
    path('checkout_process_guest', views.checkout_process_guest),
    path('confirmation', views.confirmation),
    path('admin/orders', views.orders_page),
    path('admin/update_status', views.update_status),
    path('admin/order/<int:order_id>', views.order_details),
    path('admin', views.admin_menu),
    path('admin/login', views.admin_login),
    path('admin/logout', views.admin_logout),
    path('browse/<str:browse_filter>', views.catalog_page),
]