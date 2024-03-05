# Introduction

A Django project will more often than not have more than one app. For instance in an e-commerce project you might have an app for user management, an orders app, a products app, a payments app and so on. This way each app will be solely focused on a specific function, but at the end of the day, all these apps should work in concert to make the e-commerce project a whole, therefore, one or more apps might be interested in knowing when a particular event takes place in another app. For instance the product app might be interested in knowing when a user confirms an order, this will enable the product app to update the inventory, but how will the product app know when a user places an order yet they are two separate applications?, to solve this, the Django framework avails a signal dispatcher. Using this framework the orders app will send a signal once an order has been saved, and the products app upon the receipt of this information it will update the inventory accordingly. So the signalling framework allows for the applications in one project to be decoupled, enabling them to communicate with each other without being tightly dependent.

This tutorial will take you through the basics of Django signals, how they enable maintenance of modular and scalable codebase, you will cover some of the built-in signals, also look at how you can define custom signals.

## Understanding signals

### What are signals?

Signals in Django are a notification system that allows certain `senders` to notify a set of `receivers` when certain actions take place. They help decoupled applications get notified when particular actions or events take place elsewhere in the framework. In the context of our example, the orders app will `send` a signal upon the confirmation of an order and since the products app is interested in this event it will have registered to `receive` it, then it will take some action upon the receipt.

### How signals work in Django

Signals work similar to the pub-sub pattern, this is where the sender of the signal is the publisher and the receiver of the signal is the subscriber. This means that for a receiver to receive a signal they must have subscribed in this case registered to receive the signal.

### Signal senders and receivers

A signal sender is any Python object that emits a signal, while a receiver is any Python function or method that gets executed in response to the signal being sent. It is also important to note that some signals especially the built-in signals are always sent out whether there is a registered receiver or not. In our example the orders app will be the sender of the signal and the products app will be the receiver of the signal.

## Setting up a Django project

To demonstrate how signals work, let's implement a sample project by following the steps below:

### Create the project directory

```bash
mkdir my_shop
```

This will create a directory named `my_shop` it is going to hold the e-commerce project.

### Create and activate a virtual environment

A virtual environment is an isolated Python environment that allows you to install the dependencies of a project without affecting the global Python environment, this means you can have different projects running in one machine each with it's own depencies and possibly running on different versions of Django.

To create a virtual environment, you will use the `virtualenv` package, it is not part of the standard Python library, install it with the following command:

```bash
pip install virtualenv
```

Upon installation of the package, to create a virtual environment for this project you have to get into the `my_shop` directory:

```bash
cd my_shop
```

Create a virtual environment using the following command:

```bash
virtualenv venv
```

The above command creates a virtual environment named `venv`, having created it, you have to activate it to use it:

For Linux / MacOS

```bash
. venv/bin/activate 
```

For Windows

```bash
. venv\Scripts\activate
```

### Install Django and other dependencies

Once the virtual environment is active, you can install Django and other dependencies the project might need, but for this demonstration you just need Django:

```bash
pip install Django
```

### Creating the project

Upon successful installation of Django, create a project and name it `my_shop` just similar to the project holder, you created above:

```bash
django-admin startproject my_shop .
```

The above command creates a Django project name it `my_shop` and the dot at the end indicates that you wish to create the project in the current directory, without creating extra directories.

### Creating the individual apps

Create two apps, that is the `products` app and the `orders` app. First create the `products` app, it will be created with the default files for any Django app:

```bash
python manage.py startapp products
```

Add the products app to the installed apps of the project, open the `my_shop` directory then go to `settings.py` file and go to the `INSTALLED_APPS`  setting, and add the following line of code at the bottom.

```python
INSTALLED_APPS = [
    # other installed apps
    'products.apps.ProductsConfig',
]
```

That setting registers the `products` app with the project and that will enable you to run migrations that will create the database tables.

Then create the `orders` app:

```bash
python manage.py startapp orders
```

As you did for the `products` app, add the `orders` app to the `INSTALLED_APPS` setting too. Open the `settings.py` file and add the following line of code at the bottom.

```python
INSTALLED_APPS = [
    # other installed apps
    'orders.apps.OrdersConfig',
]
```

### Defining the models for the apps

This demonstration will involve changing and updating some values in the database, to indicate some state changes, which eventually leads to some events taking place, and for that you will need to define models for the two apps. Let's define the models for the `products` app first. Open the `products` app and go to the `models.py` file and put in the following block of code:

```python
# products/models.py

from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
```

The above code defines a product model that will be mapped to a products table in the database, it has a few fields, which are quite descriptive.

Next define the `orders` models. Open the `orders` app and put in the following code to the  `models.py` file.

```python
# orders/models.py

from django.db import models
from products.models import Product

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    confirmed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Calculate total_price before saving the order
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

```

Having defined the models, you have to run migrations, this will create the tables in the database. The Django ORM  avails various database management commands, but for now you will use the two that are used to prepare the database tables.

Before running the migrations to create the two new models, upto this point you have not run the project to test if it is setup correctly, run it using the following command:

```bash
python manage.py runserver
```

The above command fires up the development server, and if everything is setup correctly, you should have an output similar to the one below:

```output
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).

You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
January 15, 2024 - 11:22:19
Django version 5.0.1, using settings 'sitepoint_django_signals_tutorial.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

If you have similar output, that means the project is configured properly and you have a basic Django project running, if you have an error, kindly refer to community with any questions that you might be having.

While still on the output, I want to bring your attention to the fourth line which starts with, "You have 18 unapplied migrations". Django being a battries included framework, if you choose to use a database for your project, the framework will create some tables meant for management and that is what that warning is, it means that you have not created the Django management tables.

To create them run the following command:

```bash
python manage.py migrate
```

Running that command creates, quite a number of tables, what you might be wondering is, where are the tables being created and yet you have not set up a database for use in your project?, Django ships with SQLite3 preconfigured by default. Therefore, you don't need to do any configuration for your project to work with SQLite.

Now that the Django management tables have been created, you have to create the tables for the `products` and `orders` apps, to do that you will need two sets of commands, and this is the format followed everytime you want to create a new table for newly defined model. The first command converts or maps your model class definition to the SQL needed to create the database tables and the command is `makemigrations`:

```bash
python manage.py makemigrations
```

Running that command without specifying any app, creates migrations for all apps. The next thing is to apply the migrations, which eventually creates the tables, for that use the following command:

```bash
python manage.py migrate
```

The above command creates the tables for two apps that you have in this sample application.

## Basics of Django signals

In this section, let's delve into the fundamentals of Django signals, you will see the steps you need to follow to get signals working in your application. You will do that by making incremental changes in the project you have just set-up.

### Importing necessary modules

To get signals to work in your project, it is essential to import the required modules. For a start let's import the `Signal` and `receiver` from the `django.dispatch` module. The `Signal` class is used to create a signal instance, especially if you want to create custom signals. In the sample project, in the `orders` app you are only going to import the `Signal` class while the `receiver` module will be imported in the `products` app. The `receiver` module avails the `receiver` decorator, which connects the signal handler to the signal sender.

While the `django.dispatch` module, serves as the core module for defining custom signals, Django offers built-in signals which are accessible through other modules, you will cover them in more details in the built-in signals section.

Using the sample project, let's show how you could add the signals functionality. The Django documentation recommends that you create a `signals.py` file that will contain all the code for the signals. In the  root of the `products`  and `orders` app, create a file and name it `signals.py`.

#### Creating a signal instance

In the `orders` app, open the `signals.py` file and put in the following code:

```python
# orders/signals.py

from django.dispatch import Signal

# create a signal instance for order confirmation
order_confirmed = Signal()
```

The above code creates an `order_confirmed` signal that will be sent when an order is confirmed, albeit manually.

### Connecting signals in `apps.py`

So as to make the signal sending and receipt functionality available throughout the lifecycle of the application, you have to connect the signals in the app configuration file. You are going to do this for both applications. Start with the `orders` app then proceed to the `products` app. Open the `orders` app then go to the `apps.py` file, update the `OrdersConfig` class with the following method:

```python
# orders/apps.py

def ready(self):
    import orders.signals
```

The `ready()` method, is a built-in method of the `AppConfig` class that is extended by the configuration classes of the particular app that you are working with. In this particular case the `OrdersConfig` extends it, and hence the methods, including `ready()`, are available for it to extend and override. Therefore, overriding the method in this case sets signals to be sent when the app is fully loaded.

Next step is to connect the signals in the `products` app, open it and go the `apps.py` file and put in the following block of code:

```python
# products/apps.py

def ready(self):
    import products.signals
```

This addition in both apps, ensures that signals will be sent when the request response cycle begins.

### Creating a signal sender

Django provides two methods to enable signal sending, you can use the `Signal.send()` or the `Signal.send_robust()` their difference being that the `send()` method does not catch any exceptions raised by receivers.

To send a signal the method takes the following format.

```python
Signal.send(sender, **kwargs)
```

`Signal` being somewhat of a placeholder to mean the sending signal for instance `order_confirmed.send()`, while the `sender` argument could be the app sending the signal or a model or someother part of the framework that can send signals. The sender in our example will be the instance of the order that has just been confirmed like this `sender=order`.

Let's see how to use the `order_confirmed` signal in our sample application. Since you want to send the signal upon the confirmation of an order, in the view that will handle order processing that is where you want send the signal from once a user confirms their order. So open the `orders` app the `views.py` and put in the following block of code:

```python
# orders/views.py

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.dispatch import receiver
from orders.models import Order


def confirm_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        
        # Perform order confirmation logic here
        
        # Send the order_confirmed signal
        # the sender of the signal is the order that just been confirmed
        order_confirmed.send(sender=order)
        
        return HttpResponse(f"Order {order_id} confirmed successfully.")
    else:
        return HttpResponse("Invalid request method. Use POST to confirm the order.")

```

### Connecting a signal handler (receiver)

A signal handler is a function that gets executed when an associated signal is sent. Django provides two ways of connecting a handler to a signal sender. You can connect the signal manually or you can use the `receiver` decorator.

#### Manual connection

If you choose to do it manually, you can do it this way:

```python
# products/signals.py

from orders.signals import order_confirmed

order_confirmed.connect(<the_signal_handler_function>)
```

#### Using the decorator

Using the `@receiver` decorator, you are able to associate a signal sender with a particular signal handler, let
s use this method. Create a function that will update the inventory when the `order_confirmed` signal is sent. This handler will be in `products` app, open the  `products/signals.py` file and put it the following code:

```python
# products/signals.py

from django.dispatch import receiver
from orders.signals import order_confirmed

@receiver(order_confirmed)
def update_quantity_on_order_confirmation(sender, **kwargs):
    """
    Signal handler to update the inventory when an order is confirmed.
    """
    # Retrieve the associated product from the order
    product = sender.product

    # Update the inventory
    product.quantity -= sender.quantity
    product.save()

    print(f"Quantity updated for {product.name}. New quantity: {product.quantity}")

```

The handler function should always take in a `sender` and `**kwargs` arguments. Django will throw an error if you write the function without the `**kwargs` arguments. That is a pre-emptive measure to ensure your handler function is able to handle arguments in future if they arise.

## Built-in signals in Django

### Overview of some commonly used built-in signals

Django ships with some built-in signals for various use cases, it has signals sent by the model system, it has signals sent by django-admin, it has signals sent during the request / response cycle, it has signals sent by database wrappers, there are also signals sent when running tests.

### Model signals

Model signals are signals sent by the model system, these are signals sent when various events take place or are about to take place in your models. You can access the signals this way `django.db.models.signals.<the_signal_to_use>`

#### pre_save

This signal is sent at the beginning of the model `save()` method, it sends various arguments with it, the `sender` this is the model class sending the signal, `instance` this is the actual instance being saved, `raw` this is a boolean value which is True if the model is saved exactly as presented.

#### post_save

This signal is sent at the end of model `save()` method. This is a particularly useful signal and it can be used in various cases,
for example in the `my_shop` project, you can also use it to notify the `products` app upon the confirmation of an order. Similar to the `pre_save` signal it also sends some arguments along, that is the `sender`, `instance`, `created`, `raw`, `using` and `update_fields.` most of these arguments are optional but understanding the effects of their usage goes a long way in ensuring that you use signals correctly in your application.

### Request / response signals

These are signals that are sent out by the core framework during the request/response cycle. You can access the signals this way `django.core.signals.<the_signal>`.

#### request_started

This signal is sent when Django starts processing a request.

#### request_finished

This signal is sent when Django finishes sending a HTTP response to a client.

The framework avails quite a number of built-in signals for use, learn more about them in the documentation link shared at the end of this tutorial.

### How to use built-in signals in your project

Using built-in signals in your project is not so different from using custom signals, then only differentiating thing is that you will not need to manually initialize sending the signal since it is sent out automatically by the framework whether there is a receiver registered or not. In other words, you don't have to explicitly call a methods like `Signal.send()` to trigger built-in signals, Django takes care of that.

For instance, let's see how you could utilize the `post_save` to demonstrate order confirmation and update of the inventory. In the `products/signal.py`  file update the code and put in the following block of code:

```python

# products/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order

@receiver(post_save, sender=Order)  # Connect to the built-in post_save signal
def update_quantity_on_order_confirmation(sender, instance, created, **kwargs):
    # This function will be called automatically after Order model instance is saved
    if created:
        # Perform actions for newly created instances
        product = instance.product

        # Update the inventory
        product.quantity -= instance.quantity
        product.save()

    else:
        # Perform actions for updated instances
```

The above code imports the `post_save` signal from the `models.signals`, it also imports the `receiver` module from `django.dispatch` and finally the `Order` model from the orders app.

In the `@receiver` decorator apart from including the `post_save` signal as the sender, you also include the model from which you want to listen for signals from, the reason for this is that all models in your project will emit the `post_save` signal so you want to be specific as to which model you are listening to signals from.

In the handler function, bring your attention to the fact that updating the inventory will only happen if the `created` option is True, the reason for this is that `post_save` signal is sent for new order creation instances and updates to orders so you want to update the inventory when a new order is created.

In the `orders` app you will update the `confirm_order` view and do away with the part where you send the signal manually since the `post_save` signal will be sent automatically by the `Order` model class.

## Practical examples

While you have seen the usage of signals to confirm an order there is quite a number of different ways that signals can be used in your projects, let's see a few examples.

### Example 1: Using signals for automatic customer profile creation

To expand on the e-commerce project, you could have an app for account management, this is where you create various accounts for users in your system where you will have adminstrative users, and other users like customers, you could set up your system in way users who signup to your system in the frontend will be customers and you could have another way of creating superusers of your system. So in this case you could also have app for customer management but you want a customer to be created upon signing up.

This way the accounts management app will be responsible for accounts creation and once an account is created for a user then a customer profile will be automatically created for them.

Let's see an example:

```python

# customers/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from customers.models import Customer

@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)
```

In this code example, a signal is employed to automatically create a customer profile whenever a new user is registered. The `create_customer_profile` function is connected to the `post_save` signal for the `User` model using the `@receiver` decorator. When a new user instance is created (as indicated by the created flag), the function generates a corresponding customer profile by utilizing the `Customer` model's manager to create an instance with a reference to the newly registered user. This approach streamlines the process of associating customer profiles with new user registrations, enhancing the efficiency and maintainability of the application's user management system.

### Example 2: Triggering email notifications with signals

In this use case, you could have a blogging application and you want the authors to be notified through an email when a reader leaves a comment  for them on their blog.

Let's see an example:

```python
# blog/signals.py
# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from blog.models import Comment

@receiver(post_save, sender=Comment)
def send_comment_notification(sender, instance, created, **kwargs):
    if created:
        subject = 'New Comment Notification'
        message = 'A new comment has been posted on your blog.'
        from_email = 'your@example.com'
        recipient_list = [instance.blog.author.email]

        send_mail(subject, message, from_email, recipient_list)


```

The above code utilizes signals to trigger an email notification when a new comment is posted on a blog. The `send_comment_notification` function is connected to the `post_save` signal for the `Comment` model, ensuring its execution upon each save. The function checks if the comment is newly created (not updated) and, if so, constructs an email notification with a predefined subject and message. The email is sent to the author of the blog to notify them of the new comment. This approach enables automatic and real-time email notifications for blog authors, enhancing user engagement and interaction with the platform.

## Conclusion

In this tutorial we have covered signals in Django, what they are and how to use them, we have also looked at how to define custom signals, built-in signals and a few real world use cases of signals. Let's recap the key takeways from this tutorial.

### Recap of key concepts covered in the tutorial

#### What are signals

We have seen that signals are a communication mechanism between different parts of a Django project and that they enable components to send notifications to trigger actions in response to events.

#### How to set-up a Django project

We have looked and the process of creating a new Django project, setting up apps within the project, and defining models for the apps.

#### Basics of signals in Django

We have explored the how to get signals working in any project, the modules needed to be imported, how to create a signal instance, we have defined signal handlers and connected signals in the various apps.

#### Various built-in signals in Django

We have looked at the various built-in signals that Django offers, how you can use them in your project and looked at how you can customize some of them by connecting to specific senders in the case that a signal is sent by different senders.

#### Real world use cases

We have illustrated real-world use cases, the likes of automatic profile creatin, triggering email notifications.

#### Resources for further learning

You can dive deeper into signals by looking at the following resources

- [Django documenation on signals](https://docs.djangoproject.com/en/5.0/ref/signals/)
