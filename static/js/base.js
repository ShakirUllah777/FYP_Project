document.addEventListener('DOMContentLoaded', function() {
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  const mainContent = document.getElementById('main-content');

  if (sidebarToggle && sidebar && mainContent) {
    sidebarToggle.addEventListener('click', function() {
      if (window.innerWidth >= 768) {
        sidebar.classList.toggle('closed');
        mainContent.classList.toggle('expanded');
      } else {
        sidebar.classList.toggle('open');
      }
    });
  }
});

setTimeout(function () {
  document.querySelectorAll('#auto-alert').forEach(function (alert) {
    alert.classList.remove('show');
    setTimeout(() => alert.remove(), 300);
  });
}, 3000);

// Chatbot functionality
function toggleChat() {
  const csWindow = document.getElementById('cs-window');
  const csIcon   = document.getElementById('cs-bubble-icon');
  if (!csWindow || !csIcon) return;
  const open = csWindow.style.display === 'flex';
  csWindow.style.display = open ? 'none' : 'flex';
  csIcon.innerText = open ? '💬' : '✕';
}

function addMsg(text, type) {
  const csMsgs   = document.getElementById('cs-messages');
  if (!csMsgs) return;
  const div = document.createElement('div');
  div.className = 'cs-msg ' + type;
  div.innerText  = text;
  csMsgs.appendChild(div);
  csMsgs.scrollTop = csMsgs.scrollHeight;
}

function askQuick(q) {
  const input = document.getElementById('cs-input');
  if (input) {
    input.value = q;
    sendChat();
  }
}

async function sendChat() {
  const input = document.getElementById('cs-input');
  const csTyping = document.getElementById('cs-typing');
  const csMsgs   = document.getElementById('cs-messages');
  if (!input || !csTyping || !csMsgs) return;

  const q     = input.value.trim();
  if (!q) return;
  addMsg(q, 'user');
  input.value = '';
  csTyping.style.display = 'block';
  csMsgs.scrollTop = csMsgs.scrollHeight;
  try {
    const res  = await fetch(window.CHATBOT_URL || '/chatbot/', {
      method: 'POST',
      headers: { 'Content-Type':'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      body: JSON.stringify({ question: q })
    });
    const data = await res.json();
    csTyping.style.display = 'none';
    addMsg(data.reply, 'bot');
  } catch(e) {
    csTyping.style.display = 'none';
    addMsg('Sorry, something went wrong.', 'bot');
  }
}

function getCookie(name) {
  let value = null;
  if (document.cookie) {
    document.cookie.split(';').forEach(c => {
      c = c.trim();
      if (c.startsWith(name + '='))
        value = decodeURIComponent(c.slice(name.length + 1));
    });
  }
  return value;
}

// Select2 initialization
$(document).ready(function() {
  if ($('.select2').length > 0) {
    $('.select2').select2({
      dropdownParent: $('#addPostModal'),
      width: '100%',
      placeholder: 'Search for skills...'
    });
  }
});

// AI Suggestion functionality
async function getAISuggestion() {
  const keywordsInput = document.getElementById('ai-keywords');
  if (!keywordsInput) return;
  const keywords = keywordsInput.value.trim();
  if (!keywords) {
    alert('Please type some keywords first!');
    return;
  }

  // Show loading
  const aiLoading = document.getElementById('ai-loading');
  const aiSuccess = document.getElementById('ai-success');
  const aiBtn = document.getElementById('ai-btn');
  
  if (aiLoading) aiLoading.style.display = 'block';
  if (aiSuccess) aiSuccess.style.display = 'none';
  if (aiBtn) {
    aiBtn.disabled = true;
    aiBtn.innerText  = '⏳ Working...';
  }

  try {
    const res = await fetch(window.AI_SUGGEST_URL || '/ai-suggest/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ keywords: keywords })
    });

    const data = await res.json();

    // Fill the form fields
    const titleField = document.getElementById('id_title');
    const descField = document.getElementById('id_description');
    if (titleField) titleField.value = data.title;
    if (descField) descField.value = data.description;

    // Show success
    if (aiLoading) aiLoading.style.display = 'none';
    if (aiSuccess) aiSuccess.style.display = 'block';

  } catch (err) {
    alert('Something went wrong. Please try again.');
    if (aiLoading) aiLoading.style.display = 'none';
  }

  // Reset button
  if (aiBtn) {
    aiBtn.disabled    = false;
    aiBtn.innerText   = '✨ Suggest';
  }
}
