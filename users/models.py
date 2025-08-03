from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from djmoney.models.fields import MoneyField
from decimal import Decimal
from django.conf import settings

# Create your models here.

"Abstract User Profile class for both customer and driver to inherit from."


class UserProfile(models.Model):

    class Meta:
        abstract = True

    phone_number = PhoneNumberField(null=True)


"""Model stores pickup/delivery location physical address."""


class Address(models.Model):
    location_name = models.CharField(
        max_length=50,
    )
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
    latitude = models.CharField(max_length=50)
    longitude = models.CharField(max_length=50)
    place_id = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.street_address} {self.sub_premise}, {self.city}, {self.state} {self.zip_code} ({self.location_name})"


"""Customer model that holds relevant information. Relationship with User model is defined as OneToOneField using user_id as the primary key/foreign key."""


class Customer(UserProfile):
    class Meta:
        permissions = [
            ("can_place_delivery", "Can place delivery orders"),
        ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
    total_amount = models.DecimalField(max_digits=19, decimal_places=4)
    time_created = models.DateTimeField(auto_now_add=True)
    time_picked_up = models.DateTimeField(null=True)
    time_delivered = models.DateTimeField(null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True)
    order_status = models.CharField(
        max_length=15, choices=Status, default=Status.PENDING
    )
    reason_for_refusal = models.TextField(max_length=200, blank=True, null=True)
    pickup_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, related_name="pickup_orders"
    )
    delivery_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, related_name="delivery_orders"
    )
    contact = models.ForeignKey("Contact", on_delete=models.CASCADE)

    def calculate_price(self, distance, length: bool):
        fuel_price_object = FuelPrice.objects.latest("date_created")
        distance = Decimal(float(distance) * 0.000621371)
        time_window_price = self.get_time_window_price()
        total_price = None

        if self.weight >= 1000 or length:
            total_price = self.calculate_delivery_fee(
                distance,
                fuel_price_object.diesel_price,
                time_window_price,
                avg_mpg=settings.AVG_MPG_HEAVY_DUTY,
                wear_and_tear=settings.WEAR_AND_TEAR_HEAVY_DUTY,
            )
        else:
            total_price = self.calculate_delivery_fee(
                distance,
                fuel_price_object.gas_price,
                time_window_price,
                avg_mpg=settings.AVG_MPG_PICKUP,
                wear_and_tear=settings.WEAR_AND_TEAR_PICKUP,
            )

        return total_price

    def calculate_delivery_fee(
        self,
        distance,
        latest_gas_price,
        time_window_price,
        avg_mpg=None,
        wear_and_tear=None,
    ):
        total_price = Decimal(
            ((latest_gas_price / Decimal(avg_mpg)) * distance)
            + (Decimal(self.weight) * Decimal(0.10))
            + (Decimal(wear_and_tear) * distance)
            + Decimal(20)
            + time_window_price
            + Decimal((100 * 0.30))
        )

        return total_price

    def get_time_window_price(self):
        time_window_price = None
        match self.time_window:
            case "1 Hour":
                time_window_price = Decimal(50.00)
            case "2 Hour":
                time_window_price = Decimal(30.00)
            case "4 Hour":
                time_window_price = Decimal(15.00)
        return time_window_price

    @property
    def get_display_string(self):
        return f"{self.pickup_address.location_name} -> {self.delivery_address.location_name} ({self.time_window}) ({self.order_status})"


"""Model that stores reference numbers used by customers and are associated via foreign key with the Order model's primary key."""


class ReferenceNumber(models.Model):
    ref_number = models.CharField(max_length=50)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)


"""Model that stores delivery location's information for each customer."""


class Contact(models.Model):
    contact_name = models.CharField(
        max_length=50,
    )
    phone_number = PhoneNumberField()
    address = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name="contacts"
    )

    def __str__(self):
        return f"{self.contact_name} {self.phone_number}"


class FuelPrice(models.Model):
    date_created = models.DateField(auto_now_add=True)
    gas_price = models.DecimalField(max_digits=19, decimal_places=4)
    diesel_price = models.DecimalField(max_digits=19, decimal_places=4)
