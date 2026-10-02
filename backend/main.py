from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import os
import requests
import json
import time


# ==================================================
# FASTAPI APP
# ==================================================

app = FastAPI()


# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# GENERATED VIDEO FOLDER
# ==================================================

os.makedirs("generated", exist_ok=True)

app.mount(
    "/generated",
    StaticFiles(directory="generated"),
    name="generated"
)


# ==================================================
# HUGGING FACE SPACE
# ==================================================

HF_SPACE = "https://minimaxai-minimax-h3-turbo-lora.hf.space"


# ==================================================
# REQUEST MODEL
# ==================================================

class VideoRequest(BaseModel):
    prompt: str


# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():
    return {
        "message": "AI Creator Backend is working!"
    }


# ==================================================
# CREATE VIDEO
# ==================================================

@app.post("/create-video")
def create_video(data: VideoRequest):

    try:

        print("====================================")
        print("VIDEO GENERATION STARTED")
        print("Prompt:", data.prompt)
        print("====================================")

        # ------------------------------------------
        # STEP 1: SEND REQUEST TO HUGGING FACE
        # ------------------------------------------

        api_url = f"{HF_SPACE}/gradio_api/call/generate"

        payload = {
            "data": [
                data.prompt,          # prompt
                None,                 # first image
                None,                 # last image
                "960x544 · 16:9 fast", # canvas
                5,                    # duration
                6,                    # steps
                42,                   # seed
                False                 # upsample
            ]
        }

        print("Sending request to Hugging Face...")

        response = requests.post(
            api_url,
            json=payload,
            timeout=60
        )

        print("HF response status:", response.status_code)
        print("HF response:", response.text)

        if response.status_code != 200:
            raise Exception(
                f"Hugging Face request failed: "
                f"{response.status_code} - {response.text}"
            )

        response_data = response.json()

        event_id = response_data.get("event_id")

        if not event_id:
            raise Exception(
                f"No event_id received from Hugging Face: "
                f"{response_data}"
            )

        print("Event ID:", event_id)

        # ------------------------------------------
        # STEP 2: WAIT FOR GENERATION
        # ------------------------------------------

        result_url = (
            f"{HF_SPACE}/gradio_api/call/generate/{event_id}"
        )

        print("Waiting for video generation...")

        video_result = None

        with requests.get(
            result_url,
            stream=True,
            timeout=900
        ) as stream:

            for line in stream.iter_lines(
                decode_unicode=True
            ):

                if not line:
                    continue

                print("STREAM:", line)

                # Gradio sends:
                # event: complete
                # data: [...]

                if line.startswith("event:"):

                    event_type = line.replace(
                        "event:",
                        ""
                    ).strip()

                    print(
                        "Event type:",
                        event_type
                    )

                if line.startswith("data:"):

                    json_data = line.replace(
                        "data:",
                        "",
                        1
                    ).strip()

                    try:

                        parsed = json.loads(
                            json_data
                        )

                        print(
                            "Parsed result:",
                            parsed
                        )

                        # --------------------------------
                        # GENERATION COMPLETE
                        # --------------------------------

                        if isinstance(parsed, list):

                            video_result = parsed

                    except json.JSONDecodeError:

                        print(
                            "Could not decode:",
                            json_data
                        )

        # ------------------------------------------
        # CHECK RESULT
        # ------------------------------------------

        if not video_result:
            raise Exception(
                "Hugging Face did not return a video."
            )

        print("FINAL RESULT:")
        print(video_result)

        # ------------------------------------------
        # GET VIDEO INFORMATION
        # ------------------------------------------

        video_data = video_result[0]

        print("VIDEO DATA:")
        print(video_data)

        video_url = None

        if isinstance(video_data, dict):

            # New Gradio FileData format
            video_url = video_data.get("url")

            if not video_url:
                video_url = video_data.get(
                    "path"
                )

        elif isinstance(video_data, str):

            video_url = video_data

        if not video_url:
            raise Exception(
                "Could not find video URL in response."
            )

        # ------------------------------------------
        # MAKE URL ABSOLUTE
        # ------------------------------------------

        if video_url.startswith("/"):

            video_url = HF_SPACE + video_url

        print("VIDEO URL:")
        print(video_url)

        # ------------------------------------------
        # DOWNLOAD VIDEO
        # ------------------------------------------

        print("Downloading video...")

        video_response = requests.get(
            video_url,
            timeout=300
        )

        if video_response.status_code != 200:

            raise Exception(
                "Could not download generated video. "
                f"Status: {video_response.status_code}"
            )

        # ------------------------------------------
        # SAVE VIDEO
        # ------------------------------------------

        output_path = os.path.join(
            "generated",
            "generated_video.mp4"
        )

        with open(
            output_path,
            "wb"
        ) as video_file:

            video_file.write(
                video_response.content
            )

        print(
            "Video saved:",
            output_path
        )

        # ------------------------------------------
        # RETURN TO FRONTEND
        # ------------------------------------------

        return {

            "status": "success",

            "message":
                "Video generated successfully!",

            "prompt":
                data.prompt,

            "video_url":
                "/generated/generated_video.mp4"
        }


    except Exception as e:

        print("")
        print("====================================")
        print("VIDEO GENERATION ERROR")
        print("====================================")

        print(
            type(e).__name__,
            ":",
            str(e)
        )

        print("====================================")

        return {

            "status": "error",

            "message":
                str(e),

            "type":
                type(e).__name__
        }