from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .tasks import request_rider, assign_scheduled_rides, auto_cancel_unconfirmed_rides
from .models import RideRequest
from django.utils.timezone import now
from datetime import timedelta

# Passenger requests a ride
class RideRequest(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'passenger_lat': openapi.Schema(type=openapi.TYPE_NUMBER, description="Passenger's latitude"),
                'passenger_lon': openapi.Schema(type=openapi.TYPE_NUMBER, description="Passenger's longitude"),
                'price_offer': openapi.Schema(type=openapi.TYPE_NUMBER, description="Offered price for the ride"),
            },
            required=['passenger_lat', 'passenger_lon', 'price_offer']
        ),
        responses={200: "Ride request initiated."}
    )
    def post(self, request):
        """
        Handle the ride request from the passenger.

        Args:
            request (Request): The request object containing passenger's ride details.

        Returns:
            Response: A response object indicating the status of the ride request initiation.
        """
        passenger_lat = request.data.get("passenger_lat")
        passenger_lon = request.data.get("passenger_lon")
        price_offer = request.data.get("price_offer")

        if not all([passenger_lat, passenger_lon, price_offer]):
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        task = request_rider.delay(passenger_lat, passenger_lon, price_offer)
        return Response({"message": "Ride request initiated.", "task_id": task.id}, status=status.HTTP_200_OK)


# Rider accepts a ride
class RideAccept(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ride_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the ride request"),
                'rider_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Rider's ID accepting the ride"),
            },
            required=['ride_id', 'rider_id']
        ),
        responses={200: "Ride accepted successfully."}
    )
    def post(self, request):
        """
        Handle the acceptance of a ride by a rider.

        Args:
            request (Request): The request object containing ride acceptance details.

        Returns:
            Response: A response object indicating the status of the ride acceptance.
        """
        ride_id = request.data.get("ride_id")
        rider_id = request.data.get("rider_id")

        try:
            ride = RideRequest.objects.get(id=ride_id, status="pending")
            ride.rider_id = rider_id
            ride.status = "confirmed"
            ride.save()
            return Response({"message": "Ride accepted successfully."}, status=status.HTTP_200_OK)
        except RideRequest.DoesNotExist:
            return Response({"error": "Ride not found or already assigned."}, status=status.HTTP_404_NOT_FOUND)

class ScheduleRide(APIView):
    def post(self, request):
        """
        Schedule a ride for a future time.

        Args:
            request (Request): The request object containing ride scheduling details.

        Returns:
            Response: A response object indicating the status of the ride scheduling.
        """
        data = request.data
        pickup_lat = data.get("pickup_lat")
        pickup_lon = data.get("pickup_lon")
        dropoff_lat = data.get("dropoff_lat")
        dropoff_lon = data.get("dropoff_lon")
        scheduled_time = data.get("scheduled_time")  # Frontend should send this in UTC format

        if not all([pickup_lat, pickup_lon, dropoff_lat, dropoff_lon, scheduled_time]):
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        ride = RideRequest.objects.create(
            passenger=request.user,
            pickup_lat=pickup_lat,
            pickup_lon=pickup_lon,
            dropoff_lat=dropoff_lat,
            dropoff_lon=dropoff_lon,
            scheduled_time=scheduled_time,
            status="pending",
        )

        #Immediately try to assign a rider
        assign_scheduled_rides.delay()

        return Response(
            {"message": "Ride scheduled successfully.", "ride_id": ride.id},
            status=status.HTTP_201_CREATED,
        )

class CancelScheduledRide(APIView):
    def post(self, request, ride_id):
        """
        Cancel a scheduled ride.

        Args:
            request (Request): The request object containing user details.
            ride_id (int): The ID of the ride to be cancelled.

        Returns:
            Response: A response object indicating the status of the ride cancellation.
        """
        try:
            ride = RideRequest.objects.get(id=ride_id, passenger=request.user, status="pending")
        except RideRequest.DoesNotExist:
            return Response({"error": "Ride not found or already assigned."}, status=status.HTTP_404_NOT_FOUND)

        ride.status = "cancelled"
        ride.save()

        return Response({"message": "Scheduled ride cancelled successfully."}, status=status.HTTP_200_OK)


# Assign riders to scheduled rides (triggered periodically)
class AssignScheduledRidesView(APIView):
    def post(self, request):
        task = assign_scheduled_rides.delay()
        return Response({"message": "Scheduled rides assignment initiated.", "task_id": task.id}, status=status.HTTP_200_OK)


# Auto-cancel unconfirmed scheduled rides
class AutoCancelUnconfirmedRidesView(APIView):
    def post(self, request):
        task = auto_cancel_unconfirmed_rides.delay()
        return Response({"message": "Auto-cancelation process started.", "task_id": task.id}, status=status.HTTP_200_OK)
