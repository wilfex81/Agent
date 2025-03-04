import openai
from langchain_community.llms import OpenAI
from math import radians, cos, sin, asin, sqrt
from django.db import connection
from asgiref.sync import sync_to_async
import asyncio
import time

from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
print("****************")
print(openai_api_key)
print("******##############3*****")

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Earth radius in km
    return c * r
@sync_to_async
# def find_nearest_riders(passenger_lat, passenger_lon, limit=5):
#     """Finds the closest 5 riders"""
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             SELECT id, name, phone, latitude, longitude,
#             (6371 * acos(cos(radians(%s)) * cos(radians(latitude)) *
#             cos(radians(longitude) - radians(%s)) +
#             sin(radians(%s)) * sin(radians(latitude)))) AS distance
#             FROM riders
#             ORDER BY distance
#             LIMIT %s;
#         """, [passenger_lat, passenger_lon, passenger_lat, limit])

#         riders = cursor.fetchall()
    
#     return [
#         {"id": r[0], "name": r[1], "phone": r[2], "latitude": r[3], "longitude": r[4], "distance": r[5]}
#         for r in riders
#     ]
def find_nearest_riders(passenger_lat, passenger_lon, limit=5):
    """Returns a hardcoded list of nearby riders"""
    riders = [
        {"id": 1, "name": "John Doe", "phone": "+1234567890", "latitude": 6.5244, "longitude": 3.3792, "distance": 1.2},
        {"id": 2, "name": "Jane Smith", "phone": "+1987654321", "latitude": 6.5250, "longitude": 3.3800, "distance": 2.4},
        {"id": 3, "name": "Mike Johnson", "phone": "+1122334455", "latitude": 6.5260, "longitude": 3.3810, "distance": 3.1},
    ]
    
    return riders[:limit]  # Return only `limit` number of riders

def ask_rider(rider):
    """Simulates asking a rider via AI"""
    prompt = f"Rider {rider['name']} (Phone: {rider['phone']}) is {rider['distance']:.2f} km away. Will they accept the ride?"
    print(prompt)

    llm = OpenAI(openai_api_key=openai_api_key)
    response = llm.invoke(prompt) 

    return "yes" in response.lower()


async def agent_match_rider(passenger_lat, passenger_lon):
    """Main AI agent logic to match a passenger with a rider"""
    riders = await find_nearest_riders(passenger_lat, passenger_lon)  # Await the async function
    
    for rider in riders:
        if await asyncio.to_thread(ask_rider, rider):  # Run ask_rider in a separate thread
            return rider  # The rider accepted the request

        await asyncio.sleep(1)  # Wait before trying the next rider

    return None  # No available rider

