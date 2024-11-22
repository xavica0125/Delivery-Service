from django.conf import settings
from google.maps import addressvalidation_v1, routing_v2
import googlemaps
from google.type import postal_address_pb2
from google.oauth2 import service_account

"""Creates validation request and returns validation action and response from validation request. """


def validate_customer_address(cust_address, city, zip_code):
    # credentials = service_account.Credentials.from_service_account_file(
    #    settings.GOOGLE_SERVICE_ACCOUNT_KEY
    # )

    client = addressvalidation_v1.AddressValidationClient()

    if not city or not zip_code:
        address = postal_address_pb2.PostalAddress(address_lines=[cust_address])
    else:
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
    # print(response)
    return (suggest_validation_action(response), response)


"""Suggest validation action to take based on validate address response."""


def suggest_validation_action(address_validation_response):
    if (
        address_validation_response.result.verdict.validation_granularity > 2
        or not address_validation_response.result.verdict.address_complete
    ):
        # print(address_validation_response.result.verdict.validation_granularity)
        return "FIX"
    elif (
        address_validation_response.result.verdict.has_replaced_components
        or address_validation_response.result.verdict.has_unconfirmed_components
    ):
        return "CONFIRM"
    else:
        return "ACCEPT"


""" Utility function that populates context that will be sent to confirmation template."""


def populate_address_context(address_components, context={}):
    for component in address_components:
        component_type = component.component_type
        if component_type == "street_number":
            context["street_address"] = component.component_name.text
        elif component_type == "route":
            context["street_address"] += f" {component.component_name.text}"
        elif component_type == "subpremise":
            context["sub_premise"] = component.component_name.text
        elif component_type == "locality":
            context["city"] = component.component_name.text
        elif component_type == "postal_code":
            context["zip_code"] = component.component_name.text

    return context


def calculate_route():
    client = routing_v2.RoutesClient()

    origin = routing_v2.Waypoint(address="109 Coneflower Cv., Elgin, TX 78621")
    destination = routing_v2.Waypoint(address="153 Fawn Hollow, Elgin, TX 78621")

    request = routing_v2.ComputeRoutesRequest(origin=origin, destination=destination)

    fieldMask = "formattedAddress,displayName"

    response = client.compute_routes(
        request=request, metadata=[("x-goog-fieldmask", "routes.localized_values")]
    )

    return response
