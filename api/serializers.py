from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from .models import CheckResult, User, Monitor, Alert

class CheckResultSerializer(serializers.ModelSerializer):
    # All fields in this serializer class are read-only
    class Meta:
        model = CheckResult
        fields = '__all__'
        read_only_fields = ['monitor', 'status_code', 'response_time_ms', 'is_up', 'error_message', 'checked_at']


class MonitorSerializer(serializers.ModelSerializer):
    # only two fields are read-only
    class Meta:
        model = Monitor
        fields = '__all__'
        read_only_fields = ["owner", "created_at"]

    # validate url function
    def validate_url(self, url_val):
        # 1. get the user from request in context
        request = self.context.get("request")
        if not request or not request.user:
            return url_val

        # 2. Check if the url already exists and handle its exception
        user = request.user
        queryset = Monitor.objects.filter(owner=user, url=url_val)

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError("You're already monitoring this url")

        return url_val

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password"]
        extra_kwargs = {
            "password": {'write_only': True},
            "email": {"required": True}
        }

    # email validation function
    def validate_email(self, email_val):
        if User.objects.filter(email__iexact=email_val).exists():
            raise serializers.ValidationError("A user with similar email already exists")
        return email_val

    # pwd validation function
    def validate_password(self, pwd):
        try:
            validate_password(pwd)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return pwd

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

