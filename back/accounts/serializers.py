from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, Review, Comment, ReviewLike


User = get_user_model()  # 커스텀 User 모델 가져오기

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['genres']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    genres = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password2', 'genres']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "비밀번호가 일치하지 않습니다."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        genres = validated_data.pop('genres', [])
        
        # User 생성
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        
        # UserProfile 수동 생성
        UserProfile.objects.create(user=user, genres=genres)
        
        return user

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'username', 'created_at']
        read_only_fields = ['id', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()
    user_like_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'movie_id', 'movie_title', 'rating', 'content',
            'username', 'likes', 'dislikes', 'created_at', 'updated_at',
            'comments', 'comment_count', 'user_like_status'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'likes', 'dislikes']
    
    def get_comment_count(self, obj):
        return obj.comments.count()
    
    def get_user_like_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            like = ReviewLike.objects.filter(user=request.user, review=obj).first()
            if like:
                return 'like' if like.is_like else 'dislike'
        return None