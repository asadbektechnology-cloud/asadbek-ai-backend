import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

# .env faylini joriy papkaga nisbatan aniq manzil bilan yuklash
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Yangi Google GenAI mijozini yaratish
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
    print("MUVAFFAQIYAT: Yangi Gemini API mijoz muvaffaqiyatli yuklandi!")
else:
    client = None
    print("DIQQAT: GEMINI_API_KEY topilmadi! .env faylini tekshiring.")

app = FastAPI(title="Web AI API", version="1.0")

# Frontend bilan muammosiz bog'lanish uchun CORS sozlamalari
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ImageRequest(BaseModel):
    prompt: str

@app.get("/")
def home():
    return {"status": "Backend muvaffaqiyatli ishlayapti!"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    if not client:
        raise HTTPException(status_code=500, detail="Tizimda API kalit sozlanmagan!")
    
    try:
        # Eng so'nggi va barqaror gemini-2.5-flash modelidan foydalanamiz
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=request.message,
        )
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-image")
async def generate_image_endpoint(request: ImageRequest):
    if not client:
        raise HTTPException(status_code=500, detail="Tizimda API kalit sozlanmagan!")
    
    try:
        # Google Imagen 3 modeli orqali rasm generatsiya qilish
        result = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=request.prompt,
            config=dict(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="1:1"
            )
        )
        
        # Generatsiya bo'lgan birinchi rasmning base64 formatidagi ma'lumotini olamiz
        generated_image = result.generated_images[0]
        image_base64 = generated_image.image.image_bytes
        
        # Frontend to'g'ridan-to'g'ri rasm qilib ko'rsatishi uchun base64 formatda qaytaramiz
        import base64
        encoded_image = base64.b64encode(image_base64).decode('utf-8')
        
        return {
            "status": "Rasm muvaffaqiyatli yaratildi!",
            "image": f"data:image/jpeg;base64,{encoded_image}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))