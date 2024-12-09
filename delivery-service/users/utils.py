from django.conf import settings
from google.maps import addressvalidation_v1, routing_v2
import googlemaps
from google.type import postal_address_pb2
from google.oauth2 import service_account
from .models import Address

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
    print(response)
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

"""Calls Google Maps API to get distance and encoded polyline."""

def calculate_route(origin_address, destination_address):
    client = routing_v2.RoutesClient()

    origin = routing_v2.Waypoint(place_id=origin_address)
    destination = routing_v2.Waypoint(place_id=destination_address)

    request = routing_v2.ComputeRoutesRequest(origin=origin, destination=destination)

    response = client.compute_routes(
        request=request,
        metadata=[
            (
                "x-goog-fieldmask",
                "routes.localized_values,routes.polyline.encoded_polyline",
            )
        ],
    )
    encoded_polyline = response.routes[0].polyline.encoded_polyline
    return encoded_polyline

"""Retrieves addresses Place ID and coordinates for origin and destination and calls Google API to return route information."""

def route_calculation(request):
    origin_id = request.POST.get("pickup_address")
    destination_id = request.POST.get("delivery_address")

    origin_address = Address.objects.get(id=origin_id)
    destination_address = Address.objects.get(id=destination_id)

    origin_address_coordinates = (origin_address.latitude, origin_address.longitude)
    destination_address_coordinates = (destination_address.latitude, destination_address.longitude)
    response = calculate_route(origin_address.place_id, destination_address.place_id)

    route_info = [response, origin_address_coordinates, destination_address_coordinates]

    return route_info
