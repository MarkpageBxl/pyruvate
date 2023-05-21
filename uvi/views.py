import json

from django.http import HttpResponse

from . import uvi


# Create your views here.
def uv_index(request):
    uv_data = uvi.get_current()
    json_data = json.dumps(uv_data, cls=uvi.UvDataEncoder)
    return HttpResponse(json_data, headers={"Content-Type": "application/json"})
