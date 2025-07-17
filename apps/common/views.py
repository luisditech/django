from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.common.services.email_service import send_external_email

class SendEmailAPIView(APIView):
    def post(self, request):
        to = request.data.get("to")
        subject = request.data.get("subject")
        body = request.data.get("body")

        if not to or not subject or not body:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        result = send_external_email(to=to, subject=subject, body=body)

        if result["success"]:
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)