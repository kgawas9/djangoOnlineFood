from django.shortcuts import render
from vendor.models import Vendor

# For location
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D # 'D is shortcut for distance
from django.contrib.gis.db.models.functions import Distance


def get_or_set_current_location(request):
    if 'lat' in request.session:
        latitude = request.session['lat']
        longitude = request.session['lng']

        return longitude, latitude 

    elif 'lat' in request.GET:
        latitude = request.GET.get('lat')
        longitude = request.GET.get('lng')

        request.session['lat'] = latitude
        request.session['lng'] = longitude

        return longitude, latitude
    
    else:
        return None



def home(request):
    if get_or_set_current_location(request) is not None:
        # latitude = request.GET.get('lat')
        # longitude = request.GET.get('lng')

        pnt = GEOSGeometry('POINT(%s %s)' %(get_or_set_current_location(request)))

        vendors = Vendor.objects.filter(user_profile__location__distance_lte=(pnt, D(km=100))
                                            ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

        for v in vendors:
            v.kms = round(v.distance.km,2)
    
    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    
    context = {
        'vendor_list': vendors,
    }
    return render(request, 'home.html', context=context)

