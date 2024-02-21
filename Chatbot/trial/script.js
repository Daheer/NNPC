function sendMessage() {
  const inputField = document.getElementById("input");
  let input = inputField.value.trim();
  input != "" && output(input);
  inputField.value = "";
}
document.addEventListener("DOMContentLoaded", () => {
  const inputField = document.getElementById("input");
  inputField.addEventListener("keydown", function (e) {
    if (e.code === "Enter") {
      let input = inputField.value.trim();
      input != "" && output(input);
      inputField.value = "";
    }
  });
});

async function output(input) {
  let product;
  document.getElementById("pulse-loading").style.display = 'flex';
  document.getElementById("normal-send").style.display = 'none';

  await fetch('https://5aca-34-66-174-126.ngrok-free.app/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message: input, use_openai: false, api_key: "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" }),
  })
    .then(response => response.json())
    .then(data => {
      product = data.data;
      addChat(input, product);
    })
    .catch(error => {
      console.error('Error:', error);
    });

}

function addChat(input, product) {
  document.getElementById("pulse-loading").style.display = 'none';
  document.getElementById("normal-send").style.display = 'flex';
  const mainDiv = document.getElementById("message-section");
  let userDiv = document.createElement("div");
  userDiv.id = "user";
  userDiv.classList.add("message");
  userDiv.innerHTML = `<span id="user-response">${input}</span>`;
  mainDiv.appendChild(userDiv);

  let botDiv = document.createElement("div");
  botDiv.id = "bot";
  botDiv.classList.add("message");
  botDiv.innerHTML = `<span id="bot-response">${product}</span>`;
  mainDiv.appendChild(botDiv);
  var scroll = document.getElementById("message-section");
  scroll.scrollTop = scroll.scrollHeight;
}