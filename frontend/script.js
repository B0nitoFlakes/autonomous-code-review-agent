const API_URL = "autonomous-code-review-agent-production.up.railway.app"

let activeTab = "code"

function switchTab(tab) {
    activeTab = tab
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"))
    event.target.classList.add("active")

    document.getElementById("code-input").classList.toggle("hidden", tab !== "code")
    document.getElementById("github-input").classList.toggle("hidden", tab !== "github")
}

function switchResult(type) {
    document.querySelectorAll(".result-tab").forEach(t => t.classList.remove("active"))
    event.target.classList.add("active")

    document.getElementById("report-output").classList.toggle("hidden", type !== "report")
    document.getElementById("fix-output").classList.toggle("hidden", type !== "fix")
}

async function submitReview() {
    const loading = document.getElementById("loading")
    const results = document.getElementById("results")

    loading.classList.remove("hidden")
    results.classList.add("hidden")

    try {
        let response

        if (activeTab === "code") {
            const code = document.getElementById("code").value
            response = await fetch(`${API_URL}/review/code`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ code })
            })
        } else {
            const url = document.getElementById("github-url").value
            response = await fetch(`${API_URL}/review/github`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url })
            })
        }

        const data = await response.json()

        document.getElementById("report-output").textContent = data.report
        document.getElementById("fix-output").textContent = data.fixed_code

        loading.classList.add("hidden")
        results.classList.remove("hidden")

    } catch (error) {
        loading.classList.add("hidden")
        alert("Something went wrong. Make sure your API is running.")
    }
}