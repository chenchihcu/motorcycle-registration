/* ============================================================
   自訂 Modal 確認對話框系統
   - 取代瀏覽器原生 confirm()
   - 使用 Bootstrap 5 Modal
   - Promise-based API：showConfirmModal(message) → Promise<boolean>
   - 支援自訂按鈕文字
   ============================================================ */

(function () {
    'use strict';

    var modalInstance = null;
    var modalElement = null;
    var currentResolve = null;

    /**
     * 建立 Modal HTML（若尚未存在於 DOM）
     */
    function ensureModal() {
        if (document.getElementById('customConfirmModal')) return;

        var modalHTML =
            '<div class="modal fade" id="customConfirmModal" tabindex="-1" aria-hidden="true">' +
            '  <div class="modal-dialog modal-dialog-centered">' +
            '    <div class="modal-content">' +
            '      <div class="modal-header">' +
            '        <h5 class="modal-title"><i class="bi bi-exclamation-triangle text-warning me-1"></i>確認操作</h5>' +
            '        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="關閉"></button>' +
            '      </div>' +
            '      <div class="modal-body">' +
            '        <p class="mb-0" id="confirmMessage">確定要執行此操作嗎？</p>' +
            '      </div>' +
            '      <div class="modal-footer">' +
            '        <button type="button" class="btn btn-outline-secondary" id="confirmCancelBtn" data-bs-dismiss="modal">取消</button>' +
            '        <button type="button" class="btn btn-danger" id="confirmOkBtn">確定</button>' +
            '      </div>' +
            '    </div>' +
            '  </div>' +
            '</div>';

        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    /**
     * 顯示確認對話框
     * @param {string} message - 確認訊息
     * @param {object} [options] - 選項
     * @param {string} [options.confirmText] - 確認按鈕文字（預設「確定」）
     * @param {string} [options.cancelText] - 取消按鈕文字（預設「取消」）
     * @param {string} [options.confirmClass] - 確認按鈕 class（預設「btn-danger」）
     * @returns {Promise<boolean>} - true=確定, false=取消
     */
    window.showConfirmModal = function (message, options) {
        options = options || {};
        ensureModal();

        modalElement = document.getElementById('customConfirmModal');
        var messageEl = document.getElementById('confirmMessage');
        var okBtn = document.getElementById('confirmOkBtn');
        var cancelBtn = document.getElementById('confirmCancelBtn');

        // 設定訊息（支援 HTML 模式）
        if (options.htmlMessage) {
            messageEl.innerHTML = message;
        } else {
            messageEl.textContent = message;
        }

        // 設定按鈕文字
        okBtn.textContent = options.confirmText || '確定';
        cancelBtn.textContent = options.cancelText || '取消';

        // 設定按鈕樣式
        okBtn.className = 'btn ' + (options.confirmClass || 'btn-danger');

        return new Promise(function (resolve) {
            currentResolve = resolve;

            // 建立 Modal 實例
            modalInstance = new bootstrap.Modal(modalElement, {
                backdrop: 'static',
                keyboard: true
            });

            // 清理事件監聽（避免重複綁定）
            var newOkBtn = okBtn.cloneNode(true);
            okBtn.parentNode.replaceChild(newOkBtn, okBtn);
            var newCancelBtn = cancelBtn.cloneNode(true);
            cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);

            newOkBtn.addEventListener('click', function () {
                resolve(true);
                modalInstance.hide();
                cleanup();
            });

            newCancelBtn.addEventListener('click', function () {
                resolve(false);
                cleanup();
            });

            modalElement.addEventListener('hidden.bs.modal', function onHidden() {
                modalElement.removeEventListener('hidden.bs.modal', onHidden);
                if (currentResolve) {
                    currentResolve(false);
                    currentResolve = null;
                }
                cleanup();
            });

            modalInstance.show();
        });
    };

    function cleanup() {
        currentResolve = null;
        modalInstance = null;
    }

    /**
     * 自動取代所有 data-confirm 屬性連結/表單
     * 使用方式：<a href="..." data-confirm="確定要刪除嗎？" data-confirm-class="btn-danger">刪除</a>
     */
    function initDataConfirm() {
        document.addEventListener('click', function (e) {
            var target = e.target.closest('[data-confirm]');
            if (!target) return;

            var message = target.getAttribute('data-confirm');
            if (!message) return;

            e.preventDefault();
            e.stopPropagation();

            var href = target.getAttribute('href');
            var method = target.getAttribute('data-method') || 'GET';

            var options = {
                confirmText: target.getAttribute('data-confirm-text') || '確定',
                cancelText: target.getAttribute('data-cancel-text') || '取消',
                confirmClass: target.getAttribute('data-confirm-class') || 'btn-danger'
            };

            window.showConfirmModal(message, options).then(function (confirmed) {
                if (confirmed) {
                    if (href) {
                        if (method.toUpperCase() === 'POST') {
                            // 建立臨時表單以執行 POST
                            var form = document.createElement('form');
                            form.method = 'POST';
                            form.action = href;
                            document.body.appendChild(form);
                            form.submit();
                        } else {
                            window.location.href = href;
                        }
                    }
                }
            });
        });
    }

    // DOM 載入後執行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            ensureModal();
            initDataConfirm();
        });
    } else {
        ensureModal();
        initDataConfirm();
    }
})();
