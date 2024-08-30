from rest_framework.views import APIView
from rest_framework.response import Response
from User.models import File
from django.http import FileResponse
from .models import Vendor
from django.db.models import Sum
from math import ceil


class FileAPIView(APIView):
    def get(self, request):
        fid = self.request.query_params.get('fid')
        user = self.request.query_params.get('user')
        count = self.request.query_params.get('count')
        file = File.objects.get(user=user, fid=fid, count=count, Printed=False)
        vendor = Vendor.objects.get(User=request.user)
        vendor.AvailablePages -= file.pages if not file.DoubleSided else ceil(file.pages/2)
        vendor.TonerCount += file.pages
        vendor.DrumCount += file.pages
        vendor.save()
        file.Printed = True
        file.save()
        ext = file.filename.split('.')[-1]
        return FileResponse(open(f"files/{file.file}", 'rb'),
                            filename=f"{{'Filename': '{file.user.id}-{file.fid}-{file.count}.{ext}',"
                                     f" 'Copies': {file.Copies},"
                                     f" 'DoubleSided': {file.DoubleSided},"
                                     f" 'Pages': {file.pages}}}"
                            )


class QRCheckView(APIView):
    def get(self, request):
        fid = self.request.query_params.get('fid')
        user = self.request.query_params.get('user')
        res = File.objects.filter(user=user, fid=fid, Printed=False)
        pages = res.aggregate(Sum("pages"))
        if not len(res):
            return Response({"message": "Invalid"})
        else:
            return Response({'user': int(user), 'fid': int(fid), 'count': res.count(), 'pages': pages['pages__sum']})
