glm-ocr での応用可能性

DeepSeek-OCR と glm-ocr はどちらも Vision / OCR モデル

CLI では glm-ocr も Text Recognition: ./image.png で動作

そのため Web API でも images に base64 を入れ、system / user role で OCR 指示を与える形は概ね可能性あり

推奨パターン（推測ベース）：

response = chat(
    model="glm-ocr",
    messages=[
        {
            "role": "system",
            "content": "You are an OCR model. Extract text from the given image."
        },
        {
            "role": "user",
            "content": "Text Recognition:",  # CLI の Text Recognition に相当
            "images": [base64_image_data]
        }
    ]
)
print(response.message.content)


system role で OCR 指示を与えることで、精度や挙動が安定しやすい

user role の content は CLI の「Text Recognition:」に相当

画像は 必ず images 配列に base64 で渡す