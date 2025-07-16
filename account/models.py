# account/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

# User model 등록
## AbstractUesr를 상속 받아서 확장 User model로 def

class User(AbstractUser):
    # username / password를 제외한 나머지 Field 정의
    name = models.CharField(
        # Form 관련 설정, ModelForm을 만들 경우 form 관련 설정을 model field에 할 수 있당.
        verbose_name= "이름",
        max_length= 50,  # varchar(50)
        default="None"
    )
    # varchar(100) -> 검증 기능 추가, 값이 email 형식(문자열@문자열)인지 여부 검증
    email = models.EmailField(verbose_name="Email", max_length=100, default="None")
    birthday = models.DateField(
        verbose_name = "생일",
        null = True,    # nullable
        blank = True,   # 입력 form 설정, 빈 값 입력 가능 여부(default : False - required)
    )
    # 프로필 이미지 업로드 받는 model field
    profile_img = models.ImageField(
        verbose_name="프로필 사진",
        upload_to="images/%Y/%m/%d", # 업로드 파일을 저장할 경로. (MEDIA_ROOT/지정한 경로)
        null = True,
        blank = True
    )

    def __str__(self):
        return f"{self.username} - {self.name}"

# settings.py에 사용자 정의 User 모델 등록
# database 삭제 (db.sqlite3파일)
# python manage.py makemigrations
# python manage.py migrate