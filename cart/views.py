from django.shortcuts import render
from engage.models import Item
from django.http import HttpResponse
from .cart import Cart

# Create your views here.


def add_to_cart(request, item_id):
    cart = Cart(request)
    cart.add(item_id)

    return render(request, "cart/menu_cart.html")


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
    return render(request, "cart/cart.html")


def hx_menu_cart(request):
    return render(request, "cart/menu_cart.html")


def hx_cart_total(request):
    return render(request, "cart/partials/cart_total.html")
