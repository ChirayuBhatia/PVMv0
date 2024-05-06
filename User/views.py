from datetime import datetime
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .utils import base64_encode, calculate_sha256_string
from django.views.decorators.csrf import csrf_exempt
from .models import File
from PyPDF2 import PdfReader
from qrcode import make
from io import BytesIO
import requests
from math import ceil
import razorpay
# for sending mails and generate token
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings


INDEX = "1"
SALTKEY = "099eb0cd-02cf-4e2a-8aca-3e6c6aff0399"
MERCHANT_ID = "PGTESTPAYUAT"
PRICE_SINGLE_SIDED = 1.5
PRICE_DOUBLE_SIDED = 1

CLIENT_ID = "rzp_test_34xiv7uMNp00GI"
CLIENT_SECRET = "BUA8hBQNrgkd4aLFFm3VVeXO"



@login_required(login_url='/login/')
def qr_image(request, fid):
    user = request.user
    data = {"user": user.id, "fid": fid}
    img = make(str(data))
    buffer = BytesIO()
    img.save(buffer, kind="PNG")
    buffer.seek(0)
    return HttpResponse(buffer)


def login_page(request):
    if request.method == "POST":
        email = request.POST.get("email")
        passwrd = request.POST.get("pswd")

        if not User.objects.filter(email=email).exists():
            messages.error(request, "Email not registered.")
            return redirect("/User/login/")

        user = authenticate(username=email, password=passwrd)

        if user is None:
            messages.error(request, "Invalid Password.")
            return redirect(r"/login/")
        else:
            login(request, user)
            return redirect("/uploadfiles/")
    else:
        if request.user.is_authenticated:
            return redirect("/uploadfiles")
        else:
            return render(request, 'LogIn.html')


@login_required(login_url='/login/')
def logout_page(request):
    logout(request)
    return redirect("/login/")


def register_page(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        passwrd = request.POST.get("pwd")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("/register/")

        user = User.objects.create(
            username=email,
            first_name=name.split()[0],
            last_name=" ".join(name.split()[1:]),
            email=email,
            is_active=False,
        )
        user.set_password(passwrd)
        user.save()
        email_subject = "Activate Your Account"
        message = render_to_string(
            "activate.html",
            {
                'user': user,
                'domain': '127.0.0.1:8000',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user)
            }
        )
        email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [email])
        email_message.send()
        messages.success(request, "Verification Email sent to Your Email Please verify.")
        return redirect("/register/")
    else:
        return render(request, 'Register.html')


@login_required(login_url='/login/')
def upload_files(request):
    if request.method == "POST":
        user = request.user
        files = request.FILES.getlist("files[]")
        subject = request.POST.get("subject")
        fid = File.objects.last().fid + 1
        count, total_pages = 0, 0
        upload = None
        for file in files:
            ext = file.name.rsplit(".")[-1]
            pages = len(PdfReader(file).pages) if ext == "pdf" else 1
            upload = File.objects.create(
                user=user,
                fid=fid,
                count=count,
                Subject=subject if subject != "" else datetime.now(),
                filename=file.name,
                pages=pages,
                file=file
            )
            total_pages += pages
            upload.save()
            count += 1
        if total_pages > 100:
            messages.error(request, "Sorry! Maximum of 100 pages of files can be printed at a time.")
            return redirect("/uploadfiles/")
        else:
            messages.success(request, "File(s) uploaded successfully.\n"
                             "Please configure the print settings for your files.")
            return redirect(f"/printsettings/{upload.fid}/")
    else:
        return render(request, "UploadFiles.html")


@login_required(login_url="/login/")
def printsettings(request, fid):
    if request.method == "POST":
        dct = dict(request.POST)
        user = request.user
        print(dct)
        total = 0
        files = File.objects.filter(user=user, fid=fid).all()
        for x in dct.keys():
            splt = x.split("_")
            if splt[0] == "copies":
                file = files[int(splt[2])]
                file.Copies = int(dct[x][0])
                if f"check_{fid}_{file.count}" in dct.keys():
                    file.DoubleSided = True
                total += (file.pages * file.Copies * (PRICE_DOUBLE_SIDED if file.DoubleSided else PRICE_SINGLE_SIDED))
                file.pages = ceil(file.pages * file.Copies * (0.5 if file.DoubleSided else 1))
                file.save()

        # client = razorpay.Client(auth=(CLIENT_ID, CLIENT_SECRET))
        # payment = client.order.create(data={
        #     "amount": total*100,
        #     "currency": "INR",
        #     "receipt": f"Rcpt_id{user.id}_{fid}"
        # })
        # context = {
        #     "KEY_ID": CLIENT_ID,
        #     "ORDER_ID": payment['id'],
        #     "AMOUNT": payment['amount'],
        #     "RECEIPT": payment['receipt'],
        #     "USER": {
        #         "Name": request.user.get_full_name(),
        #         "Email": request.user.email,
        #     }
        # }
        # return render(request, "Payment.html", context)
        return redirect("/myQRs/")
        # MAINPAYLOAD = {
        #     "merchantId": MERCHANT_ID,
        #     "merchantTransactionId": f"{user.id}_{fid}",
        #     "merchantUserId": user.id,
        #     "amount": total*100,
        #     "redirectUrl": "http://127.0.0.1:8000/res/",
        #     "redirectMode": "POST",
        #     "callbackUrl": "http://127.0.0.1:8000/res/",
        #     "mobileNumber": "",
        #     "paymentInstrument": {
        #         "type": "PAY_PAGE"
        #     }
        # }
        # endpoint = "/pg/v1/pay"
        # base64String = base64_encode(MAINPAYLOAD)
        # mainString = base64String + endpoint + SALTKEY
        # sha256Val = calculate_sha256_string(mainString)
        # checkSum = sha256Val + '###' + INDEX
        # headers = {
        #     'Content-Type': 'application/json',
        #     'X-VERIFY': checkSum,
        #     'accept': 'application/json',
        # }
        # json_data = {
        #     'request': base64String,
        # }
        # response = requests.post('https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/pay',
        #                          headers=headers, json=json_data)
        # response_data = response.json()
        # print(response_data)
        # return redirect(response_data['data']['instrumentResponse']['redirectInfo']['url'])
    else:
        data = list(File.objects.filter(user=request.user, fid=fid).values('fid', 'filename', 'pages', 'count'))
        context = {
            'files': [{"name": file['filename'],
                       "no": file['count'],
                       "pages": file['pages'],
                       "price": file['pages']*1.5,
                       } for file in data],
            'fid': fid,
            'price': {"Single": PRICE_SINGLE_SIDED, "Double": PRICE_DOUBLE_SIDED},
            'total': str(sum([file['pages']*PRICE_SINGLE_SIDED for file in data]))
        }
        print(context)
        return render(request, "PrintSettings.html", context)


@login_required(login_url="/login/")
def qrs_page(request):
    user = request.user
    fids, context = [], []
    files = list(File.objects.filter(user=user, Printed=False).values_list('fid', 'Subject', 'filename'))
    for file in files:
        if file[0] in fids:
            context[fids.index(file[0])]["files"].append(file[2])
        else:
            context.append({"fid": file[0], "subject": file[1], "files": [file[2], ], "qr_url": f"/qr/{file[0]}"})
            fids.append(file[0])
    return render(request, "MyQRs.html", {"context": context})


@csrf_exempt
def pay_status(request):
    form_data = request.POST
    transaction_id = form_data.get('transactionId', None)
    if transaction_id:
        request_url = 'https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/status/PGTESTPAYUAT/' + transaction_id
        sha256_Pay_load_String = '/pg/v1/status/PGTESTPAYUAT/' + transaction_id + SALTKEY
        sha256_val = calculate_sha256_string(sha256_Pay_load_String)
        checksum = sha256_val + '###' + INDEX
        headers = {
            'Content-Type': 'application/json',
            'X-VERIFY': checksum,
            'X-MERCHANT-ID': transaction_id,
            'accept': 'application/json',
        }
        response = requests.get(request_url, headers=headers)
        page_respond_data_varify = response.text
        print(page_respond_data_varify)
    return redirect("/myQRs/")


def verify_mail(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request,"activatesuccess.html")
    else:
        return render(request,"activatefail.html")
