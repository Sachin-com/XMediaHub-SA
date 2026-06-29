document.addEventListener("DOMContentLoaded", function () {

    const fetchBtn = document.getElementById("fetchBtn");

    if (!fetchBtn) return;

    fetchBtn.addEventListener("click", function () {

        const url = document.getElementById("url").value.trim();

        if (url === "") {
            alert("Please paste a YouTube URL.");
            return;
        }

        const formData = new FormData();
        formData.append("url", url);

        // --------------------------
        // Fetch Video Info
        // --------------------------

        fetch("/youtube/info", {
            method: "POST",
            body: formData
        })
        .then(res => res.json())
        .then(data => {

            if (data.error) {
                alert(data.error);
                return;
            }

            document.getElementById("videoInfo").style.display = "block";

            document.getElementById("thumb").src = data.thumbnail;
            document.getElementById("title").innerHTML = "🎬 " + data.title;
            document.getElementById("channel").innerHTML = "👤 " + data.channel;
            document.getElementById("duration").innerHTML = "⏱ " + data.duration + " sec";
            document.getElementById("views").innerHTML = "👁 " + data.views;

        });

        // --------------------------
        // Fetch Available Formats
        // --------------------------

        fetch("/youtube/formats", {
            method: "POST",
            body: formData
        })
        .then(res => res.json())
        .then(formats => {

            const quality = document.getElementById("quality");

            quality.innerHTML = "";

            if (formats.error) {
                alert(formats.error);
                return;
            }

            formats.forEach(f => {

                const option = document.createElement("option");

                option.value = f.quality;

                option.text =
                    `${f.quality} (${f.size})`;

                quality.appendChild(option);

            });

        });

    });

});