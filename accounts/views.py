from .authentication import AccountActivationTokenGenerator
from django.conf import settings
from django.contrib.auth import (
    get_user_model,
    logout,
)
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import (
    force_bytes,
    force_text,
)
from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)
from .models import Token
from .permissions import (
    IsAdmin,
    IsAuthenticatedAndActive,
    IsOwnerOrReadOnly,
    IsOwnerOrAdmin,
)
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    CreateAPIView,
    ListCreateAPIView,
    RetrieveUpdateAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import AllowAny
from .serializers import (
    AdminUserListCreateSerializer,
    UserCreateSerializer,
    UserLoginSerializer,
    UserPasswordChangeSerializer,
    UserPasswordChangeTokenSerializer,
    UserPasswordResetSerializer,
    UserRetrieveUpdateSerializer,
    AdminUserRetrieveUpdateSerializer,
)
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView


User = get_user_model()


class UserActivateAPIView(APIView):
    """
    User activation endpoint. Activates the user account if the link is valid and has not expired.
    """
    permission_classes = (AllowAny,)

    def post(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user_obj = User.objects.get(id=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValidationError({'detail': 'User does not exists.'})
        if user_obj and AccountActivationTokenGenerator().check_token(user_obj, token):
            user_obj.is_active = True
            user_obj.save()
        else:
            raise ValidationError({'detail': 'Activation link is invalid.'})
        return Response({'detail': 'Your account has been activated.'})


class UserCreateAPIView(CreateAPIView):
    """
    User sing up endpoint.
    Returns the message about the sent activation link.
    """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            email = data['email']
            user_obj = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user_obj.id)).decode("utf-8")
            token = AccountActivationTokenGenerator().make_token(user_obj)
            send_email = self.send_activation_email(email, uid, token)
            if send_email:
                return Response({'detail': 'An activation e-mail has been sent to your email address.'})
            raise ValidationError({'detail': 'An activation e-mail has not been sent. \
                                              Please contact the administration.'})
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def send_activation_email(self, email, uid, token):
        user_obj = User.objects.get(email=email)
        subject = "Activate your account."
        activate_url = settings.UI_URL + settings.UI_ACCOUNT_ACTIVATE_PATH + uid + '/' + token + '/'
        msg_html = render_to_string('accounts/activate_account.html', {
            'first_name': user_obj.first_name,
            'activate_url': activate_url,
        })
        from_email = settings.DEFAULT_FROM_EMAIL
        new_email = send_mail(
            subject,
            msg_html,
            from_email,
            [user_obj.email],
            html_message=msg_html,
            fail_silently=False
        )
        return new_email


class UserLoginAPIView(APIView):
    """
    User sign in endpoint.
    Returns the user's email and token.
    """
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            new_data = serializer.data
            return Response(new_data)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class UserLogoutAPIView(APIView):
    """
    User logout endpoint. Sets the token to be invalid.
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            token = request.META['HTTP_AUTHORIZATION'][6:]
            token = Token.objects.get(key=token)
            logout(request)
            token.logout = True
            token.save()
        except (Token.DoesNotExist, KeyError):
            return Response({'detail': 'Token has not exists.'}, status=HTTP_400_BAD_REQUEST)
        return Response({'detail': 'You have successfully logged out.'})


class UserPasswordChangeAPIView(UpdateAPIView):
    """
    User password change endpoint.
    """
    serializer_class = UserPasswordChangeSerializer
    permission_classes = (IsAuthenticatedAndActive, IsOwnerOrReadOnly,)

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            instance.set_password(data['password_new'])
            instance.save()
            return Response({'detail': 'Password has been successfully updated'})
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class UserPasswordResetTokenAPIView(UpdateAPIView):
    """
    User password reset link endpoint.
    Changes the user's password if the passwords match and the link is valid and has not expired.
    """
    serializer_class = UserPasswordChangeTokenSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        try:
            uidb64 = self.kwargs['uidb64']
            uid = force_text(urlsafe_base64_decode(uidb64))
            user_obj = User.objects.get(id=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValidationError({'detail': 'User does not exists.'})
        return user_obj

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        token = self.kwargs['token']
        if instance and PasswordResetTokenGenerator().check_token(instance, token):
            data = request.data
            serializer = self.get_serializer(data=data)
            if serializer.is_valid(raise_exception=True):
                instance.set_password(data['password_new'])
                instance.save()
                return Response({'detail': 'Password has been successfully updated'})
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        raise ValidationError({'detail': 'Password Reset link is invalid.'})


class UserPasswordResetAPIView(APIView):
    """
    User password reset endpoint. Sends an email with a link to the page with the password change form.
    Returns the message about the sent password reset link.
    """
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = UserPasswordResetSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            email = data['email']
            user_obj = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user_obj.id)).decode("utf-8")
            token = PasswordResetTokenGenerator().make_token(user_obj)
            send_email = self.reset_password(email, uid, token)
            if send_email:
                return Response({'detail': 'E-mail with new password creation link has been sent.'})
            raise ValidationError({'detail': 'An e-mail with new password creation link has not been sent. \
                                             Please contact the administration.'})
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def reset_password(self, email, uid, token):
        user_obj = User.objects.get(email=email)
        subject = "Change your account password."
        password_reset_url = settings.UI_URL + '/account/password-reset/' + uid + '/' + token + '/'
        msg_html = render_to_string('accounts/password_reset.html', {
            'first_name': user_obj.first_name,
            'password_reset_url': password_reset_url,
        })
        from_email = settings.DEFAULT_FROM_EMAIL
        new_email = send_mail(
            subject,
            msg_html,
            from_email,
            [user_obj.email],
            html_message=msg_html,
            fail_silently=False
        )
        return new_email


class UserListCreateAPIView(ListCreateAPIView):
    """
    User list/create endpoint. Allowed for admin only.
    """
    queryset = User.objects.all()
    serializer_class = AdminUserListCreateSerializer
    permission_classes = (IsAdmin,)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """
    User retrieve/update endpoint. Allowed for admin and user with corresponding id.
    """
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedAndActive, IsOwnerOrAdmin,)

    def get_serializer_class(self):
        if self.request.user.is_admin:
            return AdminUserRetrieveUpdateSerializer
        return UserRetrieveUpdateSerializer
