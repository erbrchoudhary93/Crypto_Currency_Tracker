import asyncio
from .models import Position
from celery import shared_task
import requests
from channels.layers import get_channel_layer

from crypto_app.celery import app


  
      
@shared_task(bind=True)
def get_crypto_data(self):
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false"
    data = requests.get(url).json()
    for item in data:
        p,_ = Position.objects.get_or_create(name=item['name'])
        p.image=item['image']
        p.price =item['current_price']
        p.rank=item['market_cap_rank']
        p.market_cap =item['market_cap']
        p.save()        
        # Send Data to Group
        channel_layer= get_channel_layer()
        loop=asyncio.get_event_loop()

        asyncio.set_event_loop(loop)
            
        loop.run_until_complete(channel_layer.group_send("cryptoapp",{
            
                'type':'crypto_update',
                'message': data
            }
            ))
        
        

@app.task
def create_test_object():
    get_crypto_data.delay()
    
        
        
