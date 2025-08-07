const API_URL ="http://127.0.0.1:8000"

const potato_login_container = document.getElementById("potato_login_container");
const info = document.getElementById("info");
const login_and_register = document.getElementById("login_and_register");
const content = document.getElementById("content");
const your_potatoes = document.getElementById("your_potatoes");
const your_potatoes_container = document.getElementById("your_potatoes_container");
const logout = document.getElementById("logout");

document.getElementById("login_button").onclick = function() {
    const username = document.getElementById("username_login").value;
    const potatoType = document.getElementById("potato_type_login").value;

    if (username.length <  4) {
        alert("Username must be at least 4 characters long");
        return;
    }

    fetch(`${API_URL}/get_images?username=${username}`, {
        method: "GET",
        headers: {}
    }).catch(err => console.log(err)).then(res => res.json()).then(res => {
        login_and_register.style.paddingTop = "0";
        for (const potato of potato_login_container.children) {
            potato.src = `data:image/webp;base64,${res[potato.id]}`;
            potato.onclick = function() {
                const username = document.getElementById("username_login").value;
                const potatoType = document.getElementById("potato_type_login").value;

                const formData = new FormData();
                formData.append("image", res[potato.id]);

                const response = fetch(`${API_URL}/login?username=${username}&favourite_potato=${potatoType}`, {
                    method: "POST",
                    headers: {},
                    body: formData
                }).catch(err => console.log(err)).then(r => {
                    if (r.status !== 200) {
                        alert("Login failed!");
                        window.location.reload();
                        return;
                    }
                    r.json().then(r => {
                        document.cookie = "username=" + username;
                        document.cookie = "potatoType=" + potatoType;
                        document.cookie = "token=" + r;
                        window.location.reload();
                    });
                });
            }
        }

        potato_login_container.style.display = "flex";
    });
}

document.getElementById("register_button").onclick = function() {
    const username = document.getElementById("username_register").value;
    const potatoType = document.getElementById("potato_type_register").value;
    const potato_register_file = document.getElementById("potato_register_file");

    if (username.length <  4) {
        alert("Username must be at least 4 characters long");
        return;
    }

    potato_register_file.style.display = "block";
    potato_register_file.onchange = function() {
        const file = this.files[0];
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = function() {
            const formData = new FormData();
            formData.append("image", reader.result.split(",")[1]);

            fetch(`${API_URL}/register?username=${username}&favourite_potato=${potatoType}`, {
                method: "POST",
                headers: {},
                body: formData
            }).catch(err => console.log(err)).then(r => {
                if (r.status !== 200) {
                    alert("Registration failed!");
                    window.location.reload();
                    return;
                }
                r.json().then(r => {
                    document.cookie = "username=" + username;
                    document.cookie = "potatoType=" + potatoType;
                    document.cookie = "token=" + r;
                    document.location.reload();
                });
            });
        }
    }
}

logout.onclick = function() {
    document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC";
    document.cookie = "username=; expires=Thu, 01 Jan 1970 00:00:00 UTC;";
    document.cookie = "potatoType=; expires=Thu, 01 Jan 1970 00:00:00 UTC;";
    window.location.reload();
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return "";
}

if (document.cookie.includes("token=")) {
    // We use remove so that it doesn't mess with scrollify
    info.remove();
    login_and_register.remove();
    logout.style.display = "block";
} else {
    content.remove();
    your_potatoes.remove();
}


// Potatoes
fetch(`${API_URL}/potatoes/${getCookie("username")}`, {
    "method": "GET",
    "headers": {}
}).catch(err => console.log(err)).then(res => res.json()).then(res => {
    for (const potato of res) {
        your_potatoes_container.innerHTML += `<img src="data:image/webp;base64,${potato}" alt="potato" class="potato">`;
    }
})