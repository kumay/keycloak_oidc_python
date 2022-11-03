import urllib.parse as parse
import os
import requests
import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import RedirectResponse, PlainTextResponse
import jwt
import secrets
from dotenv import dotenv_values

config = dotenv_values(".env")

# Applicatuon settings
APP_BASE_URL = config.get("APP_BASE_URL")
APP_CLIENT_ID = config.get("APP_CLIENT_ID")
APP_CLIENT_SECRET = config.get("APP_CLIENT_SECRET")
APP_REDIRECT_URI = config.get("APP_REDIRECT_URI")
APP_LOGOUT_REDIRECT_URL = f"{APP_BASE_URL}/auth/logout/callback"

# Keycloak Settings
KEYCLOAK_BASE_URL_LOCALHOST = config.get("KEYCLOAK_BASE_URL_LOCALHOST") 
KEYCLOAK_REALM = config.get("KEYCLOAK_REALM")

# Authorization Endpoint
AUTH_BASE_URL = f"{KEYCLOAK_BASE_URL_LOCALHOST}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth"

# Token Endpoint
TOKEN_URL = f"{KEYCLOAK_BASE_URL_LOCALHOST}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"

LOGOUT_URL = f"{KEYCLOAK_BASE_URL_LOCALHOST}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/logout"


# Public Key for RS256
RSA_PUBLIC_KEY_BODY = config.get("RSA_PUBLIC_KEY_BODY")
RSA_PUBLIC_KEY = "-----BEGIN RSA PUBLIC KEY-----\n" \
                  + RSA_PUBLIC_KEY_BODY \
                  + "\n-----END RSA PUBLIC KEY-----"

app = FastAPI()

# Redirect to Keycloak Authorization Endpoint for login
# use state to track the login flow
@app.get("/auth/login")
async def login() -> RedirectResponse:
    state = secrets.token_urlsafe(32)
    AUTH_URL = AUTH_BASE_URL + '?{}'.format(parse.urlencode({
        'client_id': APP_CLIENT_ID,
        'redirect_uri': APP_REDIRECT_URI,
        'scope': 'openid',
        'state': state,
        'response_type': 'code'
    }))
    response = RedirectResponse(AUTH_URL)
    response.set_cookie(key="AUTH_STATE", value=state)
    return response


# Token Request
def get_token(code):
    params = {
        'client_id': APP_CLIENT_ID,
        'client_secret': APP_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': APP_REDIRECT_URI,
        'code': code
    }
    token_response = requests.post(TOKEN_URL, params, verify=False)
    token = token_response.json()
    return token


# Callback Endpoint. Recieving the redirect from Keycloak
# check the state in GET parameter with stored state value in Cookie
@app.get("/auth/callback")
async def auth(request: Request, code: str, state: str) -> RedirectResponse:
    if state != request.cookies.get("AUTH_STATE"):
        return {"error": "state_verification_failed"}
    token = get_token(code)
    response = RedirectResponse("/my")
    # Store information in cookie.
    # Set following cookie values for security purpose, 
    # - Secure; (Limit Cookie access to connection over SSL. ) 
    # - HttpOnly (Avoid javascript access),
    # - SameSite=Strict (prevents some CSRF attacks)
    # - Domain=myapp.com, (Restrict which domaincan access the Cookies)
    # - Expires=<data time> (Cookie expiration timing)
    response.set_cookie(key="ACCESS_TOKEN", value=token.get("access_token"))
    response.set_cookie(key="ID_TOKEN", value=token.get("id_token"))
    response.set_cookie(key="REFRESH_TOKEN", value=token.get("refresh_token"))
    return response


@app.get("/")
async def index(request: Request) -> PlainTextResponse:
    return "Top page !!!"


@app.get("/my")
async def user_my_page(request: Request) -> PlainTextResponse:
    id_token = request.cookies.get("ID_TOKEN")
    access_token= request.cookies.get("ACCESS_TOKEN")
    decoded_id_token = jwt.decode(jwt=id_token, key=RSA_PUBLIC_KEY, audience=APP_CLIENT_ID, algorithms="RS256")
    decoded_access_token = jwt.decode(jwt=access_token, key=RSA_PUBLIC_KEY, audience="account", algorithms="RS256")
    return decoded_id_token, decoded_access_token


@app.get("/auth/logout")
async def logout(request: Request) -> RedirectResponse:
    
    # This will do logout and redirect back to the application logout callback endpoint
    id_token = request.cookies.get("ID_TOKEN")
    get_param = parse.urlencode({"client_id": APP_CLIENT_ID,
                                 "post_logout_redirect_uri": APP_LOGOUT_REDIRECT_URL,
                                 "id_token_hint": id_token})

    # This will logout from Keyclaok and logged out page is served in keyclaok
    # get_param = parse.urlencode({"client_id": APP_CLIENT_ID})
    
    url = LOGOUT_URL + "?{}".format(get_param)

    return RedirectResponse(url)


@app.get("/auth/logout/callback")
async def logout(request: Request) -> RedirectResponse:
    # Do clean up and redirect to some endpoint.
    response = RedirectResponse("/")

    # Delete stored information in cookie.
    response.delete_cookie("ID_TOKEN")
    response.delete_cookie("ACCESS_TOKEN")
    response.delete_cookie("REFRESH_TOKEN")
    response.delete_cookie("AUTH_STATE")
    return response


if __name__ == "__main__":
    uvicorn.run(app, port=8000, loop="asyncio")
