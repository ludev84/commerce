from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.forms import ModelForm
from django import forms
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bid


class newListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "price", "category"]


class BidForm(forms.Form):
    amount = forms.DecimalField(
        label="Your Bid", min_value=0.01, max_digits=6, decimal_places=2
    )


def index(request):
    return render(
        request,
        "auctions/index.html",
        {"listings": Listing.objects.filter(status=Listing.Status.ACTIVE)},
    )


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


def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    highest_bid = listing.bid_set.all().aggregate(Max("new_bid"))["new_bid__max"]
    # If there are no bids, the starting price is the current price
    current_price = round(highest_bid, 2) if highest_bid is not None else listing.price

    is_in_watchlist = False
    if request.user.is_authenticated:
        is_in_watchlist = listing in request.user.watchlist.all()

    error_message = None

    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            bid_amount = form.cleaned_data["amount"]
            # Check if bid is valid
            if bid_amount > current_price:
                new_bid = Bid(user=request.user, listing=listing, new_bid=bid_amount)
                listing.current_price = bid_amount
                listing.save()
                new_bid.save()
                return redirect("listing_detail", listing_id=listing_id)
            else:
                error_message = "Your bid must be higher than the current price."

    # For a GET request, create a fresh form
    bid_form = BidForm()

    return render(
        request,
        "auctions/listing_detail.html",
        {
            "listing": listing,
            "bid_form": bid_form,
            "highest_bid": current_price,
            "is_in_watchlist": is_in_watchlist,
            "error_message": error_message,
        },
    )


@login_required
def close_listing(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=listing_id)
        highest_bid = listing.bid_set.all().aggregate(Max("new_bid"))["new_bid__max"]
        winner_bid = Bid.objects.filter(listing=listing, new_bid=highest_bid).first()

        if request.user == listing.user:
            listing.status = listing.Status.CLOSED
            listing.winner = winner_bid.user
            listing.save()
            return redirect("index")
    # TODO: Handle exceptions


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

        new_listing = Listing(
            user=request.user,
            title=title,
            price=price,
            current_price=price,
            category=category,
        )
        new_listing.save()
        return render(
            request,
            "auctions/listing_detail.html",
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
