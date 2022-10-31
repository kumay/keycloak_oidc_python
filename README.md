# Preparing Keycloak for OpenID connect

### 1. run kaycloak using docker

```
$ docker run -p 8080:8080 -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak:19.0.3 my-keycloak
```

### 2. create realm

| Setting | Parameter | value |
|---------|-----------|-------|
| Realm Setting | Name | My Realm |
| Realm Setting | User managed access | ON |
| Client scopes | roles | Default |
| Client scopes | profile | Default |
| Clinet scopes | email | Default |


Add some Roles.
Such as "dev", "dev admin", "back office", "admin"


### 3. create client

| Setting | Tab | Parameter | value |
|---------|-----|-----------|-------|
| Clients | Settings | Client ID | My Client |
| Clients | Settings | Name | My Client |
| Clients | Settings | Always display in console | ON |
| Clients | Settings | Root URL | http://MY-APP-URL:PORT |
| Clients | Settings | Valid redirect URLs | http://MY-APP-URL:PORT/auth/callback |
| Clients | Settings | Client authentication | ON |
| Clients | Settings | Authentication flow: Standard flow | ON |
| Clients | Settings | Authentication flow: Direct access grants | ON |
| Clients | Settings | Authentication flow: Service account role | ON |
| Clients | Settings | Authentication flow: Service account role | ON |
| Clients | Credentials | Client Authenticator | Client ID and Secret |
| Clients | Credentials | Client Authenticator | Client ID and Secret |
| Clients | Roles | Create role | "dev" |
| Clients | Roles | Create role | "dev admin" |
| Clients | Roles | Create role | "back office" |
| Clients | Roles | Create role | "admin" |
| Clients | Client scopes | profile | Default |
| Clients | Client scopes | roles | Default |
| Clients | Advance | Authentication flow overrides: Browser Flow | browser |
| Clients | Advance | Authentication flow overrides: Direct Grant Flow | direct grant |


### 4. Add user for login test

**Do not forget to set credencial (i.e password)** 


**Example Login URL**

http://localhost:8080/realms/app/protocol/openid-connect/auth?client_id=account-console&\
    redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Frealms%2Fapp%2Faccount%2F%23%2F&\
    state=eb0042a24dd143ca969fb915142e49ce&\
    response_mode=fragment&\
    response_type=code&\
    scope=openid&\
    nonce=e18aa2b8-1857-4df9-86fa-034928117810&\
    code_challenge=vz9b5W5hjQ0LIpucJxQNiMGK7ss5-lluC8-KGvi8h9I&\
    code_challenge_method=S256


**RSA public key**

Need to be in following format.
-----BEGIN RSA PUBLIC KEY-----
<..public key string...>
-----END RSA PUBLIC KEY-----

Example:

-----BEGIN RSA PUBLIC KEY-----
MIICWwIBACKBgQCUn8GgYNw49UCmHZl0cmbHQucMJEPZQoCzisBG3D80jlhea6di
dPrPHNhb9jNNOY2W4Ip6AfggbpFeemUhPhD88yz8Y9ntNzH0ztES6JV5lSyhOKLn
f+pccfXvHExxxWWWWWWWWWWWWWWWWWXXXXXXxxxxxxxxxxxxxxxxQJAvkQIDAQAB
AoGAdUiAnSPtFbnME4qGH5tr+dC0zWMM27TcJVLYKdFhW1L9Lz2x8FpJ1gj4P9CI
MUe6kRaOkDtfaBB4zOqfR6VaB13OMSn3JnXeP4VpzFpFYKJCeKfxnbiIFMqzarfg
Kk8FSVHxS43pZQtQQQQQQQQQQQQQQQQQQQQQQQQQQQQc80ECQQDxglcCfssFioVe
PSWOoi6LX5Gxky2StoiUgyAH6RDtDZDhJi5pHgwtPWJkqvKTmoJEgp8A7Qvn8eCl
5A2xuN3JA6EAswpiamr8gme09Z9f5dbTd62fKMq+n5eVa/C9Uqt8FGTCOcjELp6z
z4km7rgz7aaaaaaaaaafffffffffffffffffaaaaaaaaaaaaaaaaKsY+K87vE5eK
wwz3uEQ9qKeiKUwcBHV8N1JfhswLL85sRjq6b9YhHiCfU2vwGWJ+SAfl2QJAA40t
Lpc4sw2Dllu350M/ppwXEqQVa+0B1cZMuxsTk3f8MlE9Mv+K6Y746rlUrlbGSdvt
gM1Iv2MsVfP3sTk+oQJABSHcGx+31fcKJoWgxGGGGGGGGGGGGGGGGGGGGGGGGGGG
vzqiaNCgAr4udqFRVGjqaFLb8rdbALFzja2fuSH4eQ==
-----END RSA PUBLIC KEY-----


### 5. Prepare .env file

```
# Applicatuon settings
APP_BASE_URL = "http://localhost:8000"
APP_CLIENT_ID = "my_client"
APP_CLIENT_SECRET = "YYxwlWABgtxxxxxxxxxxxxmf7hOwY7e"
APP_REDIRECT_URI = "http://localhost:8000/auth/callback"

# Keycloak Settings
KEYCLOAK_BASE_URL_LOCALHOST = "http://localhost:8080/"
KEYCLOAK_REALM = "my_application"

# Public Key for RS256 [TODO : hide this info to .env]
RSA_PUBLIC_KEY_BODY = "MIIBIjANBgkqhkiG......................Baa="
```


### 6. Start test web server 

```
$ python main.py
```