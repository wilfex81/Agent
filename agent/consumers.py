import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .langchainmodel import agent_match_rider

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(json.dumps({
            'message': "Hello! Type 'Find me a ride' to request a rider."
        }))
        
        
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "").lower()
        
        if "find me a ride" in message:
            passenger_lat, passenger_lon = 6.5244, 3.3792
            
            matched_rider = await agent_match_rider(passenger_lat, passenger_lon)  # Await the async function
            
            if matched_rider:
                response = f"Rider {matched_rider['name']} (📞 {matched_rider['phone']}) is on the way!"
            else:
                response = "Sorry, no rider is available at the moment."
            
            await self.send(json.dumps({'message': response}))
        
        else:
            await self.send(json.dumps({
                "message": "I can only help you find a ride. Try saying 'Find me a ride'."
            }))
