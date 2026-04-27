from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, get_user_model
from .serializers import UserSerializer, UserProfileSerializer, ReviewSerializer, CommentSerializer
from .models import Review, Comment, ReviewLike
import requests
import json
import os
from django.conf import settings

User = get_user_model()  # 커스텀 User 모델 가져오기

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """회원가입"""
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        # 중복 체크
        if User.objects.filter(username=request.data.get('username')).exists():
            return Response(
                {'error': '이미 존재하는 아이디입니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'genres': user.profile.genres
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """로그인"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': '아이디와 비밀번호를 입력해주세요.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'genres': user.profile.genres
            }
        })
    
    return Response(
        {'error': '아이디 또는 비밀번호가 잘못되었습니다.'},
        status=status.HTTP_401_UNAUTHORIZED
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """로그아웃"""
    try:
        request.user.auth_token.delete()
        return Response({'message': '로그아웃 되었습니다.'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """프로필 조회"""
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'genres': user.profile.genres
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """프로필 업데이트"""
    profile = request.user.profile
    serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'id': request.user.id,
            'username': request.user.username,
            'genres': profile.genres
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def review_list(request):
    """리뷰 목록 조회 / 생성"""
    if request.method == 'GET':
        movie_id = request.query_params.get('movie_id')
        
        if movie_id:
            reviews = Review.objects.filter(movie_id=movie_id)
        else:
            reviews = Review.objects.all()
        
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response(
                {'error': '로그인이 필요합니다.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def review_detail(request, review_id):
    """리뷰 상세 조회 / 수정 / 삭제"""
    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return Response(
            {'error': '리뷰를 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = ReviewSerializer(review, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if review.user != request.user:
            return Response(
                {'error': '수정 권한이 없습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if review.user != request.user:
            return Response(
                {'error': '삭제 권한이 없습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        review.delete()
        return Response({'message': '리뷰가 삭제되었습니다.'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_like(request, review_id):
    """리뷰 좋아요/싫어요"""
    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return Response(
            {'error': '리뷰를 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    is_like = request.data.get('is_like')
    
    if is_like is None:
        return Response(
            {'error': 'is_like 값이 필요합니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    existing_like = ReviewLike.objects.filter(user=request.user, review=review).first()
    
    if existing_like:
        if existing_like.is_like == is_like:
            if is_like:
                review.likes -= 1
            else:
                review.dislikes -= 1
            existing_like.delete()
            review.save()
            return Response({'message': '취소되었습니다.', 'status': None})
        
        else:
            if is_like:
                review.likes += 1
                review.dislikes -= 1
            else:
                review.dislikes += 1
                review.likes -= 1
            
            existing_like.is_like = is_like
            existing_like.save()
            review.save()
            return Response({'message': '변경되었습니다.', 'status': 'like' if is_like else 'dislike'})
    
    else:
        ReviewLike.objects.create(user=request.user, review=review, is_like=is_like)
        if is_like:
            review.likes += 1
        else:
            review.dislikes += 1
        review.save()
        return Response({'message': '등록되었습니다.', 'status': 'like' if is_like else 'dislike'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_create(request, review_id):
    """댓글 생성"""
    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return Response(
            {'error': '리뷰를 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user, review=review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def comment_delete(request, comment_id):
    """댓글 삭제"""
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response(
            {'error': '댓글을 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if comment.user != request.user:
        return Response(
            {'error': '삭제 권한이 없습니다.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    comment.delete()
    return Response({'message': '댓글이 삭제되었습니다.'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_ai_recommendations(request):
    """GMS GPT API를 사용한 영화 DNA 분석 및 추천"""
    
    print("=== AI 추천 요청 시작 (DNA 분석 포함) ===")
    
    movie_titles = request.data.get('movie_titles', [])
    print(f"영화 목록: {movie_titles}")
    
    if not movie_titles:
        return Response(
            {'error': '영화 목록이 비어있습니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        movie_list_str = ', '.join(movie_titles)
        
        # GMS API 키
        GMS_API_KEY = settings.GMS_API_KEY
        
        print(f"GMS API 호출 중... (영화: {movie_list_str})")
        
        # GMS API 호출 - DNA 분석 포함
        gms_response = requests.post(
            'https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {GMS_API_KEY}'
            },
            json={
                'model': 'gpt-4o-mini',
                'messages': [
                    {
                        'role': 'developer',
                        'content': 'Answer in Korean'
                    },
                    {
                        'role': 'user',
                        'content': f"""사용자가 찜한 영화 목록: {movie_list_str}

1단계: 먼저 이 영화들의 DNA를 분석해주세요.
- 선호하는 장르 (상위 3개, 비율 포함)
- 반복되는 테마/주제 (3-5개)
- 선호하는 분위기/톤
- 자주 등장하는 감독 스타일

2단계: 분석된 DNA를 바탕으로 사용자가 좋아할 만한 영화 5개를 추천해주세요.

반드시 다음 JSON 형식으로만 답변하세요:
{{
  "dna_analysis": {{
    "genres": ["장르1 70%", "장르2 50%", "장르3 30%"],
    "themes": ["테마1", "테마2", "테마3"],
    "mood": "분위기 설명 (한 문장)",
    "director_style": "감독 스타일 설명 (한 문장)"
  }},
  "explanation": "DNA 기반 추천 설명 (한 문장)",
  "movies": [
    {{
      "title": "영화 제목",
      "reason": "이 영화가 당신의 DNA와 맞는 이유 (한 문장)"
    }}
  ]
}}"""
                    }
                ]
            },
            timeout=30
        )
        
        print(f"GMS 응답 상태: {gms_response.status_code}")
        
        if gms_response.status_code == 200:
            data = gms_response.json()
            print(f"GMS 응답 데이터: {data}")
            
            # GPT 응답에서 텍스트 추출
            if 'choices' in data and len(data['choices']) > 0:
                message = data['choices'][0].get('message', {})
                content = message.get('content', '')
                
                print(f"GPT 응답 내용 (처음 200자): {content[:200]}")
                
                # JSON 파싱
                try:
                    # { 로 시작하는 부분 찾기
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    
                    if json_start != -1 and json_end > json_start:
                        json_str = content[json_start:json_end]
                        print(f"추출된 JSON: {json_str[:200]}")
                        
                        ai_result = json.loads(json_str)
                        print(f"파싱 성공! DNA 분석 포함됨")
                        
                        return Response(ai_result, status=status.HTTP_200_OK)
                    else:
                        print(f"JSON을 찾을 수 없음. 전체 내용: {content}")
                        return Response(
                            {'error': 'AI 응답에서 JSON을 찾을 수 없습니다'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
                        
                except json.JSONDecodeError as e:
                    print(f"JSON 파싱 에러: {e}")
                    return Response(
                        {'error': f'JSON 파싱 실패: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                print(f"응답에 choices가 없음: {data}")
                return Response(
                    {'error': 'AI 응답 형식 오류'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            error_text = gms_response.text
            print(f"GMS API 에러 {gms_response.status_code}: {error_text}")
            return Response(
                {'error': f'GMS API 오류: {gms_response.status_code}', 'detail': error_text},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except requests.exceptions.Timeout:
        print("타임아웃 발생")
        return Response(
            {'error': '요청 시간이 초과되었습니다.'},
            status=status.HTTP_504_GATEWAY_TIMEOUT
        )
    except requests.exceptions.RequestException as e:
        print(f"네트워크 에러: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'네트워크 오류: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        print(f"예상치 못한 에러: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'서버 오류: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )