import json
from channels.generic.websocket import AsyncWebsocketConsumer


class MyasyncWebsocketConsumer(AsyncWebsocketConsumer):
   
    async def connect(self):
   

        # Join room group
        await self.channel_layer.group_add(
            "cryptoapp",
            self.channel_name
        )
        await self.accept()

    

    # Receive message from WebSocket
    async def receive(self, text_data):
        # print(text_data)
        text_data_json = json.loads(text_data)
        message= text_data_json['message']
        # print(message)
        
        # print(text_data_json)

        # Send message to room group
        await self.channel_layer.group_send(
            "cryptoapp",
            
            {
                'type': 'crypto.update',
                'message': message
            }
        )
        
        
    
    # Receive message from room group
    async def crypto_update(self, event):
        # print("ready to update",event)
        message = event['message']
        # print(message)
        for i in message:
            j=dict(i)
            # print(type(j))
            # print(j['name'])
            name=j['name']
            image=j['image']
            rank=j['market_cap_rank']
            price=j['current_price']
            mcap=j['market_cap']
            Id=j['id']
            
            data={'name':name,
                  'image':image,
                  'rank':rank,
                  'price':price,
                  'mcap':mcap,
                  'Id':Id
                  }
            await self.send(text_data=json.dumps(
                {'message':data}
                
                )
            )
        
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            "cryptoapp",
            self.channel_name
        )
        
        
