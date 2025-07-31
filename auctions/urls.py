from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    # path("listing/<int:id>", views.listing_detail, name="listing"),
    path("new", views.new, name="new"),
    path("listing/<int:listing_id>", views.listing_detail, name="listing_detail"),
    path("watchlist", views.view_watchlist, name="watchlist"),
    path(
        "watchlist/toggle/<int:listing_id>",
        views.toggle_watchlist,
        name="toggle_watchlist",
    ),
    path(
        "listing/close/<int:listing_id>",
        views.close_listing,
        name="close_listing",
    ),
    path("comment/<int:listing_id>", views.add_comment, name="add_comment"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category_value>", views.category, name="category"),
]
