const CV_TEXT = `PASTE LENNON CV TEXT HERE`;

const chatMessages = [
  { role: 'system', content: `You are an enthusiastic assistant for Lennon's portfolio website. Use only the following CV information to answer questions. If you cannot answer based on the CV, say you don't know. CV: ${CV_TEXT}` },
  { role: 'assistant', content: 'Hi there! I\'m excited to tell you about Lennon. Ask me anything about his experience or skills!' }
];

function addMessage(sender, text) {
  const container = document.getElementById('chatMessages');
  const msg = document.createElement('div');
  msg.className = sender;
  msg.textContent = text;
  container.appendChild(msg);
  container.scrollTop = container.scrollHeight;
}

function sendToOpenAI(apiKey, userText) {
  chatMessages.push({role:'user', content:userText});
  addMessage('user', userText);
  fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + apiKey
    },
    body: JSON.stringify({model:'gpt-3.5-turbo', messages: chatMessages})
  })
  .then(r => r.json())
  .then(data => {
    const reply = data.choices?.[0]?.message?.content?.trim() || '';
    chatMessages.push({role:'assistant', content: reply});
    addMessage('assistant', reply);
  })
  .catch(err => {
    addMessage('assistant', 'Error: ' + err.message);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const chatbox = document.getElementById('chatbot');
  const sendBtn = document.getElementById('sendBtn');
  const input = document.getElementById('chatInput');
  const keyInput = document.getElementById('apiKey');

  addMessage('assistant', chatMessages[1].content);

  sendBtn.addEventListener('click', () => {
    const text = input.value.trim();
    const key = keyInput.value.trim();
    if (!key) {
      alert('Please enter your OpenAI API key.');
      return;
    }
    if (text) {
      input.value = '';
      sendToOpenAI(key, text);
    }
  });
});
