async function reviewCode() {

    const code = document.getElementById("code").value;

    const language = document.getElementById("language").value;

    if (!code.trim()) {

        alert("Please enter some code.");

        return;
    }

    const response = await fetch("/review", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            code: code,
            language: language
        })

    });


    const result = await response.json();


    if (result.error) {

        alert(result.error);

        return;
    }


    document.getElementById("score").innerText =
        result.score + "/100";


    document.getElementById("quality").innerText =
        result.quality;


    document.getElementById("summary").innerText =
        result.summary;


    const container =
        document.getElementById("issues-container");


    container.innerHTML = "";


    if (result.issues.length === 0) {

        container.innerHTML =
            "<p>✅ No major issues detected.</p>";

        return;
    }


    result.issues.forEach(issue => {

        const div = document.createElement("div");

        div.className =
            "issue " +
            (issue.severity === "Low" ? "low" : "");


        div.innerHTML = `

            <h3>
                ${issue.type}
                - ${issue.severity}
            </h3>

            <p>
                <strong>Line:</strong>
                ${issue.line || "N/A"}
            </p>

            <p>
                <strong>Problem:</strong>
                ${issue.message}
            </p>

            <p>
                <strong>Suggestion:</strong>
                ${issue.suggestion}
            </p>

        `;


        container.appendChild(div);

    });

}