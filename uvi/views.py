import json

from django.http import HttpResponse

from . import uvdata


# Create your views here.
def uv_index(request):
    uv_data = uvdata.get_current()
    json_data = json.dumps(uv_data, cls=uvdata.UvDataEncoder)
    return HttpResponse(json_data, headers={"Content-Type": "application/json"})
