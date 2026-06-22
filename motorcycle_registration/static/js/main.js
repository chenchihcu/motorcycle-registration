/* ============================================================
   重機車隊報名系統 — 前端互動 JS
   - Toast 浮動通知系統（轉換 Bootstrap flash alerts）
   - 表單送出 Loading 狀態（防止重複送出）
   - 無第三方依賴，純 Vanilla JS
   ============================================================ */

(function () {
    'use strict';

    /* =================================================================
     * 1. Toast 浮動通知系統
     * ================================================================= */

    /**
     * 將伺服器端的 flash alerts 轉換為 Toast 浮動通知
     * 支援 success / error (danger) / warning / info 四種類型
     * 每則 Toast 5 秒後自動消失，可按關閉鈕手動關閉
     */
    function initToastNotifications() {
        var flashMessages = document.querySelectorAll('#flash-container .toast-notification');
        if (flashMessages.length === 0) return;

        var toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);

        flashMessages.forEach(function (el) {
            var toastType = 'info';
            if (el.classList.contains('success')) toastType = 'success';
            if (el.classList.contains('error'))   toastType = 'error';
            if (el.classList.contains('warning')) toastType = 'warning';

            var message = el.textContent.trim();
            if (!message) return;

            var toast = createToast(message, toastType);
            toastContainer.appendChild(toast);
            el.remove();
        });

        var flashContainer = document.getElementById('flash-container');
        if (flashContainer && flashContainer.children.length === 0 && flashContainer.textContent.trim() === '') {
            flashContainer.remove();
        }
    }

    function createToast(message, type) {
        var el = document.createElement('div');
        el.className = 'toast-notification ' + type;
        el.setAttribute('role', 'alert');

        var text = document.createElement('span');
        text.textContent = message;

        var closeBtn = document.createElement('button');
        closeBtn.className = 'toast-close';
        closeBtn.innerHTML = '&#x2715;';
        closeBtn.setAttribute('aria-label', '關閉');
        closeBtn.addEventListener('click', function () { dismissToast(el); });

        el.appendChild(text);
        el.appendChild(closeBtn);

        setTimeout(function () { dismissToast(el); }, 5000);
        return el;
    }

    function dismissToast(toast) {
        if (toast.dataset.dismissing === 'true') return;
        toast.dataset.dismissing = 'true';
        toast.classList.add('toast-hiding');
        setTimeout(function () {
            if (toast.parentNode) toast.parentNode.removeChild(toast);
            var container = document.querySelector('.toast-container');
            if (container && container.children.length === 0) container.remove();
        }, 300);
    }

    /* =================================================================
     * 2. 表單送出 Loading 狀態
     *    - 所有 POST 表單在送出時顯示按鈕 spinner + 全域遮罩
     *    - data-no-loading 屬性可跳過
     * ================================================================= */

    function initFormLoading() {
        var forms = document.querySelectorAll('form');
        forms.forEach(function (form) {
            // 只處理 POST 表單，且未標記 data-no-loading
            if (form.method !== 'post' && form.method !== 'POST') return;
            if (form.hasAttribute('data-no-loading')) return;

            form.addEventListener('submit', function (e) {
                // 如果表單已經在送出中，阻止重複送出
                if (form.dataset.submitting === 'true') {
                    e.preventDefault();
                    return;
                }

                form.dataset.submitting = 'true';

                // 為送出按鈕加上 loading 動畫
                var submitBtn = form.querySelector('[type="submit"]');
                if (submitBtn && !submitBtn.disabled) {
                    submitBtn.classList.add('btn-loading');
                    submitBtn.disabled = true;
                }

                // 顯示全域載入遮罩
                var overlay = document.createElement('div');
                overlay.className = 'overlay-loading';
                overlay.innerHTML =
                    '<div class="spinner"></div>' +
                    '<div class="overlay-text">處理中，請稍候…</div>';
                document.body.appendChild(overlay);
            });
        });
    }

    /* =================================================================
     * 3. 初始化
     * ================================================================= */

    function init() {
        initToastNotifications();
        initFormLoading();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
