const roleSelect = document.getElementById("roleSelect");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const chatBox = document.getElementById("chatBox");
const errorBox = document.getElementById("errorBox");

let conversationId = null;

function renderMessage(sender, text) {
  const bubble = document.createElement("article");
  bubble.className = `bubble ${sender}`;
  bubble.innerHTML = `<strong>${sender === "user" ? "Vos" : "Asistente"}:</strong> ${text}`;
  chatBox.appendChild(bubble);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function setError(message) {
  if (!message) {
    errorBox.hidden = true;
    errorBox.textContent = "";
    return;
  }
  errorBox.hidden = false;
  errorBox.textContent = message;
}

async function loadRoles() {
  const response = await fetch("/api/v1/roles");
  const roles = await response.json();
  roleSelect.innerHTML = "";
  roles.forEach((role) => {
    const option = document.createElement("option");
    option.value = role.id;
    option.textContent = `${role.label} — ${role.description}`;
    roleSelect.appendChild(option);
  });
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setError("");

  const message = messageInput.value;
  if (!message.trim()) {
    setError("El mensaje no puede estar vacío");
    return;
  }

  const payload = {
    conversation_id: conversationId,
    role: roleSelect.value,
    channel: "web",
    message,
  };

  renderMessage("user", message);
  messageInput.value = "";

  try {
    const response = await fetch("/api/v1/chat/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data?.error?.message || "Error enviando mensaje");
    }

    conversationId = data.conversation_id;
    renderMessage("assistant", data.assistant_message.content);
  } catch (error) {
    setError(error.message || "Ocurrió un error");
  }
});

loadRoles().catch((error) => {
  setError(error.message || "No se pudieron cargar los roles");
});
