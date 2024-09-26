from django.conf import settings
from google.maps import addressvalidation_v1
import googlemaps
from google.type import postal_address_pb2
from google.oauth2 import service_account


"""def validate():

    gmaps = googlemaps.Client(key=settings.MAPS_KEY)

    address_validation_result = gmaps.addressvalidation(
        ["7907 Canoga Av"],
        regionCode="US",
        locality="Austin",
    )
    print(address_validation_result)"""


def validate_customer_address(cust_address, city, zip_code):
    # credentials = service_account.Credentials.from_service_account_file(
    #    settings.GOOGLE_SERVICE_ACCOUNT_KEY
    # )

    client = addressvalidation_v1.AddressValidationClient()

    address = postal_address_pb2.PostalAddress(
        address_lines=[cust_address],  # Street address
        locality=city,  # City
        administrative_area="TX",
        postal_code=zip_code,  # State# ZIP code # Country
    )

    mapping_data = {
        "address": {
            "address_lines": ["109 Coneflower"],
            "locality": "Elgin",
            "administrative_area": "TX",
        }
    }

    # Initialize request argument(s)
    request = addressvalidation_v1.ValidateAddressRequest(address=address)
    # Make the request
    response = client.validate_address(request=request)
    print(response)
    return suggest_validation_action(response)


"""Suggest validation action to take based on validate address response."""


def suggest_validation_action(address_validation_response):
    if address_validation_response.result.verdict.validation_granularity not in [1, 2]:
        print(address_validation_response.result.verdict.validation_granularity)
        return "FIX"
    elif (
        # address_validation_response["result"]["verdict"]["hasInferredComponents"]
        address_validation_response.result.verdict.has_replaced_components
    ):
        # or address_validation_response.result.verdict.has_unconfirmed_components

        return "CONFIRM"
    elif address_validation_response.result.verdict.address_complete:
        return "ACCEPT"
