from django.shortcuts import render, redirect
from django.db.models import Q
from main.models import *
from datetime import datetime

def all_products_func(request):
    products = Product.objects.all()
    manufacturers = Manufacturer.objects.all()
    categories = Category.objects.all()
    recently_viewed_products = get_watched_recently_from_session_func(request)


    if products.exists():
        min_price = min(product.price for product in products)
        max_price = max(product.price for product in products)
    else:
        min_price = 0
        max_price = 1000
    
    manufacturers_with_count = []
    for manufacturer in manufacturers:
        count = products.filter(manufacturer_id=manufacturer).count()
        manufacturers_with_count.append({
            'manufacturer': manufacturer,
            'count': count
        })
    
    categories_with_count = []
    for category in categories:
        count = products.filter(category_id=category).count()
        categories_with_count.append({
            'category': category,
            'count': count
        })
    
    series = []
    for product in products:
        title_words = product.title.split()
        if len(title_words) >= 2:
            series_name = ' '.join(title_words[:2])
            if not any(s['name'] == series_name for s in series):
                count = products.filter(title__icontains=series_name).count()
                series.append({
                    'name': series_name,
                    'count': count
                })
    
    processors = []
    for category in categories:
        if 'processor' in category.name.lower() or 'chip' in category.name.lower():
            count = products.filter(category_id=category).count()
            processors.append({
                'name': category.name,
                'count': count
            })
    
    slovnik = {
        "products": products,
        "manufacturers": manufacturers_with_count,
        "categories": categories_with_count,
        "series": series,
        "processors": processors,
        "min_price": min_price,
        "max_price": max_price,
        "recently_viewed_products": recently_viewed_products
    }
    return render(request, "all_products.html", context=slovnik)

def add_product_func(request):
    if request.method == "POST":
        title = request.POST["title"]
        price = request.POST["price"]
        product_image = request.POST["product_image"]
        description = request.POST["description"]
        count = request.POST["count"]
        status = request.POST["status"]
        
        isavaible = request.POST["isavaible"]
        if isavaible == "yes":
            isavaible = True
        else:
            isavaible = False

        manufacturer_id = request.POST["manufacturer_id"]
        category_id = request.POST["category_id"]

        manufacturer = Manufacturer.objects.get(id = manufacturer_id)
        category = Category.objects.get(id = category_id)

        Product.objects.create(title = title, price = price, product_image = product_image, description = description, count = count, status = status, isavaible = isavaible, manufacturer_id = manufacturer, category_id = category)

        return render(request, "add_product.html")
    
    manufacturers = Manufacturer.objects.all()
    categories = Category.objects.all()

    slovnik = {
        "manufacturers": manufacturers,
        "categories": categories
    }    

    return render(request, "add_product.html", context=slovnik)


def add_manufacturer_func(request):
    if request.method == "POST":
        name = request.POST["name"]
        country = request.POST["country"]
        buisness_stream = request.POST["buisness_stream"]
        description = request.POST["description"]

        Manufacturer.objects.create(name = name, country = country, buisness_stream = buisness_stream, description = description)

    return render(request, "add_manufacturer.html")

def add_category_func(request):
    if request.method == "POST":
        name = request.POST["name"]

        Category.objects.create(name = name)

        
    return render(request, "add_category.html")

def info_product_func(request, id):
    product = Product.objects.get(id = id)
    save_to_session_func(request, id)
    slovnik = {
        "product": product
    }
    
    return render(request, "info_product.html", context=slovnik)

def create_cart_func(request):
    if request.method == "POST":
        user = request.user
        Cart.objects.create(user=user)
        
    return render(request, "info_product.html") 

def add_item_to_cart_func(request, id):
    if request.method == "POST":
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user)
        product = Product.objects.get(id=id)
        cartitem, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cartitem.count += 1
            cartitem.save()
    print("Створено:", cartitem)
    print("Його cart.id:", cartitem.cart.id)
    return redirect(info_cart_func)

def info_cart_func(request):
    user = request.user
    cart = Cart.objects.get(user = user)
    cartitems = CartItem.objects.filter(cart = cart)
    print("Cart ID:", cart.id)
    print("Items:", cartitems)
    mainprice = 0

    list = []
    for i in cartitems:
        result = i.product.price * i.count
        list.append((i, result))
        mainprice += i.product.price * i.count
    slovnik = {
        "cartitems": list,
        "mainprice": mainprice
    }
    return render(request, "info_cart.html", context=slovnik)
    

def add_item_plus_one_in_cart_func(request, id):
    if request.method == "POST":
        cartitem = CartItem.objects.get(id = id)
        cartitem.count += 1
        cartitem.save()
    return redirect(info_cart_func)

def remove_item_minus_one_in_cart_func(request, id):
    if request.method == "POST":
        cartitem = CartItem.objects.get(id = id)
        cartitem.count -= 1

        if cartitem.count == 0:
            cartitem.delete()
        else:
            cartitem.save()

    return redirect(info_cart_func)

def clear_cart_func(request):
    if request.method == "POST":
        clear_cart(request.user)
            
    return redirect(info_cart_func)

def clear_cart(user):
    cart = Cart.objects.get(user = user)
    cartitems = CartItem.objects.filter(cart = cart)
    for cartitem in cartitems:
        cartitem.delete()
            
def confirm_order_func(request):
    if request.method == "POST":
        if request.POST.get("card_number") != "":
            cardnumber = request.POST.get("card_number")
            cardexpiry = request.POST.get("card_expiry")
            cardcvc = request.POST.get("card_cvc")
            cardname = request.POST.get("card_name")
            user = request.user

            paymentmethod = PaymentMethod.objects.create(card_number = cardnumber, card_expiry = cardexpiry, card_cvc = cardcvc, card_name = cardname, type = "by_card", user = user)
            paymentmethod.save()

        elif request.POST.get("email") != "":
            email = request.POST.get("email")
            user = request.user

            paymentmethod = PaymentMethod.objects.create(email = email, user = user, type = "paypal")
            paymentmethod.save()

        else:
            user = request.user
            paymentmethod = PaymentMethod.objects.create(user = user, type = "cash")
            paymentmethod.save()

        cart = Cart.objects.get(user = request.user)

        order = Order.objects.create(user = request.user, paymentmethod = paymentmethod, status = "In process", date_of_create = datetime.now())
        order.save()

        cartitems = CartItem.objects.filter(cart = cart)
        for cartitem in cartitems:
            orderitem = OrderItem.objects.create(order = order, product = cartitem.product, count = cartitem.count)
            orderitem.save()

        clear_cart(request.user)

        return redirect(all_orders_func)
    
def all_orders_func(request):
    user = request.user
    orders = Order.objects.filter(user = user)
    orderdictionary = {}
 
    for i in orders:
        orderitems = OrderItem.objects.filter(order = i)
        orderscortage = []
        totalprice = 0

        for j in orderitems:
            totalprice += j.product.price * j.count
            orderscortage.append((j, totalprice))
            
        orderdictionary[i] = (orderscortage, totalprice)

    return render(request, "all_orders.html", {"orders": orderdictionary})        
    

def delete_all_orders_func(request):
    Order.objects.all().delete()
    return redirect(all_products_func)

def filter_by_manufacturer_func(request):
    manufacturer_ids = request.POST.getlist("manufacturer_ids")
    products = Product.objects.filter(manufacturer_id__in=manufacturer_ids) if manufacturer_ids else Product.objects.all()
    
    manufacturers = Manufacturer.objects.all()
    categories = Category.objects.all()
    
    if products.exists():
        min_price = min(product.price for product in products)
        max_price = max(product.price for product in products)
    else:
        min_price = 0
        max_price = 1000
    
    manufacturers_with_count = []
    for manufacturer in manufacturers:
        count = Product.objects.filter(manufacturer_id=manufacturer).count()
        manufacturers_with_count.append({
            'manufacturer': manufacturer,
            'count': count
        })
    
    categories_with_count = []
    for category in categories:
        count = Product.objects.filter(category_id=category).count()
        categories_with_count.append({
            'category': category,
            'count': count
        })
    
    series = []
    for product in products:
        title_words = product.title.split()
        if len(title_words) >= 2:
            series_name = ' '.join(title_words[:2])
            if not any(s['name'] == series_name for s in series):
                count = products.filter(title__icontains=series_name).count()
                series.append({
                    'name': series_name,
                    'count': count
                })
    
    processors = []
    for category in categories:
        if 'processor' in category.name.lower() or 'chip' in category.name.lower():
            count = Product.objects.filter(category_id=category).count()
            processors.append({
                'name': category.name,
                'count': count
            })
    
    slovnik = {
        "products": products,
        "manufacturers": manufacturers_with_count,
        "categories": categories_with_count,
        "series": series,
        "processors": processors,
        "min_price": min_price,
        "max_price": max_price
    }
    return render(request, "all_products.html", context=slovnik)

def filter_by_category_func(request):
    category_ids = request.POST.getlist("category_ids")
    products = Product.objects.filter(category_id__in=category_ids) if category_ids else Product.objects.all()
    
    manufacturers = Manufacturer.objects.all()
    categories = Category.objects.all()
    
    if products.exists():
        min_price = min(product.price for product in products)
        max_price = max(product.price for product in products)
    else:
        min_price = 0
        max_price = 1000
    
    manufacturers_with_count = []
    for manufacturer in manufacturers:
        count = Product.objects.filter(manufacturer_id=manufacturer).count()
        manufacturers_with_count.append({
            'manufacturer': manufacturer,
            'count': count
        })
    
    categories_with_count = []
    for category in categories:
        count = Product.objects.filter(category_id=category).count()
        categories_with_count.append({
            'category': category,
            'count': count
        })
    
    series = []
    for product in products:
        title_words = product.title.split()
        if len(title_words) >= 2:
            series_name = ' '.join(title_words[:2])
            if not any(s['name'] == series_name for s in series):
                count = products.filter(title__icontains=series_name).count()
                series.append({
                    'name': series_name,
                    'count': count
                })
    
    processors = []
    for category in categories:
        if 'processor' in category.name.lower() or 'chip' in category.name.lower():
            count = Product.objects.filter(category_id=category).count()
            processors.append({
                'name': category.name,
                'count': count
            })
    
    slovnik = {
        "products": products,
        "manufacturers": manufacturers_with_count,
        "categories": categories_with_count,
        "series": series,
        "processors": processors,
        "min_price": min_price,
        "max_price": max_price
    }
    return render(request, "all_products.html", context=slovnik)

def filter_by_price_func(request):
    min_price = float(request.POST.get("min_price", 0))
    max_price = float(request.POST.get("max_price", 1000))
    
    products = Product.objects.filter(price__gte=min_price, price__lte=max_price)
    manufacturers = Manufacturer.objects.all()
    categories = Category.objects.all()
    
    if products.exists():
        min_price_db = min(product.price for product in products)
        max_price_db = max(product.price for product in products)
    else:
        min_price_db = min_price
        max_price_db = max_price
    
    manufacturers_with_count = []
    for manufacturer in manufacturers:
        count = Product.objects.filter(manufacturer_id=manufacturer).count()
        manufacturers_with_count.append({
            'manufacturer': manufacturer,
            'count': count
        })
    
    categories_with_count = []
    for category in categories:
        count = Product.objects.filter(category_id=category).count()
        categories_with_count.append({
            'category': category,
            'count': count
        })
    
    series = []
    for product in products:
        title_words = product.title.split()
        if len(title_words) >= 2:
            series_name = ' '.join(title_words[:2])
            if not any(s['name'] == series_name for s in series):
                count = products.filter(title__icontains=series_name).count()
                series.append({
                    'name': series_name,
                    'count': count
                })
    
    processors = []
    for category in categories:
        if 'processor' in category.name.lower() or 'chip' in category.name.lower():
            count = Product.objects.filter(category_id=category).count()
            processors.append({
                'name': category.name,
                'count': count
            })
    
    slovnik = {
        "products": products,
        "manufacturers": manufacturers_with_count,
        "categories": categories_with_count,
        "series": series,
        "processors": processors,
        "min_price": min_price_db,
        "max_price": max_price_db
    }
    return render(request, "all_products.html", context=slovnik)

def filter_by_series_func(request):
    series_names = request.POST.getlist("series_names")
    if series_names:
        query = Q()
        for series_name in series_names:
            query |= Q(title__icontains=series_name)
        products = Product.objects.filter(query)
    else:
        products = Product.objects.all()
    
    manufacturers = Manufacturer.objects.all()
    categories = Category.objects.all()
    
    if products.exists():
        min_price = min(product.price for product in products)
        max_price = max(product.price for product in products)
    else:
        min_price = 0
        max_price = 1000
    
    manufacturers_with_count = []
    for manufacturer in manufacturers:
        count = Product.objects.filter(manufacturer_id=manufacturer).count()
        manufacturers_with_count.append({
            'manufacturer': manufacturer,
            'count': count
        })
    
    categories_with_count = []
    for category in categories:
        count = Product.objects.filter(category_id=category).count()
        categories_with_count.append({
            'category': category,
            'count': count
        })
    
    series = []
    for product in products:
        title_words = product.title.split()
        if len(title_words) >= 2:
            series_name = ' '.join(title_words[:2])
            if not any(s['name'] == series_name for s in series):
                count = products.filter(title__icontains=series_name).count()
                series.append({
                    'name': series_name,
                    'count': count
                })
    
    processors = []
    for category in categories:
        if 'processor' in category.name.lower() or 'chip' in category.name.lower():
            count = Product.objects.filter(category_id=category).count()
            processors.append({
                'name': category.name,
                'count': count
            })
    
    slovnik = {
        "products": products,
        "manufacturers": manufacturers_with_count,
        "categories": categories_with_count,
        "series": series,
        "processors": processors,
        "min_price": min_price,
        "max_price": max_price
    }
    return render(request, "all_products.html", context=slovnik)

def filter_by_processor_func(request):
    processor_names = request.POST.getlist("processor_names")
    if processor_names:
        query = Q()
        for processor_name in processor_names:
            query |= Q(category_id__name__icontains=processor_name)
        products = Product.objects.filter(query)
    else:
        products = Product.objects.all()
    
    manufacturers = Manufacturer.objects.all()
    categories = Category.objects.all()
    
    if products.exists():
        min_price = min(product.price for product in products)
        max_price = max(product.price for product in products)
    else:
        min_price = 0
        max_price = 1000
    
    manufacturers_with_count = []
    for manufacturer in manufacturers:
        count = Product.objects.filter(manufacturer_id=manufacturer).count()
        manufacturers_with_count.append({
            'manufacturer': manufacturer,
            'count': count
        })
    
    categories_with_count = []
    for category in categories:
        count = Product.objects.filter(category_id=category).count()
        categories_with_count.append({
            'category': category,
            'count': count
        })
    
    series = []
    for product in products:
        title_words = product.title.split()
        if len(title_words) >= 2:
            series_name = ' '.join(title_words[:2])
            if not any(s['name'] == series_name for s in series):
                count = products.filter(title__icontains=series_name).count()
                series.append({
                    'name': series_name,
                    'count': count
                })
    
    processors = []
    for category in categories:
        if 'processor' in category.name.lower() or 'chip' in category.name.lower():
            count = Product.objects.filter(category_id=category).count()
            processors.append({
                'name': category.name,
                'count': count
            })
    
    slovnik = {
        "products": products,
        "manufacturers": manufacturers_with_count,
        "categories": categories_with_count,
        "series": series,
        "processors": processors,
        "min_price": min_price,
        "max_price": max_price
    }
    return render(request, "all_products.html", context=slovnik)

def save_to_session_func(request, id):
    request.session["item_" + str(id)] = str(id)


def get_watched_recently_from_session_func(request):
    session_data = dict(request.session)
    id_list = []
    for i, j in session_data.items():
        if "item_" in i:
            id_list.append(j)

    products = []
    for i in id_list:
        product = Product.objects.get(id = int(i))
        products.append(product)

    return products