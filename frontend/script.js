const API_URL = "https://autonomous-code-review-agent-production.up.railway.app"

let activeTab = "code"
let fileCache = {}
let fileList = []

function switchTab(tab) {
    activeTab = tab
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"))
    event.target.classList.add("active")

    document.getElementById("code-input").classList.toggle("hidden", tab !== "code")
    document.getElementById("github-input").classList.toggle("hidden", tab !== "github")

    // hide results and file list when switching tabs
    document.getElementById("results").classList.add("hidden")
    document.getElementById("file-list-section").classList.add("hidden")
    fileCache = {}
    fileList = []
}

function switchResult(type) {
    document.querySelectorAll(".result-tab").forEach(t => t.classList.remove("active"))
    event.target.classList.add("active")

    document.getElementById("report-output").classList.toggle("hidden", type !== "report")
    document.getElementById("fix-output").classList.toggle("hidden", type !== "fix")
}

function renderResults(data) {
    document.getElementById("bug-output").innerHTML = marked.parse(data.bug_result || "No bugs found.")
    document.getElementById("security-output").innerHTML = marked.parse(data.security_result || "No security issues found.")
    document.getElementById("style-output").innerHTML = marked.parse(data.style_result || "No style issues found.")
    document.getElementById("performance-output").innerHTML = marked.parse(data.performance_result || "No performance issues found.")
    document.getElementById("fixes-output").innerHTML = marked.parse(data.suggested_fixes || "No suggested fixes.")
    document.getElementById("fix-output").innerHTML = marked.parse(data.fixed_code || "No fixed code available.")
}

function renderFileList(files) {
    const fileListEl = document.getElementById("file-list")
    fileListEl.innerHTML = ""

    files.forEach(file => {
        const filename = file.filename || file.file_name
        const item = document.createElement("div")
        item.className = "file-item"
        item.id = `file-${filename}`
        item.innerHTML = `<span>${filename}</span>`
        item.onclick = () => reviewFile(filename, file.code, item)
        fileListEl.appendChild(item)
    })

    document.getElementById("file-list-section").classList.remove("hidden")
}

async function reviewFile(filename, code, itemEl) {
    // if cached serve instantly
    if (fileCache[filename]) {
        showFileResult(filename, fileCache[filename])
        return
    }

    // mark as loading
    itemEl.classList.add("loading")
    itemEl.innerHTML = `<span>${filename}</span><span>reviewing...</span>`

    const loading = document.getElementById("loading")
    document.getElementById("loading-text").textContent = `Reviewing ${filename}...`
    loading.classList.remove("hidden")
    document.getElementById("results").classList.add("hidden")

    try {
        const response = await fetch(`${API_URL}/review/file`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filename, code })
        })

        const data = await response.json()

        if (!response.ok) {
            alert(data.detail || "Something went wrong")
            itemEl.classList.remove("loading")
            itemEl.innerHTML = `<span>${filename}</span>`
            loading.classList.add("hidden")
            return
        }

        // cache the result
        fileCache[filename] = data

        // mark as cached
        itemEl.classList.remove("loading")
        itemEl.classList.add("cached")
        itemEl.innerHTML = `<span>${filename}</span><span class="file-badge">reviewed</span>`

        showFileResult(filename, data)

    } catch (error) {
        alert("Something went wrong. Make sure your API is running.")
        itemEl.classList.remove("loading")
        itemEl.innerHTML = `<span>${filename}</span>`
        loading.classList.add("hidden")
    }
}

function showFileResult(filename, data) {
    document.getElementById("loading").classList.add("hidden")

    const label = document.getElementById("current-file-label")
    label.textContent = `Reviewing: ${filename}`
    label.classList.remove("hidden")

    // reset to report tab
    document.querySelectorAll(".result-tab").forEach(t => t.classList.remove("active"))
    document.querySelectorAll(".result-tab")[0].classList.add("active")
    document.getElementById("report-output").classList.remove("hidden")
    document.getElementById("fix-output").classList.add("hidden")

    renderResults(data)
    document.getElementById("results").classList.remove("hidden")
}

async function submitReview() {
    const loading = document.getElementById("loading")
    const results = document.getElementById("results")

    // reset
    fileCache = {}
    fileList = []
    document.getElementById("file-list-section").classList.add("hidden")
    results.classList.add("hidden")

    loading.classList.remove("hidden")
    document.getElementById("loading-text").textContent = "Running agents in parallel..."

    try {
        let response

        if (activeTab === "code") {
            const code = document.getElementById("code").value
            response = await fetch(`${API_URL}/review/code`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ code })
            })

            const data = await response.json()

            if (!response.ok) {
                loading.classList.add("hidden")
                alert(data.detail || "Something went wrong")
                return
            }

            document.getElementById("current-file-label").classList.add("hidden")
            renderResults(data)
            loading.classList.add("hidden")
            results.classList.remove("hidden")

        } else {
            const url = document.getElementById("github-url").value
            document.getElementById("loading-text").textContent = "Fetching files from GitHub..."

            response = await fetch(`${API_URL}/review/github`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url })
            })

            const data = await response.json()

            if (!response.ok) {
                loading.classList.add("hidden")
                alert(data.detail || "Something went wrong")
                return
            }

            fileList = data
            loading.classList.add("hidden")
            renderFileList(fileList)
        }

    } catch (error) {
        loading.classList.add("hidden")
        alert("Something went wrong. Make sure your API is running.")
    }
}