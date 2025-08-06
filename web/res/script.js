document.getElementById("login_button_one").onclick = function() {
    const username = document.getElementById("username_login").value;
    const potatoType = document.getElementById("potato_type_login").value;

    if (username.length <  6) {
        alert("Username must be at least 6 characters long");
        return;
    }

    alert(username);
    alert(potatoType);
}