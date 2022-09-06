from django.shortcuts import render
from .tasks import notify_customers

# Create your views here.
def say_hello(request):
    notify_customers.delay('Hellooo')
    return render(request, 'hello.html', {'name': 'Talitha'})