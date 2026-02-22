/**
 * Nonprofit AI Chatbot Widget
 * Embed this on your WordPress site for site-wide chatbot access
 * 
 * Usage in WordPress:
 * Add this to your theme's footer or use a custom code snippet plugin:
 * <script src="https://your-railway-domain.com/widget.js"></script>
 */

(function() {
  const API_URL = window.CHATBOT_API_URL || 'https://your-railway-domain.com';
  const WIDGET_ID = 'nonprofit-chatbot-widget';
  const STORAGE_KEY = 'chatbot_messages';

  // Create widget HTML
  const createWidget = () => {
    const container = document.createElement('div');
    container.id = WIDGET_ID;
    container.innerHTML = `
      <style>
        #${WIDGET_ID} {
          position: fixed;
          bottom: 20px;
          right: 20px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          z-index: 99999;
        }

        .chatbot-header {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 16px;
          border-radius: 12px 12px 0 0;
          cursor: pointer;
          display: flex;
          justify-content: space-between;
          align-items: center;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .chatbot-header h3 {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
        }

        .chatbot-minimize {
          background: none;
          border: none;
          color: white;
          cursor: pointer;
          font-size: 20px;
        }

        .chatbot-messages {
          width: 380px;
          height: 500px;
          background: white;
          border: 1px solid #e0e0e0;
          border-top: none;
          display: flex;
          flex-direction: column;
          border-radius: 0 0 12px 12px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
          overflow: hidden;
        }

        .messages-container {
          flex: 1;
          overflow-y: auto;
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .message {
          display: flex;
          gap: 8px;
          margin-bottom: 8px;
        }

        .message.user {
          justify-content: flex-end;
        }

        .message-bubble {
          max-width: 70%;
          padding: 10px 14px;
          border-radius: 12px;
          line-height: 1.4;
          font-size: 14px;
        }

        .message.assistant .message-bubble {
          background: #f0f0f0;
          color: #333;
        }

        .message.user .message-bubble {
          background: #667eea;
          color: white;
        }

        .message-source {
          font-size: 12px;
          color: #666;
          margin-top: 4px;
          padding-left: 12px;
          border-left: 3px solid #ddd;
        }

        .input-container {
          padding: 12px;
          border-top: 1px solid #e0e0e0;
          display: flex;
          gap: 8px;
        }

        .input-container input {
          flex: 1;
          padding: 10px 12px;
          border: 1px solid #ddd;
          border-radius: 6px;
          font-size: 14px;
          outline: none;
        }

        .input-container input:focus {
          border-color: #667eea;
        }

        .input-container button {
          padding: 10px 16px;
          background: #667eea;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 600;
          transition: background 0.2s;
        }

        .input-container button:hover {
          background: #5568d3;
        }

        .input-container button:disabled {
          background: #ccc;
          cursor: not-allowed;
        }

        .loading {
          display: inline-block;
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #667eea;
          animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        .hidden {
          display: none;
        }

        @media (max-width: 480px) {
          .chatbot-messages {
            width: calc(100vw - 32px);
            height: 60vh;
            max-height: 500px;
          }
        }
      </style>

      <div class="chatbot-header">
        <h3>💬 How can we help?</h3>
        <button class="chatbot-minimize">−</button>
      </div>
      <div class="chatbot-messages">
        <div class="messages-container"></div>
        <div class="input-container">
          <input type="text" placeholder="Ask a question..." />
          <button>Send</button>
        </div>
      </div>
    `;

    return container;
  };

  // Initialize widget
  const init = () => {
    if (document.getElementById(WIDGET_ID)) return; // Already initialized

    const widget = createWidget();
    document.body.appendChild(widget);

    const header = widget.querySelector('.chatbot-header');
    const messages = widget.querySelector('.chatbot-messages');
    const container = widget.querySelector('.messages-container');
    const input = widget.querySelector('input');
    const button = widget.querySelector('button');

    let isMinimized = false;

    // Load saved messages
    loadMessages(container);

    // Toggle minimize
    header.addEventListener('click', () => {
      isMinimized = !isMinimized;
      messages.classList.toggle('hidden', isMinimized);
      header.querySelector('.chatbot-minimize').textContent = isMinimized ? '+' : '−';
    });

    // Send message
    const sendMessage = async () => {
      const query = input.value.trim();
      if (!query) return;

      // Add user message
      addMessage(container, query, 'user');
      input.value = '';
      button.disabled = true;

      // Add loading indicator
      const loadingDiv = document.createElement('div');
      loadingDiv.className = 'message assistant';
      loadingDiv.innerHTML = '<div class="message-bubble"><div class="loading"></div></div>';
      container.appendChild(loadingDiv);
      container.scrollTop = container.scrollHeight;

      try {
        const response = await fetch(`${API_URL}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query })
        });

        const data = await response.json();

        // Remove loading indicator
        container.removeChild(loadingDiv);

        // Add assistant response
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message assistant';
        msgDiv.innerHTML = `
          <div class="message-bubble">
            ${data.answer}
            ${data.sources && data.sources.length > 0 ? `
              <div class="message-source">
                <strong>Sources:</strong> ${data.sources.map(s => s.source).join(', ')}
              </div>
            ` : ''}
          </div>
        `;
        container.appendChild(msgDiv);

        // Save to history
        saveMessage({ query, answer: data.answer, sources: data.sources });

      } catch (error) {
        container.removeChild(loadingDiv);
        addMessage(container, '❌ Sorry, I encountered an error. Please try again.', 'assistant');
        console.error('Chat error:', error);
      }

      button.disabled = false;
      container.scrollTop = container.scrollHeight;
      input.focus();
    };

    button.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendMessage();
    });
  };

  // Helper functions
  const addMessage = (container, text, role) => {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    msgDiv.innerHTML = `<div class="message-bubble">${escapeHtml(text)}</div>`;
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
  };

  const escapeHtml = (text) => {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return text.replace(/[&<>"']/g, m => map[m]);
  };

  const saveMessage = (msg) => {
    let messages = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    messages.push({ ...msg, timestamp: new Date().toISOString() });
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-20))); // Keep last 20
  };

  const loadMessages = (container) => {
    const messages = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    messages.forEach(msg => {
      addMessage(container, msg.query, 'user');
      addMessage(container, msg.answer, 'assistant');
    });
  };

  // Load when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
