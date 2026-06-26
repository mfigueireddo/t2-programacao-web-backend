"""Serializers do domínio de Usuários (Users).

Define a tradução entre instâncias do modelo :class:`users.models.User` e a
representação JSON produzida pela API REST. Por ora, expõe apenas os dados
necessários para que o frontend descubra o papel (permissão) de um usuário.
"""

"""Serializers do domínio de Usuários e autenticação."""

from rest_framework import serializers

from .models import AuthToken, PasswordResetToken, User


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'role', 'role_display', 'created_at']
        read_only_fields = ['id', 'role_display', 'created_at']


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'name', 'password', 'role']
        read_only_fields = ['id']

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError('O nome é obrigatório.')

        if User.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError('Já existe um usuário com esse nome.')

        return value

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    name = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        name = attrs.get('name', '').strip()
        password = attrs.get('password', '')

        try:
            user = User.objects.get(name=name)
        except User.DoesNotExist:
            raise serializers.ValidationError('Nome ou senha inválidos.')

        if not user.check_password(password):
            raise serializers.ValidationError('Nome ou senha inválidos.')

        attrs['user'] = user
        return attrs


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    user = UserSerializer()


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_current_password(self, value):
        user = self.context['request'].user

        if not user.check_password(value):
            raise serializers.ValidationError('Senha atual incorreta.')

        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()

        AuthToken.objects.filter(user=user).delete()

        return user


class ForgotPasswordSerializer(serializers.Serializer):
    name = serializers.CharField()

    def validate_name(self, value):
        try:
            return User.objects.get(name=value.strip())
        except User.DoesNotExist:
            raise serializers.ValidationError('Usuário não encontrado.')

    def save(self):
        user = self.validated_data['name']
        return PasswordResetToken.create_for_user(user)


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_token(self, value):
        try:
            reset_token = PasswordResetToken.objects.select_related('user').get(
                token=value,
                used=False,
            )
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError('Token inválido.')

        if reset_token.is_expired:
            raise serializers.ValidationError('Token expirado.')

        return reset_token

    def save(self):
        reset_token = self.validated_data['token']
        user = reset_token.user

        user.set_password(self.validated_data['new_password'])
        user.save()

        reset_token.used = True
        reset_token.save(update_fields=['used'])

        AuthToken.objects.filter(user=user).delete()

        return user