from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .serializers import ConnectionSerializer
from .services.services import list_connections, get_connection, delete_connection
from utils.pagination import paginate_queryset


class ConnectionListCreateAPIView(APIView):

    @swagger_auto_schema(
        operation_description="Get a list of all connections with nested config",
        responses={200: ConnectionSerializer(many=True)}
    )
    @paginate_queryset(ConnectionSerializer)
    def get(self, request):
        queryset = list_connections()
        return queryset

    @swagger_auto_schema(
        operation_description="Create a new connection of type sftp/shopify/restlet",
        request_body=ConnectionSerializer,
        responses={
            201: ConnectionSerializer,
            400: "Validation errors"
        }
    )
    def post(self, request):
        serializer = ConnectionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            connection = serializer.save()
            return Response(ConnectionSerializer(connection, context={'request': request}).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConnectionDetailAPIView(APIView):

    @swagger_auto_schema(
        operation_description="Retrieve a single connection by ID",
        responses={200: ConnectionSerializer, 404: "Not found"}
    )
    def get(self, request, pk):
        connection = get_connection(pk)
        serializer = ConnectionSerializer(connection, context={'request': request})
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Delete a connection by ID (logical delete)",
        responses={204: "Deleted", 400: "Already deleted", 404: "Not found"}
    )
    def delete(self, request, pk):
        connection = get_connection(pk, include_deleted=True)
        if connection.is_deleted:
            return Response({'detail': 'Connection already deleted.'}, status=status.HTTP_400_BAD_REQUEST)

        delete_connection(connection)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description="Update a connection by ID (partial allowed)",
        request_body=ConnectionSerializer,
        responses={200: ConnectionSerializer, 400: "Validation errors", 404: "Not found"}
    )
    def put(self, request, pk):
        connection = get_connection(pk)
        serializer = ConnectionSerializer(connection, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            updated_connection = serializer.save()
            return Response(ConnectionSerializer(updated_connection, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
