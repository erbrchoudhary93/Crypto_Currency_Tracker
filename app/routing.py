from django.urls import path,re_path
from .import consumers



websocket_urlpattern  =  [ 
        
                      
        # path('ws/sc/<str:groupkaname>/',consumers.MyWebsocketConsumer.as_asgi()),                  
        re_path('ws/asc/',consumers.MyasyncWebsocketConsumer.as_asgi()),  
        # re_path(r'ws/asc/(?P<room_name>\w+)/$', consumers.MyasyncWebsocketConsumer.as_asgi()),                
                          
]