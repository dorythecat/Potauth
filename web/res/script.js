document.getElementById("login_button_one").onclick = function() {
    const username = document.getElementById("username_login").value;
    const potatoType = document.getElementById("potato_type_login").value;

    if (username.length <  4) {
        alert("Username must be at least 4 characters long");
        return;
    }

    const potato_login_container = document.getElementById("potato_login_container");

    const response =  fetch(`http://127.0.0.1:8000/get_images?username=${username}`, {
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
    });

    for (let i = 0; i < 9; i++) {

    }

    potato_login_container.style.display = "flex";
}