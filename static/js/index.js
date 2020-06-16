var from;
function check() {
    form = document.getElementById("newchat");
    if (form.user.value.trim().length > 0) {
        return true;
    } else {
        document.getElementById("emptyuser").style.visibility = "visible"
        form.user.focus();
        return false;
    }
}

function jchat() {
    document.getElementById("cidbox").style.visibility = "visible";
    return false;
}

function joinchat() {
    if (!check()) {
        return false;
    } else if (form.chatid.value.trim().length < 1) { 
        document.getElementById("emptychatid").style.visibility = "visible";
        form.chatid.focus();
        return false;
    }
}