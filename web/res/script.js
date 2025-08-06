const API_URL ="http://127.0.0.1:8000"

const potato_login_container = document.getElementById("potato_login_container");
const login = document.getElementById("login");

document.getElementById("login_button_one").onclick = function() {
    const username = document.getElementById("username_login").value;
    const potatoType = document.getElementById("potato_type_login").value;

    if (username.length <  4) {
        alert("Username must be at least 4 characters long");
        return;
    }

    const response =  fetch(`${API_URL}/get_images?username=${username}`, {
        method: "GET",
        headers: {}
    }).catch(err => {
        console.log(err);
    }).then(res => res.json()).then(res => {
        potato_login_container.children[0].src = `data:image/WEBP;base64,${res['image0']}`;
        potato_login_container.children[1].src = `data:image/WEBP;base64,${res['image1']}`;
        potato_login_container.children[2].src = `data:image/WEBP;base64,${res['image2']}`;
        potato_login_container.children[3].src = `data:image/WEBP;base64,${res['image3']}`;
        potato_login_container.children[4].src = `data:image/WEBP;base64,${res['image4']}`;
        potato_login_container.children[5].src = `data:image/WEBP;base64,${res['image5']}`;
        potato_login_container.children[6].src = `data:image/WEBP;base64,${res['image6']}`;
        potato_login_container.children[7].src = `data:image/WEBP;base64,${res['image7']}`;
        potato_login_container.children[8].src = `data:image/WEBP;base64,${res['image8']}`;

        potato_login_container.style.display = "flex";
    });
}

for (let potato of potato_login_container.children) {
    potato.onclick = function() {
        const username = document.getElementById("username_login").value;
        const potatoType = document.getElementById("potato_type_login").value;

        const formData = new FormData();
        formData.append("image", this.src.split(",")[1]);

        console.log(this.src.split(",")[1]);
        const response = fetch(`${API_URL}/login?username=${username}&favourite_potato=${potatoType}`, {
            method: "POST",
            headers: {},
            body: formData
        }).catch(err => {
            console.log(err);
        }).then(r => r.json()).then(r => {
            document.cookie = "username=" + username;
            document.cookie = "potatoType=" + potatoType;
            document.cookie = "token=" + r;
            window.location.reload();
        });
    }
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return "";
}

if (document.cookie.includes("token=")) {
    login.style.display = "none";
}