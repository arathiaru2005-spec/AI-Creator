async function createVideo() {

    const prompt = document.getElementById("prompt").value.trim();

    if (prompt === "") {
        alert("Please enter a description!");
        return;
    }

    const result = document.getElementById("result");

    result.innerHTML = `
        <h2>🎬 Creating Video...</h2>
        <p>⏳ AI is generating your video. Please wait...</p>
    `;

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/create-video",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    prompt: prompt
                })
            }
        );

        const data = await response.json();

        console.log("Backend response:", data);

        if (data.status === "success") {

            // Prevent browser from showing an old cached video
            const videoUrl =
                "http://127.0.0.1:8000" +
                data.video_url +
                "?t=" +
                Date.now();

            result.innerHTML = `
                <h2>🎉 Video Ready!</h2>

                <p>
                    <b>Prompt:</b> ${data.prompt}
                </p>

                <video
                    controls
                    autoplay
                    style="
                        width:100%;
                        max-width:800px;
                        border-radius:15px;
                    "
                >
                    <source
                        src="${videoUrl}"
                        type="video/mp4"
                    >
                    Your browser does not support video playback.
                </video>

                <br><br>

                <a
                    href="${videoUrl}"
                    target="_blank"
                >
                    ▶ Open Video
                </a>
            `;

        } else {

            result.innerHTML = `
                <h2>❌ Video Generation Failed</h2>

                <p>
                    ${data.message || "Something went wrong."}
                </p>
            `;
        }

    } catch (error) {

        console.error("ERROR:", error);

        result.innerHTML = `
            <h2>❌ Error</h2>

            <p>
                Could not connect to backend.
            </p>

            <p>
                Make sure your FastAPI server is running.
            </p>
        `;
    }
}