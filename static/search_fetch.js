document.addEventListener('DOMContentLoaded', () => {
    document.getElementById("indexing").addEventListener('click', index)
});

function index() {
    document.getElementById("indexing").disabled = true;
    fetch("/InvertedCreation", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        }
    }).then((response) => {
        if (response.ok) {
            window.location = response.url;
        } else {
            throw new Error(`Request failed: ${response.status}`);
        }
    })
        .catch((error) => {
            console.error(error);
        });
}
