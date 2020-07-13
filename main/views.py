from django.shortcuts import render, HttpResponse, redirect
from main.models import *
import datetime
from django.contrib import messages

# Home
def index(request):
    # This checks if a cart already exists in session. If not, it creates a cart and saves its id to session.
    if 'cart_id' not in request.session:
        cart = Cart.objects.create(total=0)
        request.session['cart_id']=cart.id

    # Grabs the 6 most recent shoes created in the DB.
    recent_shoes = ShoeColor.objects.all().order_by('-created_at')[0:6]

    # Also grabs all the models of the three brands, for display in the top bar.
    context = {
        'recent_shoes': recent_shoes,
        'air_jordans': Brand.objects.get(name="Air Jordan").models.all(),
        'nikes': Brand.objects.get(name="Nike").models.all(),
        'adidases': Brand.objects.get(name="Adidas").models.all(),
    }
    return render(request, 'home.html', context)

# Catalog Page, works for Browse all, but also catagories and filters. Default filter is "all".
def catalog_page(request, browse_filter = "all"):
    if 'cart' not in request.session:
        cart = Cart.objects.create(total=0)
        request.session['cart']=cart.id

    # Info for the side-bar.
    all_brands = Brand.objects.all().order_by('name')
    all_models = ShoeModel.objects.all().order_by('model')

    # Checks if there are min and max price filters in the GET url, otherwise sets min and max to default values.
    if request.method == 'GET' and request.GET.get('min'):
        min_price = request.GET['min']
    else:
        min_price = 0

    if request.method == 'GET' and request.GET.get('max'):
        max_price = request.GET['max']
    else:
        max_price = 10000

    # Assigns display_shoes to either all, a brand, or a specific model in the else statement. "browse_filter" can include brand or model info. Always filters for price as well. 
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

    context = {
        'shoes': display_shoes,
        'all_brands': all_brands,
        'all_models': all_models,
        'category': category,
        'air_jordans': Brand.objects.get(name="Air Jordan").models.all(),
        'nikes': Brand.objects.get(name="Nike").models.all(),
        'adidases': Brand.objects.get(name="Adidas").models.all(),
        'max_price': max_price,
        'min_price': min_price,
    }
    return render(request, 'catalog.html', context)

# Add a shoe form page.
def add_shoe_page(request):
    # Kicks out user to /admin if they are not logged in as admin
    if 'admin' not in request.session:
        return redirect('/admin')
    
    context = {

    }
    return render(request,"add_shoe_page.html", context)

# Add shoe function.
def add_shoe(request):
    # Checks to see if brand already exists. Form was originally a text field for Brand input, but has since been changed to a drop down.
    if len(Brand.objects.filter(name=request.POST['brand']))>0:
        brand = Brand.objects.get(name=request.POST['brand'])
    else:
        brand = Brand.objects.create(name = request.POST['brand'])

    # Checks to see if the model already exists. This is if you are adding new colors to an already existing model in the database.
    if len(ShoeModel.objects.filter(model=request.POST['model']))>0:
        model = ShoeModel.objects.get(model=request.POST['model'])
    else:
        model = ShoeModel.objects.create(model = request.POST['model'], price = request.POST['price'], brand=brand, desc=request.POST['desc'])
    
    # Gets the colors and images for the colors, then creates the color objects for all colors.
    colors = request.POST.getlist('colors[]')
    images = request.FILES.getlist('images[]')
    for i in range(0, len(colors), 1):
        new_color = ShoeColor.objects.create(color = colors[i], image = images[i], model = model)
        # Creates a default inventory size of 5 for each possible size between 6.0 and 12.0 at increments of .5. These can later be changed in the manage inventory page.
        for counter in range(0, 13, 1):
            size = 6 + counter*0.5
            ShoeSize.objects.create(size = size, inventory = 5, quantity_sold = 0, color = new_color)
    # Shoes have been added to inventory. Each shoe is a ShoeSize model. Model structure is ShoeSize -> ShoeColor -> ShoeModel -> Brand.
    return redirect('/admin/shoe_list')

# Inventory Management Page.
def shoe_list(request):
    if 'admin' not in request.session:
        return redirect('/admin')

    # Checks if there is a Model filter applied before retrieving shoes.
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

# Updates inventory of specific size.
def update_inv(request):
    shoe = ShoeSize.objects.get(id=request.POST['shoe_id'])
    shoe.inventory = request.POST['new_inventory']
    shoe.save()

    return redirect('/admin/shoe_list')

# Updates image upload of specific color. Applies to all sizes.
def update_img(request):
    shoe = ShoeColor.objects.get(id=request.POST['shoe_color_id'])
    shoe.image = request.FILES.get('new_image', False)
    shoe.save()

    return redirect('/admin/shoe_list')

#Updates price of specific model. Prices are constant across all colors/sizes of the same model.
def update_price(request):
    shoe = ShoeModel.objects.get(id=request.POST['shoe_id'])
    shoe.price = request.POST['new_price']
    shoe.save()

    return redirect('/admin/shoe_list')

# def filter_list(request):
#     model_id=request.POST['model_id']
#     shoes_of_model = ShoeSize.objects.filter(color__model__id = model_id)
#     context ={
#         'shoes': shoes_of_model,
#         'models': ShoeModel.objects.all(),
#         'filtered': True,
#     }

#     return render(request, 'shoe_list.html', context)

# Catalog page for individual Model-Color
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

# Function used within views.py for refreshing the total of a cart when things are added or removed.
def refresh_cart_total(cart):
    total = 0
    for item in cart.cart_items.all():
        total+= item.quantity * item.shoe.color.model.price
    cart.total = total
    cart.save()

# Add shoe size instance to cart.
def add_to_cart(request):
    shoe = ShoeSize.objects.get(id=request.POST['size_id'])
    cart = Cart.objects.get(id=request.session['cart_id'])
    cart_item = CartItem.objects.create(shoe=shoe, quantity=1, cart=cart)

    refresh_cart_total(cart)

    return redirect('/cart')

# Show cart to user.
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

# Update the quantity in the cart.
def update_quantity(request):
    item = CartItem.objects.get(id=request.POST['item_id'])

    # Checks to make sure the new updated quantity is in stock.
    if item.shoe.inventory<int(request.POST['new_quantity']):
        messages.error(request, "Sorry, that quantity is not currently in stock.")
        return redirect('/cart')
    item.quantity = request.POST['new_quantity']

    #Updates quantity or deletes the CartItem if quantity has been updated to 0.
    if int(request.POST['new_quantity'])>0:
        item.save()
    else:
        item.delete()
    cart = Cart.objects.get(id=request.session['cart_id'])

    refresh_cart_total(cart)

    return redirect('/cart')

# Checkout page. Goes to form to input checkout information.
def checkout(request):
    if 'cart_id' not in request.session:
        return redirect("/")

    cart = Cart.objects.get(id=request.session['cart_id'])

    # Returns user to home is cart is empty.
    if not cart.cart_items.exists():
        return redirect("/")

    context = {
        'cart': Cart.objects.get(id=request.session['cart_id']),
    }

    return render(request,'checkout_guest.html',context)

# Checkout processing function.
def checkout_process_guest(request):
    # Creates shipping address.
    shipping_address = Address.objects.create(
        address = request.POST['address'],
        address2 = request.POST['address2'],
        city = request.POST['city'],
        state = request.POST['state'],
        zipcode = request.POST['zipcode'],
    )
    # Checks to see if Billing Address was marked same as Shipping Address.
    if 'same_address' in request.POST:
        billing_address = shipping_address
        # Uses shipping first and last name for credit card later.
        cc_first_name = request.POST['first_name']
        cc_last_name = request.POST['last_name']
    else:
        # Creates new address and saves the billing first name and last name for credit card.
        billing_address = Address.objects.create(
            address = request.POST['cc_address'],
            address2 = request.POST['cc_address2'],
            city = request.POST['cc_city'],
            state = request.POST['cc_state'],
            zipcode = request.POST['cc_zipcode'],
        )
        cc_first_name = request.POST['cc_first_name']
        cc_last_name = request.POST['cc_last_name']
    
    # Creates guest user. Assigns Shipping Address to user.
    guest_user = User.objects.create(
        first_name = request.POST['first_name'],
        last_name = request.POST['last_name'],
        email = request.POST['email'],
        password = "",
        address = shipping_address
    )
    # Credit Card expiration date set as a datetime, where it's the first of the month of the MM/YYYY provided
    expiration_date = datetime.date(int(request.POST['expireYYYY']),int(request.POST['expireM']),1)
    # Creates the credit card.
    credit_card = CreditCard.objects.create(
        number = request.POST['cc_number'],
        security_code = request.POST['cc_security_code'],
        expiration_date = expiration_date,
        first_name = cc_first_name,
        last_name = cc_last_name,
        address = billing_address,
        user = guest_user,
    )
    # Retrieves the cart from the session cart_id. Creates an Order object with it, the User, and Credit Card
    cart = Cart.objects.get(id=request.session['cart_id'])
    new_order = Order.objects.create(
        status = "Processing",
        cart = cart,
        user = guest_user,
        credit_card = credit_card,
    )

    # Removes the purchased items from the store inventory.
    for item in cart.cart_items.all():
        shoe = item.shoe
        shoe.inventory = shoe.inventory-item.quantity
        shoe.quantity_sold = shoe.quantity_sold+item.quantity
        shoe.save()

    # Places order_id in session to retrieve for confirmation page.
    request.session['order_id'] = new_order.id

    # Removes cart from session. The next visit to the store page will create a new cart.
    request.session.pop("cart_id")

    return redirect('/confirmation')

# Order confirmation page.
def confirmation(request):
    # Retrieves order from session.
    current_order = Order.objects.get(id = request.session['order_id'])

    # Formats credit card number to just show last digits.
    # This may be a security vulnerability. Not sure.
    cc_last_digits = current_order.credit_card.number % 10000

    # Because credit card expiration date is stored as a date with the first of the month,
    # this reformats it as a MM/YY
    cc_expiration_date = current_order.credit_card.expiration_date.strftime('%m/%y')

    context = {
        'order': current_order,
        'cc_last_digits': cc_last_digits,
        'cc_expiration_date': cc_expiration_date
    }

    return render(request, 'confirmation.html', context)

# Admin page for viewing all orders.
def orders_page(request):
    if 'admin' not in request.session:
        return render(request, "admin_login.html")

    context = {
        'orders': Order.objects.all().order_by('-created_at')
    }

    return render(request, 'orders_page.html', context)

# Update the status of the order between "Processing", "Shipped", or "Canceled"
def update_status(request):
    order = Order.objects.get(id=request.POST['order_id'])
    order.status = request.POST['status']
    order.save()

    return redirect('/admin/orders')

# Order details page. This is an order summary that can be used by the store to fullfill orders.
def order_details(request, order_id):
    if 'admin' not in request.session:
        return redirect('/admin')
    order = Order.objects.get(id=order_id)
    # Because credit card expiration date is stored as a date with the first of the month,
    # this reformats it as a MM/YY
    cc_expiration_date = order.credit_card.expiration_date.strftime('%m/%y')
    context = {
        'order': order,
        'cc_expiration_date': cc_expiration_date
    }
    return render(request,"order_details.html", context)

# Basic navigation menu for admin pages.
def admin_menu(request):
    # If admin hasn't been logged in, redirect to login page.
    if 'admin' not in request.session:
        return render(request, "admin_login.html")
    
    return render(request, "admin_menu.html")

# Logs in admin. Checks to see if password is "admin". This probably isn't secure.
def admin_login(request):
    if request.POST['password']=="admin":
        request.session['admin']=True
        return redirect('/admin')
    messages.error(request, "Incorrect Password")
    return redirect('/admin')

# Remove admin from session on logout.
def admin_logout(request):
    request.session.pop("admin")

    return redirect('/admin')