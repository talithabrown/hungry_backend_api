from django.shortcuts import render
from .tasks import notify_customers
import logging

logger = logging.getLogger(__name__)

# Create your views here.
def say_hello(request):
    logger.info('Calling function name')
    notify_customers.delay('Hellooo')
    return render(request, 'hello.html', {'name': 'Talitha'})