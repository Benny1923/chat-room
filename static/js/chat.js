var xhr;

function update(status, message = '') {
    xhr = $.ajax({
        url: "/api/"+$('#chatid').val(),
        method: "POST",
        contentType : 'application/json; charset=utf-8',
        data: JSON.stringify({"status": status, "message": message}),
        timeout: 60000,
        success: function(data) {
            info = JSON.parse(data);
            updateUserList(info['online']);
            if (info["message"]) newMessage(info["message"]["from"], info["message"]["msg"])
            update('wait');
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            if (errorThrown != "abort") {
                update("join");
            } else {
                console.log("abort by send()");
            }
        }
    })
}

function updateUserList(user = []) {
    $('#userlist').empty()
    user.forEach(function(name){
        $('#userlist').append("<p>"+name+"</p>")
    })
}

function newMessage(name, msg) {
    $chat = $("#chatbox")
    $chat.append(`<p><span>${name}：</span><br>${msg}</p>`);
    $chat.scrollTop($chat.height());
    console.log(`${name} says: ${msg}`);
}

function send(){
    if ($("#msg").val()) {
        $chat = $("#chatbox");
        $chat.append("<p style=\"float: right;\"><span>"+$("#msg").val()+"</span></p><div style=\"clear:both;\"></div>");
        $chat.scrollTop($chat.height());
        xhr.abort();
        update("send", $('#msg').val());
        $('#msg').val('');
        $('#msg').focus();
    }
}

$(document).ready(()=>{
    update('join')
})