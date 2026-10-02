from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from gradio_client import Client

import os
import shutil
import uuid

# Load environment variables
load_dotenv()


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="AI Creator API"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# FOLDERS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VIDEO_DIR = os.path.join(
    BASE_DIR,
    "generated_videos"
)

os.makedirs(
    VIDEO_DIR,
    exist_ok=True
)


# =========================================================
# SERVE GENERATED VIDEOS
# =========================================================

app.mount(
    "/videos",
    StaticFiles(directory=VIDEO_DIR),
    name="videos"
)


# =========================================================
# HUGGING FACE SPACE
# =========================================================

SPACE = "Pepe104/MiniMax-H3-Turbo-LoRA-UNCENSORED"


# =========================================================
# CREATE CLIENT
# =========================================================

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    print("Warning: HF_TOKEN is not found")
else:
        print("HF_TOKEN found, using it to create the client")
if HF_TOKEN:

    client = Client(
        SPACE,
        token=HF_TOKEN
    )

else:

    client = Client(
        SPACE
    )


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "status": "running",
        "message": "AI Creator backend is running"
    }


# =========================================================
# CREATE VIDEO
# =========================================================

@app.post("/create-video")
async def create_video(data: dict):

    prompt = data.get("prompt", "").strip()

    if not prompt:

        return {
            "status": "error",
            "message": "Prompt is required"
        }


    try:

        print("\n===================================")
        print("Generating video...")
        print("Prompt:", prompt)
        print("===================================\n")


        # -------------------------------------------------
        # CALL HUGGING FACE SPACE
        # -------------------------------------------------

        result = client.predict(
            prompt=prompt,
            api_name="/generate"
        )


        print("\n========== HUGGING FACE RESULT ==========")
        print(result)
        print("=========================================\n")


        # -------------------------------------------------
        # FIND VIDEO FILE
        # -------------------------------------------------

        video_path = None


        if isinstance(result, str):

            video_path = result


        elif isinstance(result, tuple):

            for item in result:

                if isinstance(item, str):

                    if (
                        item.endswith(".mp4")
                        or os.path.exists(item)
                    ):

                        video_path = item
                        break


                elif isinstance(item, dict):

                    if "path" in item:

                        video_path = item["path"]
                        break


        elif isinstance(result, dict):

            if "path" in result:

                video_path = result["path"]


        # -------------------------------------------------
        # CHECK RESULT
        # -------------------------------------------------

        if not video_path:

            return {
                "status": "error",
                "message": "Hugging Face returned a result, but no video file was found.",
                "raw_result": str(result)
            }


        # -------------------------------------------------
        # CHECK FILE
        # -------------------------------------------------

        if not os.path.exists(video_path):

            return {
                "status": "error",
                "message": "Generated video file could not be found.",
                "video_path": str(video_path)
            }


        # -------------------------------------------------
        # CREATE UNIQUE FILE NAME
        # -------------------------------------------------

        filename = (
            f"{uuid.uuid4().hex}.mp4"
        )


        destination = os.path.join(
            VIDEO_DIR,
            filename
        )


        # -------------------------------------------------
        # COPY VIDEO
        # -------------------------------------------------

        shutil.copy2(
            video_path,
            destination
        )


        # -------------------------------------------------
        # URL
        # -------------------------------------------------

        video_url = (
            f"/videos/{filename}"
        )


        print("Video saved:")
        print(destination)
        print("Video URL:")
        print(video_url)


        return {

            "status": "success",

            "prompt": prompt,

            "video_url": video_url

        }


    except Exception as e:

        print("\n========== ERROR ==========")
        print(str(e))
        print("===========================\n")


        return {

            "status": "error",

            "message": str(e)

        }