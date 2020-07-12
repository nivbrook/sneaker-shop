from django.shortcuts import render, HttpResponse, redirect
from main.models import *
import datetime
from django.contrib import messages

def index(request):
    if 'cart_id' not in request.session:
        cart = Cart.objects.create(total=0)
        request.session['cart_id']=cart.id

    recent_shoes = ShoeColor.objects.all().order_by('-created_at')[0:6]

    context = {
        'recent_shoes': recent_shoes,
        'air_jordans': Brand.objects.get(name="Air Jordan").models.all(),
        'nikes': Brand.objects.get(name="Nike").models.all(),
        'adidases': Brand.objects.get(name="Adidas").models.all(),
    }
    return render(request, 'home.html', context)

def catalog_page(request, browse_filter = "all"):
    if 'cart' not in request.session:
        cart = Cart.objects.create(total=0)
        request.session['cart']=cart.id

    all_brands = Brand.objects.all().order_by('name')
    all_models = ShoeModel.objects.all().order_by('model')
    sizes = [6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0]

    if request.method == 'GET' and request.GET.get('min'):
        min_price = request.GET['min']
    else:
        min_price = 0

    if request.method == 'GET' and request.GET.get('max'):
        max_price = request.GET['max']
    else:
        max_price = 10000


    if browse_filter == "all":
        category = "All Sneakers"
        display_shoes = ShoeColor.objects.filter(model__price__gte=min_price).filter(model__price__lte=max_price)
    elif browse_filter == "air jordan":
        category = "Air Jordan"
        display_shoes = ShoeColor.objects.filter(model__brand__name="Air Jordan").filter(model__price__gte=min_price).filter(model__price__lte=max_price)
    elif browse_filter == "nike":
        category = "Nike"
        display_shoes = ShoeColor.objects.filter(model__brand__name="Nike").filter(model__price__gte=min_price).filter(model__price__lte=max_price)
    elif browse_filter == "adidas":
        category = "Adidas"
        display_shoes = ShoeColor.objects.filter(model__brand__name="Adidas").filter(model__price__gte=min_price).filter(model__price__lte=max_price)
    else:
        model = ShoeModel.objects.get(id = int(browse_filter))
        category = model.model
        display_shoes = ShoeColor.objects.filter(model = model).filter(model__price__gte=min_price).filter(model__price__lte=max_price)

    print(max_price)
    print(min_price)

    context = {
        'shoes': display_shoes,
        'all_brands': all_brands,
        'all_models': all_models,
        'sizes': sizes,
        'category': category,
        'air_jordans': Brand.objects.get(name="Air Jordan").models.all(),
        'nikes': Brand.objects.get(name="Nike").models.all(),
        'adidases': Brand.objects.get(name="Adidas").models.all(),
        'max_price': max_price,
        'min_price': min_price,
    }
    return render(request, 'catalog.html', context)

def add_shoe_page(request):
    if 'admin' not in request.session:
        return redirect('/admin')
    
    context = {

    }
    return render(request,"add_shoe_page.html", context)

def add_shoe(request):
    if len(Brand.objects.filter(name=request.POST['brand']))>0:
        brand = Brand.objects.get(name=request.POST['brand'])
    else:
        brand = Brand.objects.create(name = request.POST['brand'])
    if len(ShoeModel.objects.filter(model=request.POST['model']))>0:
        model = ShoeModel.objects.get(model=request.POST['model'])
    else:
        model = ShoeModel.objects.create(model = request.POST['model'], price = request.POST['price'], brand=brand, desc=request.POST['desc'])
    
    colors = request.POST.getlist('colors[]')
    images = request.FILES.getlist('images[]')
    for i in range(0, len(colors), 1):
        new_color = ShoeColor.objects.create(color = colors[i], image = images[i], model = model)
        for counter in range(0, 13, 1):
            size = 6 + counter*0.5
            ShoeSize.objects.create(size = size, inventory = 5, quantity_sold = 0, color = new_color)

    return redirect('/admin/shoe_list')

def shoe_list(request):
    if 'admin' not in request.session:
        return redirect('/admin')

    model_id = request.POST.get('model_id', 0)
    if(model_id == 0 or model_id == "all"):
        shoes = ShoeSize.objects.all()
    else:
        shoes = ShoeSize.objects.filter(color__model__id = model_id)
    context = {
        'shoes': shoes,
        'models': ShoeModel.objects.all(),
    }

    return render(request, 'shoe_list.html', context)

def update_inv(request):
    shoe = ShoeSize.objects.get(id=request.POST['shoe_id'])
    shoe.inventory = request.POST['new_inventory']
    shoe.save()

    return redirect('/admin/shoe_list')

def update_img(request):
    shoe = ShoeColor.objects.get(id=request.POST['shoe_color_id'])
    shoe.image = request.FILES.get('new_image', False)
    shoe.save()

    return redirect('/admin/shoe_list')

def update_price(request):
    shoe = ShoeModel.objects.get(id=request.POST['shoe_id'])
    shoe.price = request.POST['new_price']
    shoe.save()

    return redirect('/admin/shoe_list')

def filter_list(request):
    model_id=request.POST['model_id']
    shoes_of_model = ShoeSize.objects.filter(color__model__id = model_id)
    context ={
        'shoes': shoes_of_model,
        'models': ShoeModel.objects.all(),
        'filtered': True,
    }

    return render(request, 'shoe_list.html', context)

def shoe_page(request, shoe_id):
    if 'cart' not in request.session:
        cart = Cart.objects.create(total=0)
        request.session['cart']=cart.id

    shoe = ShoeColor.objects.get(id=shoe_id)
    current_brand_id = shoe.model.brand.id
    related_shoes = ShoeColor.objects.filter(model__brand__id = current_brand_id).exclude(id = shoe.id)[0:6]

    context = {
        'shoe': ShoeColor.objects.get(id=shoe_id),
        'related_shoes': related_shoes,
        'air_jordans': Brand.objects.get(name="Air Jordan").models.all(),
        'nikes': Brand.objects.get(name="Nike").models.all(),
        'adidases': Brand.objects.get(name="Adidas").models.all(),
    }

    return render(request, 'shoe_page.html', context)

def refresh_cart_total(cart):
    total = 0
    for item in cart.cart_items.all():
        total+= item.quantity * item.shoe.color.model.price
    cart.total = total
    cart.save()

def add_to_cart(request):
    shoe = ShoeSize.objects.get(id=request.POST['size_id'])
    cart = Cart.objects.get(id=request.session['cart_id'])
    cart_item = CartItem.objects.create(shoe=shoe, quantity=1, cart=cart)

    refresh_cart_total(cart)

    return redirect('/cart')

def cart(request):
    if 'cart_id' not in request.session:
        cart = Cart.objects.create(total=0)
        request.session['cart_id']=cart.id
    context = {
        'cart': Cart.objects.get(id=request.session['cart_id']),
        'air_jordans': Brand.objects.get(name="Air Jordan").models.all(),
        'nikes': Brand.objects.get(name="Nike").models.all(),
        'adidases': Brand.objects.get(name="Adidas").models.all(),
    }

    return render(request, 'cart.html', context)

def update_quantity(request):
    item = CartItem.objects.get(id=request.POST['item_id'])
    if item.shoe.inventory<int(request.POST['new_quantity']):
        messages.error(request, "Sorry, that quantity is not currently in stock.")
        return redirect('/cart')
    item.quantity = request.POST['new_quantity']
    if int(request.POST['new_quantity'])>0:
        item.save()
    else:
        item.delete()
    cart = Cart.objects.get(id=request.session['cart_id'])

    refresh_cart_total(cart)

    return redirect('/cart')

def checkout(request):
    if 'cart_id' not in request.session:
        return redirect("/")

    context = {
        'cart': Cart.objects.get(id=request.session['cart_id']),
    }

    return render(request,'checkout_guest.html',context)

def checkout_process_guest(request):
    shipping_address = Address.objects.create(
        address = request.POST['address'],
        address2 = request.POST['address2'],
        city = request.POST['city'],
        state = request.POST['state'],
        zipcode = request.POST['zipcode'],
    )
    if 'same_address' in request.POST:
        billing_address = shipping_address
        cc_first_name = request.POST['first_name']
        cc_last_name = request.POST['last_name']
    else:
        billing_address = Address.objects.create(
            address = request.POST['cc_address'],
            address2 = request.POST['cc_address2'],
            city = request.POST['cc_city'],
            state = request.POST['cc_state'],
            zipcode = request.POST['cc_zipcode'],
        )
        cc_first_name = request.POST['cc_first_name']
        cc_last_name = request.POST['cc_last_name']
    
    guest_user = User.objects.create(
        first_name = request.POST['first_name'],
        last_name = request.POST['last_name'],
        email = request.POST['email'],
        password = "",
        address = shipping_address
    )
    expiration_date = datetime.date(int(request.POST['expireYYYY']),int(request.POST['expireM']),1)
    credit_card = CreditCard.objects.create(
        number = request.POST['cc_number'],
        security_code = request.POST['cc_security_code'],
        expiration_date = expiration_date,
        first_name = cc_first_name,
        last_name = cc_last_name,
        address = billing_address,
        user = guest_user,
    )
    cart = Cart.objects.get(id=request.session['cart_id'])
    new_order = Order.objects.create(
        status = "Processing",
        cart = cart,
        user = guest_user,
        credit_card = credit_card,
    )

    for item in cart.cart_items.all():
        shoe = item.shoe
        shoe.inventory = shoe.inventory-item.quantity
        shoe.quantity_sold = shoe.quantity_sold+item.quantity
        shoe.save()

    request.session['order_id'] = new_order.id
    request.session.pop("cart_id")

    return redirect('/confirmation')

def confirmation(request):
    current_order = Order.objects.get(id = request.session['order_id'])

    cc_last_digits = current_order.credit_card.number % 10000

    context = {
        'order': current_order,
        'cc_last_digits': cc_last_digits
    }

    return render(request, 'confirmation.html', context)

def orders_page(request):
    if 'admin' not in request.session:
        return render(request, "admin_login.html")

    context = {
        'orders': Order.objects.all().order_by('-created_at')
    }

    return render(request, 'orders_page.html', context)

def update_status(request):
    order = Order.objects.get(id=request.POST['order_id'])
    order.status = request.POST['status']
    order.save()

    return redirect('/admin/orders')

def order_details(request, order_id):
    if 'admin' not in request.session:
        return redirect('/admin')

    context = {
        'order': Order.objects.get(id=order_id)
    }

    return render(request,"order_details.html", context)

def admin_menu(request):
    if 'admin' not in request.session:
        return render(request, "admin_login.html")
    
    return render(request, "admin_menu.html")

def admin_login(request):
    if request.POST['password']=="admin":
        request.session['admin']=True
        return redirect('/admin')
    messages.error(request, "Incorrect Password")
    return redirect('/admin')

def admin_logout(request):
    request.session.pop("admin")

    return redirect('/admin')