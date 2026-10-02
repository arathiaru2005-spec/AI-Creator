async function createVideo() {

    const promptElement =
        document.getElementById("prompt");

    const result =
        document.getElementById("result");


    const prompt =
        promptElement.value.trim();


    // ==========================================
    // CHECK PROMPT
    // ==========================================

    if (!prompt) {

        alert(
            "Please enter a description!"
        );

        return;
    }


    // ==========================================
    // LOADING
    // ==========================================

    result.innerHTML = `

        <div class="loading">

            <div class="loader"></div>

            <h2>
                🎬 Creating Video...
            </h2>

            <p>
                AI is generating your video.
            </p>

            <p>
                ⏳ This may take a few minutes.
            </p>

        </div>

    `;


    try {

        // ======================================
        // SEND REQUEST TO FASTAPI
        // ======================================

        const response = await fetch(
            "http://127.0.0.1:8000/create-video",
            {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    prompt: prompt
                })

            }
        );


        // ======================================
        // CHECK HTTP RESPONSE
        // ======================================

        if (!response.ok) {

            throw new Error(
                `Server error: ${response.status}`
            );

        }


        const data =
            await response.json();


        console.log(
            "Backend response:",
            data
        );


        // ======================================
        // SUCCESS
        // ======================================

        if (
            data.status ===
            "success"
        ) {


            const videoUrl =
                "http://127.0.0.1:8000"
                + data.video_url
                + "?t="
                + Date.now();


            result.innerHTML = `

                <div class="video-result">

                    <h2>
                        🎉 Video Ready!
                    </h2>

                    <p>
                        <strong>Prompt:</strong>
                        ${escapeHtml(data.prompt)}
                    </p>


                    <video
                        controls
                        autoplay
                        playsinline
                    >

                        <source
                            src="${videoUrl}"
                            type="video/mp4"
                        >

                        Your browser does not
                        support video playback.

                    </video>


                    <br>


                    <a
                        class="open-video"
                        href="${videoUrl}"
                        target="_blank"
                    >
                        ▶ Open Video
                    </a>

                </div>

            `;

        }


        // ======================================
        // ERROR FROM BACKEND
        // ======================================

        else {

            result.innerHTML = `

                <div class="error-box">

                    <h2>
                        ❌ Video Generation Failed
                    </h2>

                    <p>
                        ${escapeHtml(
                            data.message ||
                            "Unknown error"
                        )}
                    </p>

                </div>

            `;

        }


    }


    // ==========================================
    // CONNECTION ERROR
    // ==========================================

    catch (error) {

        console.error(
            "Frontend error:",
            error
        );


        result.innerHTML = `

            <div class="error-box">

                <h2>
                    ❌ Connection Error
                </h2>

                <p>
                    Could not connect to
                    the FastAPI backend.
                </p>

                <p>
                    Make sure FastAPI is running.
                </p>

                <code>
                    python -m uvicorn
                    main:app --reload
                </code>

            </div>

        `;

    }

}


// ==========================================
// SECURITY / HTML ESCAPING
// ==========================================

function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent = text;

    return div.innerHTML;

}