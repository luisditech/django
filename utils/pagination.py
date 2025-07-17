from functools import wraps
from rest_framework.response import Response

def paginate_queryset(serializer_class):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            result = view_func(self, request, *args, **kwargs)

            if isinstance(result, dict) and 'queryset' in result:
                queryset = result['queryset']
            elif hasattr(result, 'all'):
                queryset = result
            else:
                return Response({'error': 'Invalid queryset'}, status=400)

            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 10))

            total = queryset.count()
            start = (page - 1) * limit
            end = start + limit

            paginated_queryset = queryset[start:end]
            serializer = serializer_class(paginated_queryset, many=True, context={'request': request})

            return Response({
                'data': serializer.data,
                'total': total,        
                'limit': limit,
                'page': page
            }, status=200)

        return _wrapped_view
    return decorator