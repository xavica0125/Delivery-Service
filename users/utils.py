from django.conf import settings
from google.maps import addressvalidation_v1, routing_v2
from google.type import postal_address_pb2
from google.oauth2 import service_account
from .models import Address
from google.protobuf.json_format import MessageToDict

import json

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

    request = routing_v2.ComputeRoutesRequest(
        origin=origin,
        destination=destination,
        routing_preference=2,
        compute_alternative_routes=True,
        units=2,
        extra_computations=[1, 2, 3],
    )

    response = client.compute_routes(
        request=request,
        metadata=[
            (
                "x-goog-fieldmask",
                "routes.polyline,routes.travelAdvisory,routes.legs.travelAdvisory,routes.duration,routes.travelAdvisory.tollInfo,routes.legs.travelAdvisory.tollInfo,",
            )
        ],
    )
    print("BEGIN")
    print(response)
    print("END RESPONSE")
    json_response = MessageToDict(response._pb)

    return json_response


"""Retrieves addresses Place ID and coordinates for origin and destination and calls Google API to return route information."""


def route_calculation(originPlaceID, destinationPlaceID):

    response = calculate_route(originPlaceID, destinationPlaceID)

    return response
