from pyngrok import ngrok
NGROK_AUTH_TOKEN = "2kBrPfkpcHpVWNjzW4TMHqdhx7G_2DMfXRg5Nbfy9Nk4zWrqw"
ngrok.set_auth_token(NGROK_AUTH_TOKEN)
# 启动 ngrok 隧道https://2156-34-16-209-243.ngrok-free.app/
public_url = ngrok.connect(9999)
print("Public URL:", public_url)