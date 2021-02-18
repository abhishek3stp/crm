from django.shortcuts import render, redirect

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.contrib import messages

from .models import *
from .forms import OrderForm, CreateUserForm, CustomerForm
from .filters import OrderFilter
from .decorators import unauthenticated_user, allowed_users, admin_only


# Registration handle
@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)

        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, username + '\'s account created')
            return redirect('login')

    context = {'form': form}
    return render(request, 'account/register.html', context)


# Login handle
@unauthenticated_user
def loginPage(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        else:
            messages.info(request, 'Incorrect credentials')

    return render(request, 'account/login.html')


# Logout handle
def logoutUser(request):
    logout(request)
    return redirect('login')


# User page
@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders = request.user.customer.order_set.all()
    total_order = orders.count()
    pending_order = orders.filter(status="Pending").count()
    delivered_order = orders.filter(status="Delivered").count()

    parms = {'orders': orders, 'total_order': total_order, 'pending_order': pending_order, 'delivered_order': delivered_order}

    return render(request, 'account/user.html', parms)


# Account settings
@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()

    parms = {'form': form}
    return render(request, 'account/account_settings.html', parms)


# Admin page
@login_required(login_url='login')
@admin_only
def dashboard(request):
    customers = Customer.objects.all()
    orders = Order.objects.all()

    total_order = orders.count()
    pending_order = orders.filter(status="Pending").count()
    delivered_order = orders.filter(status="Delivered").count()

    parms = {'customers': customers, 'orders': orders, 'total_order': total_order, 'pending_order': pending_order, 'delivered_order': delivered_order}

    return render(request, 'account/dashboard.html', parms)


# Particular customer page
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, slug):
    customer = Customer.objects.get(id=slug)
    orders = customer.order_set.all()
    order_count = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    parms = {'customer': customer, 'orders': orders, 'order_count': order_count, 'myFilter': myFilter}

    return render(request, 'account/customer.html', parms)


# Create orders for a customer
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, slug):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status', 'note'), extra=5)
    customer = Customer.objects.get(id=slug)

    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)

    if request.method == 'POST':
        formset = OrderFormSet(request.POST, instance=customer)

        if formset.is_valid():
            formset.save()
            return redirect('dashboard')

    parms = {'form': formset}
    return render(request, 'account/order_form.html', parms)


# Update orders for a customer
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, slug):
    order = Order.objects.get(id=slug)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)

        if form.is_valid():
            form.save()
            return redirect('dashboard')
    
    parms = {'form': form}
    return render(request, 'account/order_form.html', parms)


# Delete orders for a customer
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, slug):
    order = Order.objects.get(id=slug)
    order.delete()
    return redirect('dashboard')


# Product page
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def product(request):
    products = Product.objects.all()
    parms = {'products': products}
    return render(request, 'account/product.html', parms)
