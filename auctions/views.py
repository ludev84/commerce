from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.forms import ModelForm
from django.contrib.auth.decorators import login_required

from .models import User, Listing


class newListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "price", "category"]


def index(request):
    return render(request, "auctions/index.html", {"listings": Listing.objects.all()})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


# @login_required
# def listing(request, id):
#     return render(
#         request, "auctions/listing.html", {"listing": Listing.objects.get(pk=id)}
#     )


def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    # Add this check to pass to the template
    is_in_watchlist = False
    if request.user.is_authenticated:
        is_in_watchlist = listing in request.user.watchlist.all()

    return render(
        request,
        "auctions/listing_detail.html",
        {
            "listing": listing,
            "is_in_watchlist": is_in_watchlist,  # Pass the boolean to the template
            # ... other context variables
        },
    )


@login_required
def view_watchlist(request):
    # Get all listings from the user's watchlist
    watched_listings = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {"listings": watched_listings})


@login_required
def new(request):
    # TODO: Add validations
    if request.method == "POST":
        title = request.POST["title"]
        price = request.POST["price"]
        category = request.POST["category"]

        new_listing = Listing(title=title, price=price, category=category)
        new_listing.save()
        return render(
            request,
            "auctions/listing.html",
            {"listing": Listing.objects.get(pk=new_listing.id)},
        )
    else:
        return render(
            request, "auctions/new.html", {"newListingForm": newListingForm()}
        )


@login_required
def toggle_watchlist(request, listing_id):
    # Ensure the method is POST for security
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=listing_id)
        user = request.user

        # Check if the listing is already in the user's watchlist
        if listing in user.watchlist.all():
            # If it is, remove it
            user.watchlist.remove(listing)
        else:
            # If it's not, add it
            user.watchlist.add(listing)

    # Redirect back to the listing's page
    return redirect("listing_detail", listing_id=listing_id)
