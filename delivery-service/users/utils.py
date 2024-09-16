from django.conf import settings
from google.maps import addressvalidation_v1
import googlemaps
from google.type import postal_address_pb2
from google.oauth2 import service_account
import os


def validate():

    gmaps = googlemaps.Client(key=settings.MAPS_KEY)

    address_validation_result = gmaps.addressvalidation(
        ["7907 Canoga Av"],
        regionCode="US",
        locality="Austin",
    )
    print(address_validation_result)


def validatev2():
    credentials = service_account.Credentials.from_service_account_file(
        "/workspaces/Delivery-Service/delivery-service/users/service_account.json"
    )

    client = addressvalidation_v1.AddressValidationClient(credentials=credentials)

    address1 = postal_address_pb2.PostalAddress(
        address_lines=["109 Coneflower"],  # Street address
        locality="Elgin",  # City
        administrative_area="TX",  # State# ZIP code # Country
    )

    mapping_data = {
        "address": {
            "address_lines": ["109 Coneflower"],
            "locality": "Elgin",
            "administrative_area": "TX",
        }
    }

    # Initialize request argument(s)
    request = addressvalidation_v1.ValidateAddressRequest(address=address1)

    # Make the request
    response = client.validate_address(request=request)

    # Handle the response
    print(response)
