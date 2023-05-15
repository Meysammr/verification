from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Post


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11, min_length=11)

    def validate_phone_number(self, value: str) -> str:
        if not (value.isnumeric() and value.startswith("09")):
            raise ValidationError("enter correct phone number")
        else:
            return value


class OTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11, min_length=11)
    otp_code = serializers.CharField(max_length=5)

    def validate_phone_number(self, value: str) -> str:
        if value.isnumeric()  and value.startswith('09'):
            return value
        else:
            return ValidationError("phone not correct")

    def validate_otp_code(self, value):
        if not str(value).isnumeric():
            raise ValidationError('otp code is not numeric')
        elif len(value) != 5:
            raise ValidationError(' please enter a correct otp code ')
        else:
            return value


class PostSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    text = serializers.CharField()


    class Meta:
        model = Post
        fields = ['id', 'owner', 'title', 'text', 'created_at', 'modified_at']
        read_only_fields = ['created_at', 'modified_at', 'id', 'owner']

    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance