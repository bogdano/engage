from django.shortcuts import render, redirect
from engage.models import Item
from accounts.models import CustomUser
from django.http import HttpResponse
from .cart import Cart
from django.template.loader import render_to_string
from django.core.mail import send_mail
import random

# Create your views here.


def add_to_cart(request, item_id):
    cart = Cart(request)
    cart.add(item_id)
    return render(request, "cart/menu_cart.html")


def add_to_cart_from_store(request, item_id):
    cart = Cart(request)
    cart.add(item_id)
    return redirect("store")


def update_cart(request, item_id, action):
    cart = Cart(request)

    if action == "increment":
        cart.add(item_id, 1, True)
    else:
        cart.add(item_id, -1, True)

    item = Item.objects.get(pk=item_id)
    if cart.get_item(item_id) == None:
        response = HttpResponse()
        response["HX-Trigger"] = "update-menu-cart"
        return response
    quantity = cart.get_item(item_id)["quantity"]

    item = {
        "item": {
            "id": item_id,
            "name": item.name,
            "image": item.image,
            "price": item.price,
        },
        "total_price": (quantity * item.price),
        "quantity": quantity,
    }

    response = render(request, "cart/partials/cart_item.html", {"item": item})
    response["HX-Trigger"] = "update-menu-cart"

    return response


def cart(request):
    if not request.user.is_authenticated:
        return redirect("send_login_link")
    user = request.user
    return render(request, "cart/cart.html", {"user": user})


def hx_menu_cart(request):
    return render(request, "cart/menu_cart.html")


def hx_cart_total(request):
    return render(request, "cart/partials/cart_total.html")

def hx_summary(request):
    return render(request, "cart/partials/summary.html")


def checkout(request):
    if not request.user.is_authenticated:
        return redirect("send_login_link")
    cart = Cart(request)
    total = cart.total()
    user = request.user
    if request.user.balance >= total and len(cart) > 0:
        items = cart
        email_order(request, user)
        clear_cart(request)
        user.balance -= total
        user.save()
        return render(request, "cart/checkout.html", {"items": items})
    elif len(cart) > 0:
        # fail state; not enough currency
        # render with error message
        response = render(request, "cart/cart.html", {"insufficient_funds": True})
        return response
    else:
        response = render(request, "cart/cart.html", {"empty_cart": True})
        return response


def email_order(request, user):
    cart = Cart(request)
    admin = list(CustomUser.objects.filter(is_staff=True))
    email = []
    for staff in admin:
        email.append(staff.email)
    subject = "New Order"
    message = render_to_string(
        "cart/partials/order_message.html", {"user": user, "cart": cart}
    )
    from_email = "noreply@engage.bogz.dev"
    send_mail(subject, message, from_email, email)


def clear_cart(request):
    cart = Cart(request)
    items = Item.objects.all()
    cart.empty()
    return render(request, "store.html", {"items": items})
