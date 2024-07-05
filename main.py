import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from starlette.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from controller import Oauth
from model import UserModel, UserData
from settings import settings
app = FastAPI()

@AuthJWT.load_config
def get_config():
    return settings

# JWT 예외 처리
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
@app.get("/")
def root():
    return "hello"

@app.get("/index")
def index():
    return FileResponse('static/templates/index.html')
@app.get("/oauth/url")
def oauth_url_api():
    """
    카카오 OAuth URL 가져오기
    """
    kakao_oauth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={settings.client_id}&redirect_uri={settings.redirect_uri}&response_type=code"
    return JSONResponse(content={"kakao_oauth_url": kakao_oauth_url})

@app.get("/data")
def name():
    return {'hello':1234}

@app.get("/oauth")
async def oauth_api(code : str, Authorize: AuthJWT = Depends()):#url에서 가져온 code의 값이 accesstoken을 받아오기 위한 임시 토큰의 역할
    oauth = oauth = Oauth(
        client_id=settings.client_id,
        client_secret=settings.client_secret,
        redirect_uri=settings.redirect_uri
    )
    auth_info = oauth.auth(code)#oauth_info에 access_token, refresh_token, 만료 시간 등등.. 이 저장됨

    user = oauth.userinfo("Bearer "+auth_info['access_token'])##회원 정보 응답값들이 저장됨

    user = UserData(user)
    UserModel().upsert(user)

    access_token = Authorize.create_access_token(subject=user.id)
    refresh_token = Authorize.create_refresh_token(subject=user.id)

    return {
        "auth_info": auth_info,
        "user_info": user.serialize(),
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@app.get("/user/{user_id}")
def get_user(user_id: str):
    user = UserModel.get_user(user_id)
    if user:
        return user.serialize()
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.delete("/user/{user_id}")
def delete_user(user_id: str):
    UserModel.remove_user(user_id)
    return {"detail": "User deleted"}


if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)