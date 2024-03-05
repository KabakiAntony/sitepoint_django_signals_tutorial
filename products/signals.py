from products.models import Product
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

    print(
        f"Quantity updated for {product.name}. New quantity: {product.quantity}")
