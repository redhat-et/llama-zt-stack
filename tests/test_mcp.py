import jwt, time
SECRET = "super-secret-key"

# Token for current scope only
token = jwt.encode(
    {"sub": "alice", "scope": "weather:current", "exp": time.time() + 600},
    SECRET,
    algorithm="HS256"
)
print(token)

## Token for current as well as forecast scopes
# token = jwt.encode(
#     {"sub": "alice", "scope": "weather:current weather:forecast", "exp": time.time() + 600},
#     SECRET,
#     algorithm="HS256"
# )
# print(token)

