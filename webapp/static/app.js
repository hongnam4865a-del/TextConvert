document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('drop-zone');
    const queueList = document.getElementById('queue-list');
    const queueCount = document.getElementById('queue-count');
    const convertBtn = document.getElementById('convert-btn');
    const clearBtn = document.getElementById('clear-btn');
    const targetFormat = document.getElementById('target-format');
    const resultArea = document.getElementById('result-area');
    const resultList = document.getElementById('result-list');
    const uploadPrompt = document.getElementById('upload-prompt');
    const statusText = document.getElementById('status-text');
    const recentList = document.getElementById('recent-list');
    const logPanel = document.getElementById('log-panel');
    const toast = document.getElementById('toast');

    let queue = [];
    let isConverting = false;

    function formatSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    function pluralize(count, singular, plural) {
        return count === 1 ? `${count} ${singular}` : `${count} ${plural}`;
    }

    function showToast(message, type = 'info') {
        toast.textContent = message;
        toast.className = 'toast ' + type;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3000);
    }

    function updateStatus(text, type = '') {
        statusText.textContent = text;
        statusText.className = 'status-text ' + type;
    }

    function updateQueueUI() {
        queueList.innerHTML = '';
        if (queue.length === 0) {
            queueList.innerHTML = `
                <div class="empty-state">
                    <p>No files</p>
                    <span>Click upload or drag files to the workspace</span>
                </div>`;
            convertBtn.disabled = true;
        } else {
            convertBtn.disabled = isConverting;
            queue.forEach((file, index) => {
                const item = document.createElement('div');
                item.className = 'queue-item';
                item.innerHTML = `
                    <div class="file-icon">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                        </svg>
                    </div>
                    <div class="file-info">
                        <div class="file-name" title="${file.name}">${file.name}</div>
                        <div class="file-size">${formatSize(file.size)}</div>
                    </div>
                    <button class="remove-btn" data-index="${index}" title="Remove">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                `;
                queueList.appendChild(item);
            });

            queueList.querySelectorAll('.remove-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const idx = parseInt(e.currentTarget.dataset.index);
                    queue.splice(idx, 1);
                    updateQueueUI();
                });
            });
        }
        queueCount.textContent = pluralize(queue.length, 'file', 'files');
    }

    function addFiles(files) {
        const validFiles = Array.from(files).filter(f => f.size > 0);
        if (validFiles.length === 0) return;
        queue.push(...validFiles);
        updateQueueUI();
        showToast(pluralize(validFiles.length, 'file added', 'files added'), 'success');
    }

    fileInput.addEventListener('change', () => addFiles(fileInput.files));

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        addFiles(e.dataTransfer.files);
    });

    clearBtn.addEventListener('click', () => {
        queue = [];
        updateQueueUI();
        resultList.innerHTML = '';
        resultArea.classList.add('hidden');
        uploadPrompt.classList.remove('hidden');
        updateStatus('Waiting for files');
    });

    function appendResult(name, url, size, success, message) {
        const item = document.createElement('div');
        item.className = 'result-item ' + (success ? 'success' : 'error');
        item.innerHTML = `
            <div class="result-info">
                <div class="result-name" title="${name}">${name}</div>
                <div class="result-meta">${success ? formatSize(size) : message}</div>
            </div>
            ${success ? `<a class="download-btn" href="${url}" download>Download</a>` : ''}
        `;
        resultList.appendChild(item);
    }

    async function doConvert() {
        if (queue.length === 0) return;
        isConverting = true;
        convertBtn.disabled = true;
        updateStatus('Converting...', 'processing');
        resultArea.classList.remove('hidden');
        uploadPrompt.classList.add('hidden');
        resultList.innerHTML = '';

        const format = targetFormat.value;

        try {
            if (queue.length === 1) {
                const formData = new FormData();
                formData.append('file', queue[0]);
                formData.append('target_format', format);

                const res = await fetch('/api/convert', { method: 'POST', body: formData });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Conversion failed');

                appendResult(data.filename, data.download_url, data.size || 0, true, '');
                showToast('Conversion successful', 'success');
                updateStatus('Conversion complete', 'success');
            } else {
                const formData = new FormData();
                queue.forEach(f => formData.append('files', f));
                formData.append('target_format', format);

                const res = await fetch('/api/batch', { method: 'POST', body: formData });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Batch conversion failed');

                data.results.forEach(r => appendResult(r.filename, r.download_url, r.size || 0, true, ''));
                showToast(`Batch conversion complete: ${pluralize(data.count, 'file', 'files')}`, 'success');
                updateStatus('Batch conversion complete', 'success');
            }

            queue = [];
            updateQueueUI();
            loadRecentFiles();
        } catch (err) {
            console.error(err);
            appendResult('Conversion failed', '', 0, false, err.message);
            showToast(err.message, 'error');
            updateStatus('Conversion failed', 'error');
        } finally {
            isConverting = false;
            updateQueueUI();
            loadLogs();
        }
    }

    convertBtn.addEventListener('click', doConvert);

    async function loadRecentFiles() {
        try {
            const res = await fetch('/api/files');
            const data = await res.json();
            recentList.innerHTML = '';
            if (data.files.length === 0) {
                recentList.innerHTML = '<div class="empty-state small">No results</div>';
                return;
            }
            data.files.slice(0, 8).forEach(file => {
                const item = document.createElement('div');
                item.className = 'queue-item';
                item.innerHTML = `
                    <div class="file-info">
                        <div class="file-name" title="${file.name}">${file.name}</div>
                        <div class="file-size">${formatSize(file.size)}</div>
                    </div>
                    <a class="download-btn" href="${file.download_url}" download>Download</a>
                `;
                recentList.appendChild(item);
            });
        } catch (err) {
            recentList.innerHTML = '<div class="empty-state small">Failed to load</div>';
        }
    }

    async function loadLogs() {
        try {
            const res = await fetch('/api/logs?lines=80');
            const data = await res.json();
            logPanel.innerHTML = '';
            if (data.logs.length === 0) {
                logPanel.innerHTML = '<div class="log-placeholder">Logs will appear here</div>';
                return;
            }
            data.logs.forEach(line => {
                const div = document.createElement('div');
                div.className = 'log-line';
                div.textContent = line;
                logPanel.appendChild(div);
            });
            logPanel.scrollTop = logPanel.scrollHeight;
        } catch (err) {
            logPanel.innerHTML = '<div class="log-placeholder">Failed to load logs</div>';
        }
    }

    loadRecentFiles();
    loadLogs();
    setInterval(loadLogs, 5000);
});
