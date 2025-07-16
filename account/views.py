# account/views.py

from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.urls import reverse
from django.contrib.auth import (login,          # 로그인 처리 함수
                                 logout,         # 로그아웃 처리 함수
                                 authenticate,   # 인증 확인 함수 (username, password를 DB에서 확인)
                                 update_session_auth_hash
                                 # 회원정보 수정 시 로그인 상태유지를 위해 저장된 User 모델 객체를 수정된 내용으로 변경하는 함수
                                 )   
from django.contrib.auth.decorators import login_required

#################################
# 사용자 가입 처리
# 요청 url : account/create
#   GET - 가입 폼 양식을 응답
#   POST - 가입처리
# 응답: GET - templates/account/create.html
#       POST - home으로 이동. redirect

def create(request):
    if request.method == "GET":
        return render(request, "account/create.html", {"form":CustomUserCreationForm()})
    else:   # POST
        # 가입 처리
        # 1. 요청 parameter 조회
        form = CustomUserCreationForm(request.POST, request.FILES)
        # 요청 parameter로 넘어온 값을 Form의 instance 변수(attribute)에 저장.

        # 2. 요청 parameter 검증
        ## form.is_valid() : bool -> T : 검증성공, F : 검증 실패
        if form.is_valid():     # 검증 성공 -> 가입 처리
            # form : ModelForm은 save() 기능 제공 -> DB insert 
            # 반환값 : insert 처리한 결과를 가진 Model
            user = form.save()
            print("===== 가입 : user :", type(user), user)
            return redirect(reverse("home"))
        else:   # 검증 실패 -> 실패 처리, 가입 화면으로 이동
            return render(request, "account/create.html", {"form" : form})  # 요청 parameter와 검증결과를 가진

############################
# Login 처리 view
# 요청 url : /account/login
# view : user_login
#   - GET : Login form 제공
#   - POST : Login 처리
# template
#   - GET : templates/account/login.html, POST : home(redirect)

def user_login(request):
    if request.method == "GET":
        # login form 응답
        return render(request, "account/login.html", {"form" : AuthenticationForm()})
    else:
        # login 처리 -> username / password 확인 -> login 상태 유지 처리
        # username / password 조회
        username = request.POST["username"]
        password = request.POST["password"]
        
        # User모델(settings.AUTH_USER_MODEL)을 기반으로 사용자 인증 처리, DB로 부터 username, password 확인
        ## 유효한 username / password면 User모델 객체 반환
        ## 유효하지 않은 경우 None 반환
        user = authenticate(request, username = username, password = password)
        if user is not None:
            # 유효한 user 계정
            login(request, user)    # login 처리 (login 상태 유지)

            next_url = request.GET.get("next")
            if next_url is not None: # account/login?next=/poll/vote_create
                return redirect(next_url)
            return redirect(reverse("home"))

        else :
            # 유효하지 않은 사용자 계정            
            return render(request, "account/login.html", 
                          { "form" : AuthenticationForm(), 
                           "error_message" : "아디나 비번이 틀림 😭"})
        
########################
# Logout 처리
# url : /account/logout
# view : user_logout
# template : redirect 방식 -> home

@login_required
def user_logout(request):
    logout(request)     # logout 처리.
    return redirect(reverse("home"))

###############################
# 사용자 정보를 조회하는 View
#   - 단순히 template만 실행해서 응답하는 View
#   - TemplateView.as_view(template_name="template경로")

# def detail(request):
#     return render(request, "account/detail.html")


################################
# 패스워드 수정 처리 View
# 요청 url: /account/password_change
# view함수: password_change
#   - GET: 패스워드 변경 폼을 응답(template: account/password_change.html)
#   - POST: 패스워드 변경 처리    (template: account/detail - redirect)
def password_change(request):
    if request.method == "GET":
        # PasswordChangeForm을 비밀번호를 변경할 User 모델을 넣어서 생성 - 기존 패스워드 확인용
        # login_user = get_user(requset) # django.contrib.auth.get_user -> 로그인한 UserModel
        login_user = request.user
        form = PasswordChangeForm(login_user)
        return render(
            request, "account/password_change.html", {"form":form}
        )
    else:
        # 요청파라미터 조회 -> 검증(Form)
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid(): # 요청파라미터 검증 통과
            # DB Update
            user = form.save() # ModelForm.save(): update(o)/insert
            # 로그인 유지를 위해 저장된 User Model객체를 업데이트된 User Model로 변경
            update_session_auth_hash(request, user)
            return redirect(reverse("account:detail"))
        else: # 요청파라미터에 문제가 있는 경우
            return render(request, "account/password_change.html",{"form":form})
        
###################################
# 회원정보 수정
# 요청 URL: account/update
# view함수: user_update
#   GET - 수정 양식페이지로 이동. (template: account/update.html)
#   POST - 수정 처리 (account/detail : redirect)
@login_required
def user_update(request):

    if request.method == "GET":
        # 수정 양식 template 반환
        ## 로그인한 사용자의 User Model객체를 전달해서 Form생성
        form = CustomUserChangeForm(instance=request.user)
        return render(request, "account/update.html", {"form":form})
    else:
        # 수정 처리
        ## 1. 요청 파라미터 조회 + 검증
        form = CustomUserChangeForm(request.POST, request.FILES, instance = request.user)
        if form.is_valid():
            # 저장
            user = form.save()
            # 로그인 사용자 정보 갱신
            update_session_auth_hash(request, user)
            return redirect(reverse("account:detail"))
        else:
            # 검증 실패 -> 수정폼(update.html)로 이동
            return render(request, "account/update.html", {"form":form})

############################
# 회원 탈퇴 - 삭제처리
#  - 요청 url: account/delete
#  - view 함수: user_delete
#  - 응답: home으로 이동 - redirect
@login_required
def user_delete(request):
    # DB에서 user정보를 삭제
    ## 데이터 삭제 - model(pk).delete()
    request.user.delete()
    # 로그아웃
    logout(request)
    return redirect(reverse("home"))

# 일반데이터를 삭제하는 경우(제품, 게시판 글 삭제...)
# 1. 삭제할 데이터의 PK값을 요청파라미터/Path 파라미터로 받는다.
# 2. Model 이용해서 삭제할 데이터를 조회(1의 PK를 이용해서)
   #  q = Question.objects.get(pk=pk)
   #  q = Question(pk=pk)
# 3. 2번의 Model.delete()
   #  q.delete()