const API_URL ="https://potauth.onrender.com"

const potato_login_container = document.getElementById("potato_login_container");
const info = document.getElementById("info");
const login_and_register = document.getElementById("login_and_register");
const content = document.getElementById("content");
const your_potatoes = document.getElementById("your_potatoes");
const your_potatoes_container = document.getElementById("your_potatoes_container");
const potato_upload_file = document.getElementById("potato_upload_file");
const logout = document.getElementById("logout");

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

    logout.onclick = function() {
        document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC";
        document.cookie = "username=; expires=Thu, 01 Jan 1970 00:00:00 UTC;";
        document.cookie = "potatoType=; expires=Thu, 01 Jan 1970 00:00:00 UTC;";
        document.location.reload();
    }

    // Potatoes
    fetch(`${API_URL}/potatoes/${getCookie("username")}`, {
        method: "GET",
        headers: {}
    }).catch(err => alert(err)).then(res => {
        if (res.status !== 200) your_potatoes_container.innerHTML = "You have no potatoes!";
        else res.json().then(res => {
            for (const potato of res)
                your_potatoes_container.innerHTML += `<img src="data:image/webp;base64,${potato}" alt="Potato" onclick="window.open(this.src)">`;
        });
    });

    potato_upload_file.onchange = function() {
        const file = this.files[0];
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = function() {
            const formData = new FormData();
            formData.append("image", reader.result.split(",")[1]);

            fetch(`${API_URL}/post`, {
                method: "POST",
                headers: { "Authorization": `Bearer ${getCookie("token")}` },
                body: formData
            }).catch(err => alert(err)).then(r => {
                if (r.status === 200) document.location.reload();
                else alert("Upload failed!");
            });
        }
    }
} else {
    content.remove();
    your_potatoes.remove();

    document.getElementById("login_button").onclick = function() {
        const username = document.getElementById("username_login").value;
        const potatoType = document.getElementById("potato_type_login").value;

        if (username.length <  4 && username.length > 32) {
            alert("Login failed!!");
            return;
        }

        fetch(`${API_URL}/get_images?username=${username}`, {
            method: "GET",
            headers: {}
        }).catch(err => alert(err)).then(res => {
            if (res.status !== 200) {
                alert("Login failed!");
                document.location.reload();
            } else res.json().then(res => {
                login_and_register.style.paddingTop = "0";
                for (const potato of potato_login_container.children) {
                    potato.src = `data:image/webp;base64,${res[potato.id]}`;
                    potato.onclick = function() {
                        const formData = new FormData();
                        formData.append("image", res[potato.id]);

                        fetch(`${API_URL}/login?username=${username}&favourite_potato=${potatoType}`, {
                            method: "POST",
                            headers: {},
                            body: formData
                        }).catch(err => alert(err)).then(r => {
                            if (r.status !== 200) {
                                alert("Login failed!");
                                document.location.reload();
                            } else r.json().then(r => {
                                document.cookie = `username=${username}; Max-Age=1800;`;
                                document.cookie = `potatoType=${potatoType}; Max-Age=1800;`;
                                document.cookie = `token=${r}; Max-Age=1800;`;
                                document.location.reload();
                            });
                        });
                    }
                }
                potato_login_container.style.display = "flex";
                $.scrollify.update(); // Make sure the spacing is right
            });
        });
    }

    document.getElementById("register_button").onclick = function() {
        const username = document.getElementById("username_register").value;
        const potatoType = document.getElementById("potato_type_register").value;
        const potato_register_file = document.getElementById("potato_register_file");

        if (username.length <  4 || username.length > 32) {
            alert("Invalid username provided!");
            return;
        }

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
                }).catch(err => alert(err)).then(r => {
                    if (r.status !== 200) {
                        alert("Registration failed!");
                        document.location.reload();
                    } else r.json().then(r => {
                        document.cookie = `username=${username}; Max-Age=1800;`;
                        document.cookie = `potatoType=${potatoType}; Max-Age=1800;`;
                        document.cookie = `token=${r}; Max-Age=1800;`;
                        document.location.reload();
                    });
                });
            }
        }
        potato_register_file.style.display = "block";
    }
}

$(document).ready(function() {
    $.scrollify({
        section: ".section",
        sectionName: ".section",
        easing: "jswing",
        scrollSpeed: 400,
        overflowScroll: true,
        setHeights: true,
        scrollbars: false,
        touchScroll: false
    });
});