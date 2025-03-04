from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
import phonenumbers
from django.core.validators import validate_email
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken


User = get_user_model()


# Custom refresh serializer
class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])

        # Check token rotation and blacklisting
        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

        data = {'refresh': str(refresh)}

        # Extract the user ID from the refresh token
        user_id = refresh.get('user_id')

        # Fetch the user object
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found.')

        # Generate a new access token
        access_token = AccessToken.for_user(user)

        # Update the access token with the latest user data
        access_token['phone'] = str(user.phone)
        access_token['email'] = str(user.email)
        access_token['first_name'] = str(user.first_name)
        access_token['middle_name'] = str(user.middle_name) if user.middle_name else ''
        access_token['last_name'] = str(user.last_name)
        access_token['avatar'] = str(user.avatar.url) if user.avatar else ''
        access_token['is_verified'] = user.is_verified

        data['access'] = str(access_token)

        return data



# Custom refresh serializer
class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])

        # Check token rotation and blacklisting
        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

        data = {'refresh': str(refresh)}

        # Extract the user ID from the refresh token
        user_id = refresh.get('user_id')

        # Fetch the user object
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found.')

        # Generate a new access token
        access_token = AccessToken.for_user(user)

        # Update the access token with the latest user data
        access_token['phone'] = str(user.phone)
        access_token['email'] = str(user.email)
        access_token['first_name'] = str(user.first_name)
        access_token['middle_name'] = str(user.middle_name) if user.middle_name else ''
        access_token['last_name'] = str(user.last_name)
        access_token['avatar'] = str(user.avatar.url) if user.avatar else ''
        access_token['is_verified'] = user.is_verified

        data['access'] = str(access_token)

        return data


# User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'phone',
            'first_name',
            'middle_name',
            'last_name',
            'username',
            'avatar',
            'password',
            "passport_or_id",
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'is_admin': {'read_only': True},
            'is_active': {'read_only': True},
            'is_verified': {'read_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(
            email=validated_data['email'],
            phone=validated_data['phone'],
            first_name=validated_data['first_name'],
            middle_name=validated_data.get('middle_name', ''),
            last_name=validated_data['last_name'],
            avatar=validated_data.get('avatar', None),
            passport_or_id=validated_data.get('passport_or_id', '')

        )
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.middle_name = validated_data.get('middle_name', instance.middle_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.passport_or_id = validated_data.get('passport_or_id', instance.passport_or_id)

        if password:
            instance.set_password(password)
        instance.save()
        return instance

# Custom token obtain pair serializer
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['phone'] = str(user.phone)
        token['email'] = str(user.email)
        token['first_name'] = str(user.first_name)
        token['middle_name'] = str(user.middle_name) if user.middle_name else ''
        token['last_name'] = str(user.last_name)
        token['avatar'] = str(user.avatar.url) if user.avatar else ''
        token['is_verified'] = user.is_verified

        return token

    @staticmethod
    def validate_and_format_phone(phone_number):
        # Remove any non-numeric characters from the phone number
        phone_number = ''.join(filter(str.isdigit, phone_number))

        # If the phone number starts with '254', remove it
        if phone_number.startswith('254'):
            phone_number = phone_number[3:]

        # If the phone number starts with '0', remove the leading zero
        if phone_number.startswith('0'):
            phone_number = '+254' + phone_number[1:]
        # If the phone number starts with '7', prepend '+254'
        elif phone_number.startswith('7'):
            phone_number = '+254' + phone_number
        # If the phone number starts with '254', prepend '+'
        elif phone_number.startswith('254'):
            phone_number = '+' + phone_number
        else:
            raise ValueError('Invalid phone number format')

        # Attempt to parse the phone number
        parsed_phone = phonenumbers.parse(phone_number, None)

        # Check if the parsed phone number is valid
        if not phonenumbers.is_valid_number(parsed_phone):
            raise ValueError('Invalid phone number')

        # Format the phone number in E.164 format
        formatted_phone_number = phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.E164)

        return formatted_phone_number

    def validate(self, attrs):
        email_or_phone = attrs.get('email')
        password = attrs.get('password')

        # Check if email_or_phone is a valid email address
        try:
            validate_email(email_or_phone)
            # If it's a valid email address, use it as the credential
            credentials = {'email': email_or_phone, 'password': password}
        except ValidationError:
            # If it's not a valid email address, assume it's a phone number
            # and filter the email using the phone number
            try:
                # Attempt to parse and validate the phone number
                valid_phone_number = self.validate_and_format_phone(email_or_phone)

                # Retrieve the user by the formatted phone number
                user = get_object_or_404(User, phone=valid_phone_number)
                credentials = {'email': user.email, 'password': password}
            except (phonenumbers.phonenumberutil.NumberParseException, User.DoesNotExist):
                raise serializers.ValidationError('Invalid credentials')

        return super().validate(credentials)


