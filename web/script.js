const conversation = document.getElementById("conversation");
const room_list = document.getElementById("room_list");
const textarea = document.getElementById("text_input");
const setting_modal = document.getElementById("setting_modal");

var last_room = null;

let websocket = new WebSocket("ws://" + window.location.hostname + ":5050")
let text_color = "#FFFFFF";

textarea.addEventListener("keypress", function(event) {
    if (event.key == "Enter") {
        send_text_message();
    };
});


websocket.onmessage = (event) => {
    data = event.data;

    if (data.startsWith("eval|")) {
        eval(data.slice(5))
    }
}
websocket.onopen = (event) => {  authorize()  }
websocket.onclose = (event) => {
    insert_message({author: "[YOU]", author_color: "#FF0000", message: "Connection to WS server lost.", timestamp: ""});
    alert("Connection to WS server is lost.");
}


function insert_message(data) {
    message_timestamp = data.timestamp;
    author_name = data.author;
    author_color = data.author_color;
    message = data.message;

    message_div = document.createElement("div");
    message_div.classList.add("message");
    
    timestamp = document.createElement("span");
    timestamp.style.color = "#e5e2e5";
    timestamp.innerHTML = message_timestamp + ": ";

    author = document.createElement("span");
    author.style.color = author_color;
    author.innerHTML = author_name + ": ";

    timestamp_html = timestamp.outerHTML
    author_html = author.outerHTML

    message_div.innerHTML = timestamp_html + author_html + message;
    conversation.appendChild(message_div);
    message_div.scrollIntoView();

    return message_div;
}

function insert_room(data) {
    room_name = data.name;
    room_id = data.id;
    room_is_private = data.private;

    room_div = document.createElement("div");
    room_div.classList.add("room");
    if(room_is_private) {
        room_div.classList.add("private_room");
    }
    room_div.setAttribute("id", "room_" + room_id);
    room_div.innerHTML = room_name
    room_div.setAttribute("onclick", "switch_to_channel(" + room_id + ")")

    room_list.appendChild(room_div);
}


function switch_to_channel(id) {
    if(last_room) {
        last_room.style.opacity = null;
    }
    room_div = document.getElementById("room_" + id)
    conversation.innerHTML = "";
    room_div.style.opacity = 1.0;
    last_room = room_div

    websocket.send(JSON.stringify({op: "switch_channel", "id": id}))
    return room_div
}

function authorize() {
    websocket.send(JSON.stringify({  op: "authorize"  }))
    console.log("Sent authorize message.")
}

function send_text_message() {
    sending_text = textarea.value;
    textarea.value = "";

    websocket.send(JSON.stringify({
        "op": "send_message",
        "text": sending_text,
        "color": text_color
    }))
}

function open_settings_modal() {
    setting_modal.style.visibility = null;
}
function setting_modal_close() {
    setting_modal.style.visibility = "hidden";
}
function setting_modal_save() {
    selected_color = document.getElementById("setting_modal_hex_author").value;
    if (selected_color != "#000000") {
        text_color = selected_color;
        console.log("Changed color.");
    }

    selected_color = document.getElementById("setting_modal_hex_primary").value;
    if (selected_color != "#000000") {
        document.documentElement.style.setProperty("--primary-background-color", selected_color)
        console.log("Changed primary color.");
    }

    selected_color = document.getElementById("setting_modal_hex_secondary").value;
    if (selected_color != "#000000") {
        document.documentElement.style.setProperty("--secondary-background-color", selected_color)
        console.log("Changed secondary color.");
    }

    selected_color = document.getElementById("setting_modal_hex_tertiary").value;
    if (selected_color != "#000000") {
        document.documentElement.style.setProperty("--tertiary-background-color", selected_color)
        console.log("Changed tertiary color.");
    }
}