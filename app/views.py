
from django.shortcuts import render
import requests
from django.contrib.auth.decorators import login_required




@login_required
def home_view(request):
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false"
    data = requests.get(url).json()
    # return HttpResponse (data)
    # create_test_object.delay(("ram1",))
    
    # app = Celery()

    # @app.on_after_configure.connect
    # def setup_periodic_tasks(sender, **kwargs):
    # # Calls test('hello') every 10 seconds.
    #     sender.add_periodic_task(10.0, create_test_object.s('hello'), name='add every 10')
    context ={'data':data,}
    return render (request,'app/index.html',context)





    


    
