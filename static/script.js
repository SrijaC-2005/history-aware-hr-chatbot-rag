async function sendMessage() {

    let input = document.getElementById("user-input");
    let message = input.value.trim();

    if(message === "") return;

    let chatBox = document.getElementById("chat-box");

    chatBox.innerHTML += `
        <div class="user-message">
            ${message}
        </div>
    `;

    input.value = "";

    chatBox.innerHTML += `
        <div class="bot-message" id="loading">
            Thinking...
        </div>
    `;

    chatBox.scrollTop = chatBox.scrollHeight;

    try{

        let response = await fetch("/chat",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                message:message
            })
        });

        let data = await response.json();

        document.getElementById("loading").remove();

        chatBox.innerHTML += `
            <div class="bot-message">
                ${data.response}
            </div>
        `;

        chatBox.scrollTop = chatBox.scrollHeight;

    }
    catch(error){

        document.getElementById("loading").remove();

        chatBox.innerHTML += `
            <div class="bot-message">
                Error contacting server.
            </div>
        `;
    }
}

document.getElementById("user-input")
.addEventListener("keypress", function(event){
    if(event.key === "Enter"){
        sendMessage();
    }
});
