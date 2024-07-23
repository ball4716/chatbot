document.addEventListener('DOMContentLoaded', function () {
    const sendButton = document.getElementById('send-button');
    const messageInput = document.getElementById('message-input');
    const messages = document.getElementById('messages');
    const fileUpload = document.getElementById('file-upload');

    sendButton.addEventListener('click', function () {
        sendMessage();
    });

    messageInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });

    fileUpload.addEventListener('change', function () {
        const file = fileUpload.files[0];
        if (file) {
            uploadFile(file);
        }
    });

    function sendMessage() {
        const message = messageInput.value.trim();
        if (message) {
            const messageElement = document.createElement('div');
            messageElement.textContent = message;
            messages.appendChild(messageElement);
            messageInput.value = '';
            messages.scrollTop = messages.scrollHeight;

            fetch('/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            }).then(response => response.json())
              .then(data => {
                  const responseElement = document.createElement('div');
                  responseElement.textContent = 'Bot: ' + data.response;
                  messages.appendChild(responseElement);
                  messages.scrollTop = messages.scrollHeight;
              }).catch(error => {
                  console.error('Error:', error);
              });
        }
    }

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        }).then(response => response.json())
          .then(data => {
              const messageElement = document.createElement('div');
              messageElement.textContent = 'File uploaded: ' + data.filename;
              messages.appendChild(messageElement);
              messages.scrollTop = messages.scrollHeight;
          }).catch(error => {
              console.error('Error:', error);
          });
    }

    document.addEventListener('dragover', function (e) {
        e.preventDefault();
    });

    document.addEventListener('drop', function (e) {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            uploadFile(files[0]);
        }
    });
});
