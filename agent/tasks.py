from celery import shared_task
from django.db import connection
from datetime import timedelta
from .models import RideRequest
from django.utils.timezone import now
import random
import time
import math

# Simulate rider response time
RIDER_RESPONSE_TIME = (2, 10)  # Riders take 2-10 seconds to respond


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculates distance between two coordinates using the Haversine formula"""
    R = 6371  # Radius of Earth in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # Distance in km


def find_nearest_riders(passenger_lat, passenger_lon, limit=5):
    """Returns nearest riders based on hardcoded data"""
    hardcoded_riders = [
        {"id": 1, "name": "John Doe", "phone": "1234567890", "latitude": 6.5, "longitude": 3.3},
        {"id": 2, "name": "Jane Smith", "phone": "0987654321", "latitude": 6.6, "longitude": 3.4},
        {"id": 3, "name": "Mike Johnson", "phone": "5678901234", "latitude": 6.7, "longitude": 3.5},
        {"id": 4, "name": "Sarah Brown", "phone": "2345678901", "latitude": 6.8, "longitude": 3.6},
        {"id": 5, "name": "David Wilson", "phone": "3456789012", "latitude": 6.9, "longitude": 3.7},
    ]

    # Compute distances
    for rider in hardcoded_riders:
        rider["distance"] = calculate_distance(
            passenger_lat, passenger_lon, rider["latitude"], rider["longitude"]
        )

    # Sort by distance and return top `limit` riders
    return sorted(hardcoded_riders, key=lambda r: r["distance"])[:limit]


@shared_task
def request_rider(passenger_lat, passenger_lon, price_offer):
    """Passenger agent requests a ride and negotiates price with nearby riders."""
    riders = find_nearest_riders(passenger_lat, passenger_lon)

    for rider in riders:
        time.sleep(random.randint(*RIDER_RESPONSE_TIME))  # Simulate real response time

        if rider_accepts(rider, price_offer):
            #  TODO: Send notification to passenger that a rider accepted the request
            return {"rider": rider, "final_price": price_offer}
        
        new_price = price_offer * 1.1

        if new_price <= price_offer * 1.2:
            #  TODO: Send notification to passenger that a rider counter-offered a new price
            return {"rider": rider, "final_price": new_price}

    #  TODO: Notify passenger that no rider accepted the request
    return None


def rider_accepts(rider, price_offer):
    """Simulates rider decision-making"""
    acceptance_chance = random.random()  # 50% chance of accepting
    return acceptance_chance > 0.5  # Rider accepts if above 0.5


@shared_task
def assign_scheduled_rides():
    """Assigns riders to scheduled rides 15 minutes before pickup time."""
    time_window = now() + timedelta(minutes=15)
    rides = RideRequest.objects.filter(scheduled_time__lte=time_window, status="pending")

    processed_rides = 0

    for ride in rides:
        if ride.scheduled_time < now():
            print(f"Skipping expired ride for passenger {ride.passenger.id}")
            continue
        
        if ride.status != "pending":
            print(f"Skipping ride {ride.id}, already {ride.status}")
            continue

        assigned_rider = find_nearest_riders(ride.pickup_lat, ride.pickup_lon, limit=1)

        if assigned_rider:
            ride.rider_id = assigned_rider[0]['id']
            ride.status = "confirmed"
            ride.save()

            # TODO: Send push notification to the assigned rider
            # TODO: Send push notification to the passenger
            print(f"Assigned rider {assigned_rider[0]['name']} to {ride.passenger}'s ride.")
        else:
            ride.status = "no_rider_found"
            ride.save()

            # TODO: Notify the passenger that no riders were found
            print(f"No riders available for {ride.passenger}'s ride.")

        processed_rides += 1

    return f"Processed {processed_rides} scheduled rides."


@shared_task
def auto_cancel_unconfirmed_rides():
    """Auto-cancel scheduled rides that are unconfirmed 15 minutes before pickup time."""
    time_threshold = now() + timedelta(minutes=15)
    rides = RideRequest.objects.filter(status="pending", scheduled_time__lte=time_threshold)

    cancelled_rides = 0

    for ride in rides:
        if ride.scheduled_time < now():
            print(f"Skipping expired ride cancellation for passenger {ride.passenger.id}")
            continue

        if ride.status not in ["pending"]:
            print(f"Skipping ride {ride.id}, already {ride.status}")
            continue

        ride.status = "cancelled"
        ride.save()

        # TODO: Notify passengers that the rides were auto-cancelled
        print(f"Auto-cancelled {ride.passenger}'s ride.")

        cancelled_rides += 1

    return f"Cancelled {cancelled_rides} unconfirmed rides."

