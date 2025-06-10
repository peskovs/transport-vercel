# transport/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.db.models import Count, Avg, Q
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
@login_required
def delete_atsauksme(request, atsauksme_id):
    atsauksme = get_object_or_404(Atsauksme, pk=atsauksme_id)
    user = request.user
    # Only author, admin, or superuser can delete
    is_admin = user.is_superuser or getattr(user, 'loma', None) == 'administrators'
    if atsauksme.lietotajs == user or is_admin:
        if request.method == 'POST':
            atsauksme.delete()
            next_url = request.POST.get('next') or request.GET.get('next') or request.META.get('HTTP_REFERER')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('transport:route_details', route_id=atsauksme.marsruts.pk)
        else:
            return HttpResponseForbidden(_('Invalid request method.'))
    else:
        return HttpResponseForbidden(_('You do not have permission to delete this review.'))

# @login_required
def home(request):
    """
    Galvenā lapa ar projektu informāciju un ātrajiem linkiem.
    """
    quick_links = [
        {'url': 'transport:routes_information', 'label': _('Routes')},
        {'url': 'transport:traffic_information', 'label': _('Traffic information')},
        {'url': 'transport:report_traffic', 'label': _('Report traffic')},
        {'url': 'transport:statistics', 'label': _('Statistics')},
    ]
    context = {
        'project_name': _('SmartTransport'),
        'description': _('This is the SmartTransport system for route management, traffic monitoring, and analytics.'),
        'quick_links': quick_links,
    }
    return render(request, 'transport/home.html', context)

def routes_list(request):
    """Route listing view"""
    search_query = request.GET.get('search', '')
    route_type = request.GET.get('type', 'all')
    sort_by = request.GET.get('sort', 'number')
    
    # Get all routes with their transport types using raw SQL
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT m.marsruts_id, m.numurs, m.nosaukums, m.apraksts, m.pilseta_id, 
                   v.veids_id, v.nosaukums as transport_type 
            FROM transport_marsruts m
            LEFT JOIN (
                SELECT DISTINCT tl.marsruts_id, tv.veids_id, tv.nosaukums
                FROM transport_transportlidzeklis tl
                JOIN transport_transportaveids tv ON tl.veids_id = tv.veids_id
            ) v ON m.marsruts_id = v.marsruts_id
        """)
        rows = cursor.fetchall()
    
    # Convert to a dictionary for easier access
    routes_data = {}
    for row in rows:
        marsruts_id, numurs, nosaukums, apraksts, pilseta_id, veids_id, transport_type = row
        routes_data[marsruts_id] = {
            'marsruts_id': marsruts_id,
            'numurs': numurs,
            'nosaukums': nosaukums,
            'apraksts': apraksts,
            'pilseta_id': pilseta_id,
            'veids_id': veids_id,
            'transport_type': transport_type or 'Autobuss'  # Default to bus if none assigned
        }
    
    # Get all routes as queryset for ORM operations
    routes = Marsruts.objects.all()

    # Filter by search query
    if search_query:
        route_ids_with_stops = MarsrutaPietura.objects.filter(
            pietura__nosaukums__icontains=search_query
        ).values_list('marsruts_id', flat=True).distinct()

        routes = routes.filter(
            Q(numurs__icontains=search_query) |
            Q(nosaukums__icontains=search_query) |
            Q(marsruts_id__in=route_ids_with_stops)
        )

    # Filter by transport type based on the data from our SQL query
    if route_type != 'all':
        # Map URL parameter to veids_id
        type_mapping = {
            'bus': 1,       # Autobuss
            'tram': 2,      # Tramvajs
            'trolley': 3,   # Trolejbuss
            'express': 4,   # Mikroautobuss
            'train': 8      # Dīzeļvilciens or 9 (Elektriskais vilciens)
        }
        
        if route_type in type_mapping:
            # Get route IDs that match the selected transport type
            matching_ids = []
            for route_id, data in routes_data.items():
                if data['veids_id'] == type_mapping[route_type] or \
                   (route_type == 'train' and data['veids_id'] == 9) or \
                   (data['veids_id'] is None and route_type == 'bus'):  # Default to bus if no type
                    matching_ids.append(route_id)
            
            # Filter the queryset to only include routes with matching IDs
            if matching_ids:
                routes = routes.filter(marsruts_id__in=matching_ids)

    # Sort results
    if sort_by == 'number':
        routes = routes.order_by('numurs')
    elif sort_by == 'name':
        routes = routes.order_by('nosaukums')
    elif sort_by == 'type':
        # Since there's no transporta_veids field, we'll sort by numurs instead
        routes = routes.order_by('numurs')

    # Add transport type information to each route for the template
    routes_with_types = []
    for route in routes:
        route_data = {
            'route': route,
            'veids_id': None,
            'transport_type': 'Autobuss'  # Default
        }
        
        # Add transport type info if available
        if route.marsruts_id in routes_data:
            route_data['veids_id'] = routes_data[route.marsruts_id]['veids_id']
            route_data['transport_type'] = routes_data[route.marsruts_id]['transport_type']
        
        routes_with_types.append(route_data)
    
    # Get transport types for the dropdown
    transport_types = [
        {'id': 1, 'code': 'bus', 'name': 'Autobuss'},
        {'id': 2, 'code': 'tram', 'name': 'Tramvajs'},
        {'id': 3, 'code': 'trolley', 'name': 'Trolejbuss'},
        {'id': 4, 'code': 'express', 'name': 'Mikroautobuss'},
        {'id': 8, 'code': 'train', 'name': 'Dīzeļvilciens'}
    ]
    
    # Add has_schedule property for each route
    from .models import KustibasGrafiks
    for route_data in routes_with_types:
        route_obj = route_data['route'] if isinstance(route_data, dict) and 'route' in route_data else route_data
        marsruts_id = route_obj.marsruts_id if hasattr(route_obj, 'marsruts_id') else getattr(route_obj, 'id', None)
        route_obj.has_schedule = KustibasGrafiks.objects.filter(marsruts_id=marsruts_id).exists()

    # Calculate statistics
    total_routes = routes.count()
    # Average frequency: schedules per route (if KustibasGrafiks is available)
    from .models import KustibasGrafiks, Transportlidzeklis
    schedule_counts = [KustibasGrafiks.objects.filter(marsruts=r['route']).count() for r in routes_with_types]
    avg_frequency = round(sum(schedule_counts) / total_routes, 2) if total_routes > 0 else 0
    # Operators count: unique operators of vehicles if such a field exists
    if hasattr(Transportlidzeklis, 'operators'):  # If there is an operators field
        operators_count = Transportlidzeklis.objects.values('operators').distinct().count()
    else:
        operators_count = Transportlidzeklis.objects.values('marsruts').distinct().count()

    context = {
        'routes': routes_with_types,
        'transport_types': transport_types,
        'total_routes': total_routes,
        'avg_frequency': avg_frequency,
        'operators_count': operators_count,
        # Pass search parameters back to template
        'search_query': search_query,
        'route_type': route_type,
        'sort_by': sort_by,
    }
    context['LANGUAGE_CODE'] = request.LANGUAGE_CODE if hasattr(request, 'LANGUAGE_CODE') else request.LANGUAGE_CODE if 'LANGUAGE_CODE' in request else 'lv'
    return render(request, 'transport/routes/list.html', context)

def route_details(request, route_id):
    """
    Maršruta detaļu skats
    """
    route = get_object_or_404(Marsruts, pk=route_id)
    stops = MarsrutaPietura.objects.filter(marsruts=route).order_by('kartas_nr')
    schedules = KustibasGrafiks.objects.filter(marsruts=route)
    vehicles = Transportlidzeklis.objects.filter(marsruts=route)

    # Reviews for this route
    atsauksmes = Atsauksme.objects.filter(marsruts=route).select_related('lietotajs').order_by('-laiks')
    user_review = None
    if request.user.is_authenticated:
        user_review = Atsauksme.objects.filter(marsruts=route, lietotajs=request.user).first()

    total_distance = max(stops.count() - 1, 0)
    total_time = total_distance * 3  # Assume 3 min between each stop

    # Provide is_saved to template for Save button state
    is_saved = False
    if request.user.is_authenticated:
        try:
            from .models import FavoriteRoute
            is_saved = FavoriteRoute.objects.filter(user=request.user, route=route).exists()
        except ImportError:
            is_saved = False
        except Exception:
            is_saved = False

    context = {
        'route': route,
        'stops': stops,
        'schedules': schedules,
        'vehicles': vehicles,
        'total_distance': total_distance,
        'total_time': total_time,
        'atsauksmes': atsauksmes,
        'user_review': user_review,
        'atsauksme_form': AtsauksmeForm() if request.user.is_authenticated and not user_review else None,
        'is_saved': is_saved,
    }

    return render(request, 'transport/routes/details.html', context)



@login_required
def submit_atsauksme(request, route_id):
    route = get_object_or_404(Marsruts, pk=route_id)
    # Prevent multiple reviews per user per route
    if Atsauksme.objects.filter(marsruts=route, lietotajs=request.user).exists():
        return HttpResponseForbidden(_('You have already submitted a review for this route.'))
    if request.method == 'POST':
        form = AtsauksmeForm(request.POST)
        if form.is_valid():
            atsauksme = form.save(commit=False)
            atsauksme.lietotajs = request.user
            atsauksme.marsruts = route
            atsauksme.save()
            messages.success(request, _('Your review has been submitted.'))
            return redirect('transport:route_details', route_id=route_id)
    else:
        form = AtsauksmeForm()
    atsauksmes = Atsauksme.objects.filter(marsruts=route).select_related('lietotajs').order_by('-laiks')
    user_review = Atsauksme.objects.filter(marsruts=route, lietotajs=request.user).first() if request.user.is_authenticated else None
    context = {
        'route': route,
        'atsauksme_form': form,
        'atsauksmes': atsauksmes,
        'user_review': user_review,
    }
    return render(request, 'transport/routes/details.html', context)

def stops_list(request):
    """
    Pieturu saraksta skats
    """
    # Get search parameters from request
    search_query = request.GET.get('search', '')
    city = request.GET.get('city', 'all')
    
    # Start with all stops
    stops = Pietura.objects.all()
    
    # Apply search filtering
    if search_query:
        # Search by stop name or address
        stops = stops.filter(
            Q(nosaukums__icontains=search_query) | 
            Q(adrese__icontains=search_query)
        )
    
    # Apply city filtering by pilseta_id
    if city != 'all':
        try:
            city_id = int(city)
            stops = stops.filter(pilseta__pilseta_id=city_id)
        except ValueError:
            pass
    
    # Get unique cities for the filter dropdown
    cities = Pilseta.objects.all()
    
    context = {
        'stops': stops,
        'cities': cities,
        'search_query': search_query,
        'selected_city': city,
    }

    return render(request, 'transport/stops/list.html', context)

def stop_details(request, stop_id):
    """
    Pieturas detaļu skats
    """
    stop = get_object_or_404(Pietura, pk=stop_id)
    route_stops = MarsrutaPietura.objects.filter(pietura=stop)
    reports = LietotajaZinojums.objects.filter(pietura=stop)

    # Šeit vajadzētu pievienot arī transportlīdzekļu ierašanās laiku aprēķinus

    context = {
        'stop': stop,
        'route_stops': route_stops,
        'reports': reports,
    }

    return render(request, 'transport/stops/details.html', context)

def traffic_information(request):
    """
    Satiksmes informācijas skats
    """
    # Get search parameters from request
    search_query = request.GET.get('search', '')
    condition_type = request.GET.get('condition_type', 'all')
    sort_by = request.GET.get('sort', 'latest')
    
    # Start with all conditions
    conditions = SatiksmeStavoklis.objects.all()
    
    # Apply search filtering
    if search_query:
        # Search by location or description
        conditions = conditions.filter(
            Q(cela_posms__icontains=search_query) | 
            Q(apraksts__icontains=search_query) |
            Q(pilseta__nosaukums__icontains=search_query)
        )
    
    # Apply condition type filtering
    if condition_type != 'all':
        conditions = conditions.filter(tips=condition_type)
        
    # Debug: Print query parameters and SQL query
    print(f"Search query: {search_query}, Condition type: {condition_type}, Sort by: {sort_by}")
    print(f"SQL query: {conditions.query}")
    print(f"Results count: {conditions.count()}")
    print(f"Condition values: {[c.tips for c in conditions]}")
    
    
    # Apply sorting
    if sort_by == 'latest':
        conditions = conditions.order_by('-sakuma_laiks')
    elif sort_by == 'severity':
        conditions = conditions.order_by('-intensitate_min')
    elif sort_by == 'city':
        conditions = conditions.order_by('pilseta__nosaukums')
    
    context = {
        'conditions': conditions,
        'search_query': search_query,
        'condition_type': condition_type,
        'sort_by': sort_by,
    }

    return render(request, 'transport/traffic/information.html', context)

@login_required
def report_traffic(request):
    """
    Satiksmes ziņojuma skats
    """
    if request.method == 'POST':
        form = TrafficReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            from django.utils import timezone
            report.lietotajs = request.user
            report.laiks = timezone.now()
            report.save()
            # Create a SatiksmeStavoklis entry so the report appears on the /traffic page
            from .models import SatiksmeStavoklis
            SatiksmeStavoklis.objects.create(
                tips=report.tips if hasattr(report, 'tips') else 'cits',
                cela_posms=getattr(report, 'marsruts', None) or getattr(report, 'pietura', None) or '',
                apraksts=report.apraksts,
                intensitate_min=report.pasazieru_skaits or 0,
                gps_koordinates=report.gps_koordinates,
                sakuma_laiks=report.laiks,
                pilseta=getattr(report.marsruts, 'pilseta', None) if hasattr(report, 'marsruts') and report.marsruts else None
            )
            messages.success(request, _('Your report has been submitted.'))
            return redirect('transport:traffic_information')
    else:
        form = TrafficReportForm()

    context = {
        'form': form,
    }

    return render(request, 'transport/traffic/report.html', context)

def statistics(request):
    """
    Statistikas skats
    """
    # Dati transporta veidu sadalījumam
    transport_types = TransportaVeids.objects.annotate(count=Count('transportlidzeklis'))

    # Pasažieru skaits pa dienām
    passenger_data = LietotajaZinojums.objects.values('laiks__date').annotate(
        count=Count('zinojums_id'),
        avg_passengers=Avg('pasazieru_skaits')
    )

    # Populārākie maršruti
    popular_routes = Marsruts.objects.annotate(
        report_count=Count('lietotajazinojums')
    ).order_by('-report_count')[:5]

    # Papildu statistika
    avg_delay = SatiksmeStavoklis.objects.aggregate(avg=Avg('intensitate_min'))['avg']
    accident_count = SatiksmeStavoklis.objects.filter(tips='negadijums').count()
    report_count = LietotajaZinojums.objects.count()

    context = {
        'transport_types': transport_types,
        'passenger_data': passenger_data,
        'popular_routes': popular_routes,
        'avg_delay': round(avg_delay, 2) if avg_delay else 0,
        'accident_count': accident_count,
        'report_count': report_count,
    }

    return render(request, 'transport/statistics/index.html', context)

@login_required
def operator_dashboard(request):
    """
    Operatora paneļa skats
    """
    # Pārbaudām, vai lietotājam ir operatora tiesības
    if request.user.loma != 'transporta_operators':
        messages.error(request, _('You do not have permission to access this page.'))
        return redirect('transport:home')

    vehicles = Transportlidzeklis.objects.all()
    traffic_conditions = SatiksmeStavoklis.objects.all()
    latest_reports = LietotajaZinojums.objects.order_by('-laiks')[:10]

    context = {
        'vehicles': vehicles,
        'traffic_conditions': traffic_conditions,
        'latest_reports': latest_reports,
    }

    return render(request, 'transport/operator/dashboard.html', context)

@login_required
def save_favorite_route(request):
    if request.method == 'POST' and request.user.is_authenticated:
        route_id = request.POST.get('route_id')
        try:
            route = Marsruts.objects.get(pk=route_id)
            obj, created = FavoriteRoute.objects.get_or_create(user=request.user, route=route)
            from django.http import JsonResponse
            return JsonResponse({'status': 'saved', 'created': created})
        except Marsruts.DoesNotExist:
            from django.http import JsonResponse
            return JsonResponse({'status': 'error', 'message': 'Route not found'}, status=404)
    from django.http import JsonResponse
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def remove_favorite_route(request):
    if request.method == 'POST' and request.user.is_authenticated:
        route_id = request.POST.get('route_id')
        try:
            route = Marsruts.objects.get(pk=route_id)
            FavoriteRoute.objects.filter(user=request.user, route=route).delete()
            from django.http import JsonResponse
            return JsonResponse({'status': 'removed'})
        except Marsruts.DoesNotExist:
            from django.http import JsonResponse
            return JsonResponse({'status': 'error', 'message': 'Route not found'}, status=404)
    from django.http import JsonResponse
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def profile(request):
    saved_routes = list(FavoriteRoute.objects.filter(user=request.user).select_related('route'))
    reports = LietotajaZinojums.objects.filter(lietotajs=request.user)
    review_count = Atsauksme.objects.filter(lietotajs=request.user).count()
    context = {
        'saved_routes': saved_routes,
        'reports': reports,
        'review_count': review_count,
        'debug_user_id': request.user.pk,
        'debug_username': request.user.username,
        'debug_fav_count': saved_routes.count(),
    }
    return render(request, 'users/profile.html', context)

@login_required
def admin_dashboard(request):
    """
    Administratora paneļa skats
    """
    # Pārbaudām, vai lietotājam ir administratora tiesības
    if request.user.loma != 'administrators':
        messages.error(request, _('You do not have permission to access this page.'))
        return redirect('transport:home')

    users = User.objects.all()
    reports = LietotajaZinojums.objects.all()

    context = {
        'users': users,
        'reports': reports,
    }

    return render(request, 'transport/admin/dashboard.html', context)