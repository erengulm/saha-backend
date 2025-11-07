# members/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Registration fields in order for Turkish frontend:
    1. first_name (Adınız)
    2. last_name (Soyadınız)
    3. city (Yaşadığınız şehir)
    4. ilce (İlçe)
    5. mahalle (Mahalle)
    6. phone (Telefon)
    7. email (E-mail - will be used as username)
    8. password (Şifre)
    9. confirm_password (Şifre tekrar)

    Note: Email will be used as username for login
    """
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=30, required=True)
    city = serializers.CharField(max_length=100, required=True)
    ilce = serializers.CharField(max_length=100, required=True)
    mahalle = serializers.CharField(max_length=100, required=True)
    phone = serializers.CharField(max_length=15, required=False, allow_blank=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)  # Updated to match frontend
    confirm_password = serializers.CharField(write_only=True)
    role = serializers.CharField(default='member', required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'city', 'ilce', 'mahalle', 'phone', 'email', 'password', 'confirm_password', 'role')

    def validate(self, attrs):
        if attrs['password'] != attrs.get('confirm_password'):
            raise serializers.ValidationError({"confirm_password": "Şifreler eşleşmiyor."})
        return attrs

    def validate_email(self, value):
        # Convert to lowercase for consistency
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu e-posta adresi ile kayıtlı bir kullanıcı zaten mevcut.")
        return value

    def validate_phone(self, value):
        if value:
            # Turkish phone number validation
            import re
            # Remove spaces and dashes for validation
            clean_phone = value.replace(' ', '').replace('-', '')
            phone_pattern = r'^(\+90|0)?[5][0-9]{9}$'
            if not re.match(phone_pattern, clean_phone):
                raise serializers.ValidationError(
                    "Lütfen geçerli bir Türk telefon numarası giriniz. (Örn: 05XXXXXXXXX)")

            # Check if phone number already exists
            if User.objects.filter(phone=value).exists():
                raise serializers.ValidationError("Bu telefon numarası ile kayıtlı bir kullanıcı zaten mevcut.")
        return value

    def validate_role(self, value):
        """Ensure only valid roles are accepted"""
        valid_roles = ['superadmin', 'admin', 'member']
        if value not in valid_roles:
            raise serializers.ValidationError(f"Geçersiz rol. Şunlardan biri olmalıdır: {', '.join(valid_roles)}")
        return value

    def validate_password(self, value):
        """Custom password validation"""
        if len(value) < 8:
            raise serializers.ValidationError("Şifre en az 8 karakter olmalıdır.")
        return value

    def create(self, validated_data):
        # Remove confirm_password from validated_data
        validated_data.pop('confirm_password')

        # Set email as the main identifier (no username needed)
        email = validated_data.get('email').lower().strip()
        validated_data['email'] = email

        # Create user with proper password hashing - use create_user without username
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=30, required=False)
    city = serializers.CharField(max_length=100, required=False)
    ilce = serializers.CharField(max_length=100, required=False)
    mahalle = serializers.CharField(max_length=100, required=False)
    phone = serializers.CharField(max_length=15, required=False, allow_blank=True)
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'city', 'ilce', 'mahalle', 'phone', 'email')

    def validate_email(self, value):
        user = self.instance
        # Convert to lowercase for consistency
        value = value.lower().strip()
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Bu e-posta adresi ile kayıtlı başka bir kullanıcı mevcut.")
        return value

    def validate_phone(self, value):
        if value:
            # Turkish phone number validation
            import re
            clean_phone = value.replace(' ', '').replace('-', '')
            phone_pattern = r'^(\+90|0)?[5][0-9]{9}$'
            if not re.match(phone_pattern, clean_phone):
                raise serializers.ValidationError(
                    "Lütfen geçerli bir Türk telefon numarası giriniz. (Örn: 05XXXXXXXXX)")

            # Check if phone number already exists (excluding current user)
            user = self.instance
            if User.objects.filter(phone=value).exclude(pk=user.pk).exists():
                raise serializers.ValidationError("Bu telefon numarası ile kayıtlı başka bir kullanıcı mevcut.")
        return value

    def update(self, instance, validated_data):
        # Update email and username together
        if 'email' in validated_data:
            new_email = validated_data['email'].lower().strip()
            instance.email = new_email
            instance.username = new_email
            validated_data.pop('email')  # Remove from validated_data to avoid double processing

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)  # Updated to match frontend
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Yeni şifreler eşleşmiyor."})
        return attrs

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mevcut şifre yanlış.")
        return value

    def validate_new_password(self, value):
        user = self.context['request'].user
        if len(value) < 8:
            raise serializers.ValidationError("Yeni şifre en az 8 karakter olmalıdır.")
        if user.check_password(value):
            raise serializers.ValidationError("Yeni şifre mevcut şifreden farklı olmalıdır.")
        return value