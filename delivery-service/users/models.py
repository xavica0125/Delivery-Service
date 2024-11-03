from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from djmoney.models.fields import MoneyField


# Create your models here.

"Abstract User Profile class for both customer and driver to inherit from."


class UserProfile(models.Model):

    class Meta:
        abstract = True

    phone_number = PhoneNumberField()


"""Model stores pickup/delivery location physical address."""


class Address(models.Model):
    street_address = models.CharField(
        max_length=50,
    )
    sub_premise = models.CharField(max_length=50, blank=True)
    city = models.CharField(
        max_length=50,
    )
    state = models.CharField(max_length=2, default="TX", blank=True)
    zip_code = models.PositiveIntegerField()
    associated_customer = models.ForeignKey(
        "Customer", on_delete=models.CASCADE, related_name="addresses"
    )

    def __str__(self):
        return f"{self.street_address} {self.sub_premise}, {self.city}, {self.state} {self.zip_code}"


"""Customer model that holds relevant information. Relationship with User model is defined as OneToOneField using user_id as the primary key/foreign key."""


class Customer(UserProfile):
    class Meta:
        permissions = [
            ("can_place_delivery", "Can place delivery orders"),
        ]

    class ContactChoice(models.TextChoices):
        MOBILE = "Phone Call"
        EMAIL = "Email"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    notification_preference = models.CharField(max_length=15, choices=ContactChoice)
    date_created = models.DateTimeField(auto_now_add=True)
    default_pickup_address = models.OneToOneField(
        Address, on_delete=models.CASCADE, null=True
    )


"""Driver model that holds relevant information. Relationship with User model is defined as OneToOneField using user_id as the primary key/foreign key."""


class Driver(UserProfile):
    class Meta:
        permissions = [
            ("can_deliver", "Can deliver orders"),
        ]

    class Vehicle(models.TextChoices):

        PICKUP = "Pickup Truck"
        HEAVY_DUTY = "Heavy Duty Pickup"
        STATE_TRUCK = "State Truck"
        VAN = "Van"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_number = models.PositiveIntegerField()
    license_expiration_date = models.DateField()
    vehicle_type = models.CharField(max_length=17, choices=Vehicle)
    date_created = models.DateTimeField(auto_now_add=True)


"""Order model used to represent orders places by customers and delivered by drivers."""


class Order(models.Model):
    class TimeWindow(models.TextChoices):
        ONE_HOUR = "1 Hour"
        TWO_HOUR = "2 Hour"
        FOUR_HOUR = "4 Hour"

    class Status(models.TextChoices):
        PENDING = "Pending"
        EN_ROUTE = "En Route"
        DELIVERED = "Delivered"
        REFUSED = "Refused"

    control_number = models.BigAutoField(primary_key=True)
    weight = models.PositiveIntegerField()
    time_window = models.CharField(
        max_length=15, choices=TimeWindow, default=TimeWindow.TWO_HOUR
    )
    content = models.TextField(max_length=500)
    total_amount = MoneyField(max_digits=6, decimal_places=2, default_currency="USD")
    time_created = models.DateTimeField(auto_now_add=True)
    time_picked_up = models.DateTimeField(null=True)
    time_delivered = models.DateTimeField(null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_status = models.CharField(max_length=15, choices=Status)
    reason_for_refusal = models.TextField(max_length=200, blank=True)
    pickup_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, related_name="pickup_orders"
    )
    delivery_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, related_name="delivery_orders"
    )


"""Model that stores reference numbers used by customers and are associated via foreign key with the Order model's primary key."""


class ReferenceNumber(models.Model):
    ref_number = models.PositiveBigIntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)


"""Model that stores delivery location's information for each customer."""


class Location(models.Model):
    location_name = models.CharField(
        max_length=15,
    )
    poc_name = models.CharField(
        max_length=15,
    )
    poc_phone_number = PhoneNumberField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
