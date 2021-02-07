from django.shortcuts import render
from rest_framework import generics, status
from .serializers import SetNewPasswordSerializer, ResetPasswordEmailRequestSerializer, LoginSerializer,RegisterSerializer, EmailVerificationSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .renderers import UserRenderer
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode



class RegisterView(generics.GenericAPIView):

    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,) 

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user=User.objects.get(email=user_data['email'])

        token = RefreshToken.for_user(user).access_token

        current_site =get_current_site(request).domain
        relativeLink= reverse('email-verify')
        absurl = 'http://'+current_site+relativeLink+'?token='+str(token)
        email_body = 'Hola ' + user.username + ' Usa este link para comprobar tú email.\n ' + absurl +'\n\n\n\n Si no reconoces esta opearación ignora o comunícate con un Admnistrador.'
        data={
            'email_body': email_body,
            'to_email': user.email,
            'email_subject':'Verifica tu email',
        }
        Util.send_email(data)
        return Response(user_data, status=status.HTTP_201_CREATED)

class VerifyEmail(APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, 
        description='Description', 
        type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:    
                user.is_verified = True
                user.save()
            return Response({'email': 'Se ha activado satisfactoriamente ...!!'}, status=status.HTTP_200_OK)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Token invalido..!!'}, status=status.HTTP_400_BAD_REQUEST)         
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Ha caducado tú token ...!!'}, status=status.HTTP_400_BAD_REQUEST)

class LoginApiView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def post(self, request): 
        serializer = self. serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class= ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        email = request.data['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)               
            uidb64 =  urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site =get_current_site(request= request).domain
            relativeLink= reverse('password-reset', kwargs={'uidb64':uidb64, 'token':token})
            # redirect_url = request.data.get('redirect_url', '')
            absurl = 'http://'+current_site+relativeLink
            email_body = ' Hola '+user.username+'. \n\n Escuchamos que olvidaste tú contraseña pero no te preocupes....!!! \n\n Usa el siguiente link y podrás restuarar tú contraseña. \n'+absurl+'\n\n\n\n Si no utilizas este codigo en 3hrs expirará. \n\n Si no reconoces esta opearación ignora o comunícate con un Admnistrador.  \n Saludos. \n Equipo Caduceo.'
            data={
                'email_body': email_body,
                'to_email': user.email,
                'email_subject':'Recuperar Password',
            }
            Util.send_email(data)
        return Response({'success': 'Nosotros te mandaremos un correo para recuperar tú password.'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):

    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):
        try:
            id=smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error':'Tu token es invalido'}, status=status.HTTP_401_UNAUTHORIZED)
       
            
            return Response({'success':True, 'message':'Informacion Validada...!!!', 'uidb64':uidb64, 'token': token}, status=status.HTTP_200_OK)
            
        except DjangoUnicodeDecodeError as identifier:
            if not PasswordResetTokenGenerator().check_token(user):
                return Response({'error':'Tu token es invalido'}, status=status.HTTP_401_UNAUTHORIZED)

class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Se ha restaurado tú contraseña satisfactorimente..!!'}, status=status.HTTP_200_OK) 