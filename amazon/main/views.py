from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from main.models import *
from datetime import datetime
from userservice.views import *
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from deep_translator import GoogleTranslator
from main.translate_product import translate_product, translate_product_title, translate_product_description, translate_via_google_translate


def all_products_func(request):
    searching_name = request.GET.get("searching_name", "").strip()
    min_price_input = request.GET.get("min_price", "")
    max_price_input = request.GET.get("max_price", "")
    selected_manufacturers = request.GET.getlist("manufacturer_ids")
    selected_categories = request.GET.getlist("category_names")
    time_threshold = timezone.now() - timedelta(hours=48)
    sort_by = request.GET.get("sort_by", "by_new")


    products = Product.objects.filter(is_deleted=False).filter(Q(count__gt=0) | Q(out_of_stock_since__gte=time_threshold))

    translator = GoogleTranslator(source="auto", target="en")

    if searching_name:
        queries = Q()
        queries |= (
            Q(title__icontains=searching_name) | Q(description__icontains=searching_name) |
            Q(title_en__icontains=searching_name) | Q(description_en__icontains=searching_name) |
            Q(title_de__icontains=searching_name) | Q(description_de__icontains=searching_name) |
            Q(title_uk__icontains=searching_name) | Q(description_uk__icontains=searching_name)
        )

        words = searching_name.split()
        for word in words:
            if len(word) > 1:
                queries |= (
                    Q(title__icontains=word) | Q(description__icontains=word) |
                    Q(title_en__icontains=word) | Q(description_en__icontains=word) |
                    Q(title_de__icontains=word) | Q(description_de__icontains=word) |
                    Q(title_uk__icontains=word) | Q(description_uk__icontains=word)
                )

        search_products_result = products.filter(queries)

        if search_products_result.exists():
            products = search_products_result
        else:
            translated_name = translator.translate(searching_name)
            translated_queries = Q(
                Q(title__icontains=translated_name) | Q(description__icontains=translated_name) | Q(title_en__icontains=translated_name) | Q(description_en__icontains=translated_name)
            )

            translated_words = translated_name.split()
            for word in translated_words:
                if len(word) > 1:
                    translated_queries |= (
                        Q(title__icontains=word) | Q(description__icontains=word) | Q(title_en__icontains=word) | Q(description_en__icontains=word)
                    )

            products = products.filter(translated_queries)



    if selected_manufacturers:
        products = products.filter(manufacturer_id__in=selected_manufacturers)
    if selected_categories:
        products = products.filter(category_id__name__in=selected_categories)
    if min_price_input:
        products = products.filter(price__gte=min_price_input)
    if max_price_input:
        products = products.filter(price__lte=max_price_input)

    if sort_by == "most_viewed":
        products = products.order_by("-view_count")
    elif sort_by == "most_sold":
        products = products.order_by("-sold_count")
    else:
        sort_by = "by_new"
        products = products.order_by("-id")

    manufacturers = Manufacturer.objects.all().order_by("name")

    db_categories = Category.objects.all()
    def translate_category(category):
        return str(category.translated_name).lower()
    categories = list(db_categories)
    categories.sort(key=translate_category)

    per_page_param = request.GET.get("per_page", 60)
    try:
        products_per_page = int(per_page_param)
    except:
        products_per_page = 60

    paginator = Paginator(products, products_per_page)
    page_number = request.GET.get("page", 1)
    try:
        products_page = paginator.page(page_number)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = []

    slovnik = {
        "products": products_page,
        "manufacturers": manufacturers,
        "categories": categories,
        "min_price": min_price_input,
        "max_price": max_price_input,
        "recently_viewed_products": get_watched_recently_from_session_func(request),
        "selected_manufacturers": selected_manufacturers,
        "selected_categories": selected_categories,
        "searching_name": searching_name,
        "selected_sort": sort_by
    }
    return render(request, "all_products.html", context=slovnik)



@login_required(login_url='/login/')
def add_product_func(request):
    has_valid_payment = PaymentMethod.objects.filter(user=request.user, type__in=["by_card", "paypal"]).exists()

    if not has_valid_payment:
        #messages.warning(request, "Before adding a product, please link a payment method (Card/PayPal) to receive money!")
        return redirect('/add_payment_method/')

    if request.method == "POST":
        title = request.POST.get("title")
        price = request.POST.get("price")
        product_image = request.POST.get("product_image")
        description = request.POST.get("description")
        count = request.POST.get("count")
        status = request.POST.get("status")

        manufacturer_id = request.POST.get("manufacturer_id")
        category_id = request.POST.get("category_id")

        manufacturer = Manufacturer.objects.get(id=manufacturer_id)
        category = Category.objects.get(id=category_id)

        try:
            price = Decimal(price)
            if price < 0 or price > 99999999:
                messages.error(request, "Give a real price for this product!")
                return redirect(add_product_func)
        except Exception:
            messages.error(request, "Give a real price for this product!")
            return redirect(add_product_func)

        try:
            count = int(count)
            if count <= 0:
                messages.error(request, "Give the count that is bigger than 0!")
                return redirect(add_product_func)
        except Exception:
            messages.error(request, "Give the count that is bigger than 0!")
            return redirect(add_product_func)

        translated_data = translate_product(title=title, description=description)


        new_product = Product.objects.create(
            title=title,
            price=price,
            product_image=product_image,
            description=description,
            count=count,
            status=status,
            isavaible=True,
            manufacturer_id=manufacturer,
            category_id=category,
            user=request.user,
            **translated_data
        )

        gallery_text = request.POST.get("gallery_urls", "")
        urls_list = [url.strip() for url in gallery_text.split('\n') if url.strip()]

        for url in urls_list[:9]:
            ProductImage.objects.create(
                product=new_product,
                image_url=url
            )
        messages.success(request, "Your product was added successfully!")
        return redirect(my_products_func)

    manufacturers = Manufacturer.objects.all().order_by("name")

    db_categories = Category.objects.all()
    def translate_category(category):
        return str(category.translated_name).lower()
    categories = list(db_categories)
    categories.sort(key=translate_category)

    slovnik = {
        "manufacturers": manufacturers,
        "categories": categories
    }

    return render(request, "add_product.html", context=slovnik)


def add_manufacturer_func(request):
    if request.user.is_superuser:
        print("-------------------------------")
        print("Original: Продаю новий IPhone 18, недорого.")
        print("Translated: " + translate_via_google_translate("Продаю новий IPhone 18, недорого."))
        print("-------------------------------")
        if request.method == "POST":
            name = request.POST["name"]
            country = request.POST["country"]
            buisness_stream = request.POST["buisness_stream"]
            description = request.POST["description"]

            Manufacturer.objects.create(name = name, country = country, buisness_stream = buisness_stream, description = description)

        return render(request, "add_manufacturer.html")
    else:
        return redirect(all_products_func)

def add_category_func(request):
    if request.user.is_superuser:
        if request.method == "POST":
            name = request.POST["name"]

            Category.objects.create(name = name)


        return render(request, "add_category.html")
    else:
        return redirect(all_products_func)

def info_product_func(request, id):
    product = Product.objects.get(id=id)

    if request.user != product.user:
        ip_address = get_client_ip(request)
        time_threshold = timezone.now() - timedelta(minutes=5)

        validate_all_views(time_threshold)

        has_viewed_recently = ProductView.objects.filter(product=product, ip_address=ip_address, created_at__gte=time_threshold).exists()

        if not has_viewed_recently:
            ProductView.objects.create(product=product, ip_address=ip_address)
            product.view_count += 1
            product.save(update_fields=['view_count'])

    save_to_session_func(request, id)
    slovnik = {
        "product": product
    }

    return render(request, "info_product.html", context=slovnik)


def validate_all_views(time_threshold):
    ProductView.objects.filter(created_at__lte=time_threshold).delete()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_cart_func(request):
    if request.method == "POST":
        user = request.user
        Cart.objects.create(user=user)

    return render(request, "info_product.html")

def add_item_to_cart_func(request, id):
    if not request.user.is_authenticated:
        return redirect(login_func)
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        user = request.user

        if product.user == user:
            messages.error(request, "You cannot add your own product to the cart!")
            return redirect(request.META.get('HTTP_REFERER', all_products_func))

        if product.count <=0:
            messages.error(request, "This product is out of stock!")
            return redirect(request.META.get('HTTP_REFERER', all_products_func))

        cart, created = Cart.objects.get_or_create(user=user)
        product = Product.objects.get(id=id)

        cartitem, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            if cartitem.count + 1 > product.count:
                messages.warning(request, "Cannot add more. Stock limit reached!")
                return redirect(info_cart_func)
            cartitem.count += 1
            cartitem.save()
        else:
            cartitem.count = 1
            cartitem.save()

    return redirect(info_cart_func)


def info_cart_func(request):
    if not request.user.is_authenticated:
        return redirect(login_func)

    try:
        user = request.user
        cart, created = Cart.objects.get_or_create(user = user)
        cartitems = CartItem.objects.filter(cart = cart)
        print("Cart ID:", cart.id)
        print("Items:", cartitems)
        mainprice = 0

        list = []
        for i in cartitems:
            result = i.product.price * i.count
            list.append((i, result))
            mainprice += Decimal(i.product.price * i.count)
        slovnik = {
            "cartitems": list,
            "mainprice": mainprice
        }
        return render(request, "info_cart.html", context=slovnik)
    except Exception as e:
        print(f"Error in cart: {e}")



def add_item_plus_one_in_cart_func(request, id):
    if request.method == "POST":
        cartitem = CartItem.objects.get(id = id)
        if cartitem.count < cartitem.product.count:
            cartitem.count += 1
            cartitem.save()
    return redirect(info_cart_func)

def remove_item_minus_one_in_cart_func(request, id):
    if request.method == "POST":
        try:
            cartitem = CartItem.objects.get(id = id)
            cartitem.count -= 1

            if cartitem.count == 0:
                cartitem.delete()
            else:
                cartitem.save()

            return redirect(info_cart_func)

        except Exception as e:
            print(f"Error with minus 1 item in cart. Error: {e}")
            return redirect(info_cart_func)

def clear_cart_func(request):
    if request.method == "POST":
        try:
            clear_cart(request.user)
        except Exception as e:
            print(f"Error with clearing cart. Error: {e}")

    return redirect(info_cart_func)

def clear_cart(user):
    cart = Cart.objects.get(user = user)
    cartitems = CartItem.objects.filter(cart = cart)
    for cartitem in cartitems:
        cartitem.delete()

from django.db import transaction
from datetime import datetime


def confirm_order_func(request):
    if request.method == "POST":
        with transaction.atomic():
            if request.POST.get("card_number") != "":
                cardnumber = request.POST.get("card_number")
                cardexpiry = request.POST.get("card_expiry")
                cardcvc = request.POST.get("card_cvc")
                cardname = request.POST.get("card_name")
                user = request.user

                paymentmethod_search = PaymentMethod.objects.filter(card_number=cardnumber, card_expiry=cardexpiry, card_cvc=cardcvc, card_name=cardname, type="by_card", user=user)
                if paymentmethod_search.exists():
                    paymentmethod = list(paymentmethod_search)[0]
                else:
                    paymentmethod = PaymentMethod.objects.create(card_number = cardnumber, card_expiry = cardexpiry, card_cvc = cardcvc, card_name = cardname, type = "by_card", user = user)
                    paymentmethod.save()

            elif request.POST.get("email") != "":
                email = request.POST.get("email")
                user = request.user

                paymentmethod_search = PaymentMethod.objects.filter(email=email, user=user, type="paypal")
                if paymentmethod_search.exists():
                    paymentmethod = list(paymentmethod_search)[0]
                else:
                    paymentmethod = PaymentMethod.objects.create(email = email, user = user, type = "paypal")
                    paymentmethod.save()

            else:
                user = request.user

                paymentmethod_search = PaymentMethod.objects.filter(user=user, type="cash")
                if paymentmethod_search.exists():
                    paymentmethod = list(paymentmethod_search)[0]
                else:
                    paymentmethod = PaymentMethod.objects.create(user = user, type = "cash")
                    paymentmethod.save()

            cart = Cart.objects.get(user = request.user)

            cartitems = CartItem.objects.filter(cart = cart)
            if not cartitems.exists():
                return redirect(info_cart_func)

            order = Order.objects.create(user = request.user, paymentmethod = paymentmethod, status = "In process", date_of_create = datetime.now())
            order.save()


            for cartitem in cartitems:
                if cartitem.count > cartitem.product.count:
                    return redirect(info_cart_func)

                orderitem = OrderItem.objects.create(order=order, product=cartitem.product, count=cartitem.count, price_at_purchase=cartitem.product.price, product_title=cartitem.product.title)
                orderitem.save()

                product = cartitem.product
                product.count -= cartitem.count
                product.sold_count += cartitem.count

                if product.count <= 0:
                    product.isavaible = False

                product.save()

            clear_cart(request.user)

            return redirect(all_orders_func)

@login_required(login_url="/login/")
def all_orders_func(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by("-id")
    orderdictionary = {}

    for i in orders:
        orderitems = OrderItem.objects.filter(order=i)
        orderscortage = []
        totalprice = 0

        for j in orderitems:
            item_price = getattr(j, "price_at_purchase", j.product.price)
            subtotal = item_price * j.count
            totalprice += subtotal
            orderscortage.append((j, subtotal))

        orderdictionary[i] = (orderscortage, totalprice)

    return render(request, "all_orders.html", {"orders": orderdictionary})


def delete_all_orders_func(request):
    Order.objects.all().delete()
    return redirect(all_products_func)

def filter_by_manufacturer_func(request):
    searching_name = request.POST.get("searching_name")
    manufacturer_ids = request.POST.getlist("manufacturer_ids")

    products = Product.objects.all()
    if searching_name:
        products = products.filter(Q(title__icontains=searching_name) | Q(description__icontains=searching_name))

    products = products.filter(manufacturer_id__in=manufacturer_ids)

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
        "max_price": max_price,
        "searching_name": searching_name
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
    searching_name = request.POST.get("searching_name")
    min_price = float(request.POST.get("min_price", 0))
    max_price = float(request.POST.get("max_price", 1000))

    products = Product.objects.all()
    if searching_name:
        products = products.filter(Q(title__icontains=searching_name) | Q(description__icontains=searching_name))

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
        "max_price": max_price_db,
        "searching_name": searching_name
    }
    return render(request, "all_products.html", context=slovnik)

def filter_by_series_func(request):
    searching_name = request.POST.get("searching_name")
    series_names = request.POST.getlist("series_names")

    products = Product.objects.all()
    if searching_name:
        products = products.filter(Q(title__icontains=searching_name) | Q(description__icontains=searching_name))

    if series_names:
        query = Q()
        for series_name in series_names:
            query |= Q(title__icontains=series_name)
        products = products.filter(query)


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
        "max_price": max_price,
        "searching_name": searching_name
    }
    return render(request, "all_products.html", context=slovnik)

def filter_by_processor_func(request):
    searching_name = request.POST.get("searching_name")
    processor_names = request.POST.getlist("processor_names")

    products = Product.objects.all()

    if searching_name:
        products = products.filter(Q(title__icontains=searching_name) | Q(description__icontains=searching_name))

    if processor_names:
        query = Q()
        for processor_name in processor_names:
            query |= Q(category_id__name__icontains=processor_name)
        products = productsfilter(query)


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
        "max_price": max_price,
        "searching_name": searching_name
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
        product = Product.objects.filter(id=int(i)).first()

        if product is not None:
            products.append(product)

    return products


def search_products_func(request):
    searching_name = request.GET.get("searching_name")
    products = Product.objects.all()

    if searching_name:
        products = products.filter(Q(title__icontains=searching_name) | Q(description__icontains=searching_name))

    slovnik = {
        "products": products,
        "searching_name": searching_name
    }

    return render(request, "all_products.html", context=slovnik)


@login_required(login_url='/login/')
def add_payment_method_func(request):
    if request.method == 'POST':
        # if card
        if request.POST.get("card_number"):
            PaymentMethod.objects.create(
                user=request.user,
                type="by_card",
                card_number=request.POST.get('card_number'),
                card_expiry=request.POST.get('card_expiry'),
                card_cvc=request.POST.get('card_cvc'),
                card_name=request.POST.get('card_name')
            )
        # if paypal
        elif request.POST.get("email"):
            PaymentMethod.objects.create(
                user=request.user,
                type="paypal",
                email=request.POST.get('email')
            )

        messages.success(request, "Payment method linked successfully! You can now list your products.")
        return redirect(add_product_func)

    return render(request, 'add_payment_method.html')


@login_required(login_url="/login/")
def my_products_func(request):
    user_products = Product.objects.filter(user = request.user, is_deleted=False).order_by("-id")

    slovnik = {
        "products": user_products
    }

    return render(request, "my_products.html", context=slovnik)



@login_required(login_url="/login/")
def edit_product_func(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.user != request.user:
        messages.error(request, "You can only edit your own products!")
        return redirect(my_products_func)

    if request.method == "POST":
        old_title = product.title
        old_description = product.description

        product.title = request.POST.get("title")
        product.description = request.POST.get("description")

        if old_title != request.POST.get("title") and old_description != request.POST.get("description"):
            translated_data = translate_product(title=request.POST.get("title"), description=request.POST.get("description"))

            product.title_en = translated_data["title_en"]
            product.description_en = translated_data["description_en"]
            product.title_de = translated_data["title_de"]
            product.description_de = translated_data["description_de"]
            product.title_uk = translated_data["title_uk"]
            product.description_uk = translated_data["description_uk"]

        elif old_title != request.POST.get("title"):
            translated_data = translate_product_title(title=request.POST.get("title"))

            product.title_en = translated_data["title_en"]
            product.title_de = translated_data["title_de"]
            product.title_uk = translated_data["title_uk"]

        elif old_description != request.POST.get("description"):
            translated_data = translate_product_description(title=request.POST.get("title"))

            product.title_en = translated_data["title_en"]
            product.title_de = translated_data["title_de"]
            product.title_uk = translated_data["title_uk"]

        product.price = request.POST.get("price")
        product.count = request.POST.get("count")

        if old_description != request.POST.get("description"):
            product.description = request.POST.get("description")

        new_image = request.POST.get("product_image")

        if new_image:
            product.product_image = new_image

        if int(product.count) > 0:
            product.isavaible = True
        else:
            product.isavaible = False

        product.save()

        additional_images_text = request.POST.get("additional_images", "")
        ProductImage.objects.filter(product=product).delete()

        if additional_images_text:
            urls = additional_images_text.split('\n')
            for url in urls:
                clean_url = url.strip()
                if clean_url:
                    ProductImage.objects.create(product=product, image_url=clean_url)

        messages.success(request, "Product updated successfully!")
        return redirect(my_products_func)

    additional_images = ProductImage.objects.filter(product=product)
    additional_images_urls = "\n".join([i.image_url for i in additional_images])

    slovnik = {
        "product": product,
        "additional_images_urls": additional_images_urls
    }

    return render(request, "edit_product.html", context=slovnik)



@login_required(login_url="/login/")
def delete_product_func(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)

        if product.user == request.user or request.user.is_superuser:
            product.delete()
            messages.success(request, "The product was successfully deleted!")

            if product.user == request.user:
                return redirect(my_products_func)
            elif request.user.is_superuser:
                return redirect(all_products_func)

        else:
            messages.error(request, "You don't have permission to delete this product!")
            return redirect(all_products_func)

    return redirect(my_products_func)
