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

// Mobile Drawer Navigation Toggle
function toggleMobileNav() {
  const drawer = document.getElementById('mobileNavDrawer');
  const backdrop = document.getElementById('mobileNavBackdrop');
  if (!drawer) return;

  const isOpen = drawer.classList.contains('show');
  if (isOpen) {
    drawer.classList.remove('show');
    if (backdrop) backdrop.classList.remove('show');
    document.body.style.overflow = '';
  } else {
    drawer.classList.add('show');
    if (backdrop) backdrop.classList.add('show');
    document.body.style.overflow = 'hidden';
  }
}

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

// ==========================================================================
// REDESIGNED CREATE POST & EXTENDED WORKSPACE INTERACTIVITY
// ==========================================================================

// Expand / Extend Modal Toggle
function toggleModalExpand() {
  const dialog = document.getElementById('createPostModalDialog');
  const icon   = document.getElementById('expandToggleIcon');
  const text   = document.getElementById('expandToggleText');
  if (!dialog) return;

  const isExpanded = dialog.classList.toggle('modal-expanded');
  if (icon) {
    icon.className = isExpanded ? 'bi bi-arrows-angle-contract' : 'bi bi-arrows-angle-expand';
  }
  if (text) {
    text.innerText = isExpanded ? 'Compact View' : 'Expand Editor';
  }
}

// Expand / Extend Standalone Page Toggle
function togglePageExpand() {
  const container = document.getElementById('pageCreateContainer');
  const card      = document.getElementById('pageCreateCard');
  const icon      = document.getElementById('pageExpandToggleIcon');
  const text      = document.getElementById('pageExpandToggleText');
  if (!card) return;

  const isExpanded = card.classList.toggle('is-expanded');
  if (container) {
    container.style.maxWidth = isExpanded ? '860px' : '560px';
  }
  if (icon) {
    icon.className = isExpanded ? 'bi bi-arrows-angle-contract' : 'bi bi-arrows-angle-expand';
  }
  if (text) {
    text.innerText = isExpanded ? 'Compact View' : 'Expand Editor';
  }
}

// Select AI Keyword Chip
function selectAiChip(val) {
  const input = document.getElementById('ai-keywords');
  if (input) {
    input.value = val;
    getAISuggestion();
  }
}

// Apply Quick Post Templates
function applyQuickTemplate(type) {
  const titleField = document.getElementById('id_title');
  const typeField  = document.getElementById('id_post_type');
  const descField  = document.getElementById('id_description');

  if (type === 'fyp') {
    if (titleField) titleField.value = "AI-Powered Student Collaboration Platform";
    if (typeField)  typeField.value  = "fyp";
    if (descField)  descField.value  = "We are building an intelligent platform for student project matchmaking. Looking for dedicated teammates skilled in React, Python/Django, and UI design for our Final Year Project.";
  } else if (type === 'paid') {
    if (titleField) titleField.value = "Mobile App Bug Fix & UI Polish";
    if (typeField)  typeField.value  = "paid";
    if (descField)  descField.value  = "Need an experienced Flutter/React Native developer to fix authentication bugs and polish the dashboard layout. Compensation provided upon completion.";
  }

  // Trigger preview update
  updateLivePreview();
}

function applyQuickTemplatePage(type) {
  applyQuickTemplate(type);
}

// Calculate Post Strength Quality Score
function updatePostStrengthScore(title, desc, type, skillsCount) {
  let score = 15;
  let tips  = "💡 Add a detailed description (>50 chars) and skills to attract 3x more teammates!";

  if (title.length > 5) score += 20;
  if (title.length > 15) score += 10;
  
  if (desc.length > 30) score += 20;
  if (desc.length > 80) score += 15;

  if (type) score += 10;
  if (skillsCount > 0) score += 10;
  if (skillsCount >= 2) score += 10;

  score = Math.min(100, score);

  if (score >= 80) {
    tips = "🚀 Excellent post! Highly detailed posts get 5x faster responses from top talent.";
  } else if (score >= 50) {
    tips = "👍 Good start! Add 1-2 more skill tags or deadline for even higher visibility.";
  }

  // Update DOM for modal
  const fill = document.getElementById('postStrengthFill');
  const text = document.getElementById('strengthPercentText');
  const tipsEl = document.getElementById('postStrengthTips');
  if (fill) fill.style.width = score + '%';
  if (text) text.innerText = score + '%';
  if (tipsEl) tipsEl.innerHTML = tips;

  // Update DOM for page
  const pageFill = document.getElementById('pagePostStrengthFill');
  const pageText = document.getElementById('pageStrengthPercentText');
  const pageTipsEl = document.getElementById('pagePostStrengthTips');
  if (pageFill) pageFill.style.width = score + '%';
  if (pageText) pageText.innerText = score + '%';
  if (pageTipsEl) pageTipsEl.innerHTML = tips;
}

// Live Post Preview Synchronization
function updateLivePreview() {
  const titleVal = document.getElementById('id_title')?.value.trim() || '';
  const typeVal  = document.getElementById('id_post_type')?.value || 'fyp';
  const descVal  = document.getElementById('id_description')?.value.trim() || '';
  const dateVal  = document.getElementById('id_deadline')?.value || '';

  // Get skills count & names
  let skillNames = [];
  const select2Vals = $('.select2').val();
  if (select2Vals && Array.isArray(select2Vals)) {
    skillNames = select2Vals;
  }

  // Update Modal Preview elements
  const prevTitle = document.getElementById('previewTitle');
  const prevDesc  = document.getElementById('previewDesc');
  const prevType  = document.getElementById('previewTypeBadge');
  const prevSkills= document.getElementById('previewSkillsRow');
  const prevDate  = document.getElementById('previewDeadlineText');

  if (prevTitle) {
    prevTitle.innerText = titleVal || 'Your Project Title Will Appear Here...';
  }
  if (prevDesc) {
    prevDesc.innerText = descVal || 'Enter a detailed description of your task or project requirements on the left form to see a live preview here...';
  }
  if (prevType) {
    const isFyp = typeVal.toLowerCase() === 'fyp';
    prevType.className = isFyp ? 'preview-type-badge fyp' : 'preview-type-badge paid';
    prevType.innerText = isFyp ? 'FYP' : 'Paid Task';
  }
  if (prevSkills) {
    if (skillNames.length > 0) {
      prevSkills.innerHTML = skillNames.map(s => `<span class="preview-skill-badge">${s}</span>`).join('');
    } else {
      prevSkills.innerHTML = '<span class="preview-skill-badge">Python</span><span class="preview-skill-badge">Django</span>';
    }
  }
  if (prevDate) {
    prevDate.innerHTML = dateVal ? `<i class="bi bi-calendar-event"></i> Deadline: ${dateVal}` : `<i class="bi bi-calendar-event"></i> No deadline set`;
  }

  // Update Standalone Page Preview elements
  const pagePrevTitle  = document.getElementById('pagePreviewTitle');
  const pagePrevDesc   = document.getElementById('pagePreviewDesc');
  const pagePrevType   = document.getElementById('pagePreviewTypeBadge');
  const pagePrevSkills = document.getElementById('pagePreviewSkillsRow');
  const pagePrevDate   = document.getElementById('pagePreviewDeadlineText');

  if (pagePrevTitle)  pagePrevTitle.innerText = titleVal || 'Your Project Title Will Appear Here...';
  if (pagePrevDesc)   pagePrevDesc.innerText  = descVal || 'Enter a detailed description of your task or project requirements on the left form to see a live preview here...';
  if (pagePrevType) {
    const isFyp = typeVal.toLowerCase() === 'fyp';
    pagePrevType.className = isFyp ? 'preview-type-badge fyp' : 'preview-type-badge paid';
    pagePrevType.innerText = isFyp ? 'FYP' : 'Paid Task';
  }
  if (pagePrevSkills) {
    if (skillNames.length > 0) {
      pagePrevSkills.innerHTML = skillNames.map(s => `<span class="preview-skill-badge">${s}</span>`).join('');
    } else {
      pagePrevSkills.innerHTML = '<span class="preview-skill-badge">Python</span><span class="preview-skill-badge">Django</span>';
    }
  }
  if (pagePrevDate) {
    pagePrevDate.innerHTML = dateVal ? `<i class="bi bi-calendar-event"></i> Deadline: ${dateVal}` : `<i class="bi bi-calendar-event"></i> No deadline set`;
  }

  // Calculate score
  updatePostStrengthScore(titleVal, descVal, typeVal, skillNames.length);
}

// Select2 initialization & input event listeners
$(document).ready(function() {
  function initSelect2(container) {
    var $targets = container ? $(container).find('.select2') : $('.select2');
    $targets.each(function() {
      var $el = $(this);
      var inModal = $el.closest('#addPostModal').length > 0;
      
      // Destroy existing select2 instance if re-initializing to ensure options render properly
      if ($el.hasClass("select2-hidden-accessible")) {
        $el.select2('destroy');
      }

      $el.select2({
        dropdownParent: inModal ? $('#addPostModal') : $(document.body),
        width: '100%',
        tags: true,
        tokenSeparators: [','],
        placeholder: 'Search or type skills...'
      });
    });
  }

  // Initial call for visible elements
  initSelect2();

  // Re-initialize whenever the Add Post modal opens so options render accurately
  if ($('#addPostModal').length > 0) {
    $('#addPostModal').on('shown.bs.modal', function() {
      initSelect2('#addPostModal');
      updateLivePreview();
    });
  }

  // Bind real-time input sync listeners
  $(document).on('input change', '#id_title, #id_post_type, #id_description, #id_deadline, .select2', function() {
    updateLivePreview();
  });
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
    const descField  = document.getElementById('id_description');
    if (titleField) titleField.value = data.title;
    if (descField)  descField.value  = data.description;

    // Trigger preview update
    updateLivePreview();

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

