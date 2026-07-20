document.getElementById('chatForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const inputField = document.getElementById('userInput');
    const chatWindow = document.getElementById('chatWindow');
    const npcSelect = document.getElementById('npcSelect');
    
    const userMessage = inputField.value.trim();
    if (!userMessage) return;
    
    // 1. Immediately inject Player Chat block into the dynamic UI Feed
    appendMessageElement('Player', userMessage, 'text-blue-400', 'bg-slate-850 border border-blue-900/50 ml-auto max-w-xl');
    inputField.value = '';
    chatWindow.scrollTop = chatWindow.scrollHeight;

    try {
        // 2. Perform production async network fetch execution block to the REST endpoint
        const response = await fetch('/api/v1/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                npc_id: npcSelect.value,
                message: userMessage
            })
        });

        if (!response.ok) throw new Error('System anomaly detected during runtime transaction.');
        
        const data = await response.json();

        // 3. Update the Diagnostics Panels dynamically
        document.getElementById('telemetryEmotion').textContent = data.emotion.toUpperCase();
        document.getElementById('telemetryAffinity').textContent = data.relationship_change;
        document.getElementById('jsonDebug').textContent = JSON.stringify(data, null, 2);

        // 4. Inject structural API Character response dialogue back to layout text flow
        const activeCharacterName = npcSelect.options[npcSelect.selectedIndex].text;
        appendMessageElement(activeCharacterName, data.dialogue, 'text-emerald-400', 'bg-slate-800 border border-slate-700 max-w-2xl');
        chatWindow.scrollTop = chatWindow.scrollHeight;

    } catch (error) {
        appendMessageElement('Error Daemon', error.message, 'text-red-400', 'bg-red-950/40 border border-red-900 max-w-xl');
    }
});

function appendMessageElement(sender, text, senderColorClass, elementBgClass) {
    const chatWindow = document.getElementById('chatWindow');
    const msgBlock = document.createElement('div');
    msgBlock.className = `${elementBgClass} rounded-lg p-4 shadow-sm transition-all`;
    
    msgBlock.innerHTML = `
        <p class="text-xs ${senderColorClass} font-semibold uppercase mb-1">${sender}</p>
        <p class="text-slate-200 leading-relaxed">${text}</p>
    `;
    chatWindow.appendChild(msgBlock);
}
