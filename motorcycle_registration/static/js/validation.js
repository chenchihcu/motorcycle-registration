/* ============================================================
   前端表單驗證 — Bootstrap 5 was-validated 模式
   - 即時欄位驗證（blur 時觸發）
   - 送出前全表單檢查
   - 支援必填、長度、格式驗證
   - 無第三方依賴，純 Vanilla JS
   ============================================================ */

(function () {
    'use strict';

    /**
     * 對單一欄位執行驗證，更新 .is-valid / .is-invalid 狀態
     */
    function validateField(field) {
        const validity = field.validity;
        if (validity.valid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
        }
    }

    /**
     * 清除欄位的驗證狀態
     */
    function clearValidation(field) {
        field.classList.remove('is-valid', 'is-invalid');
    }

    /**
     * 初始化表單驗證
     */
    function initFormValidation() {
        const forms = document.querySelectorAll('form');
        if (forms.length === 0) return;

        forms.forEach(function (form) {
            // 略過非 WTForms 的搜尋表單（GET method）
            if (form.method === 'get' || form.method === 'GET') return;

            // 取得所有需要驗證的欄位
            const fields = form.querySelectorAll('input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="reset"]):not([type="search"]), select, textarea');

            if (fields.length === 0) return;

            // 離開欄位時單一驗證
            fields.forEach(function (field) {
                field.addEventListener('blur', function () {
                    if (field.value.trim() !== '' || field.hasAttribute('required')) {
                        validateField(field);
                    } else {
                        clearValidation(field);
                    }
                });

                // 輸入時即時清除錯誤狀態
                field.addEventListener('input', function () {
                    if (field.classList.contains('is-invalid')) {
                        validateField(field);
                    }
                });

                // 變更時（select, checkbox, radio）
                field.addEventListener('change', function () {
                    if (field.classList.contains('is-invalid') || field.classList.contains('is-valid')) {
                        validateField(field);
                    }
                });
            });

            // 送出前整批驗證
            form.addEventListener('submit', function (event) {
                let isValid = true;

                fields.forEach(function (field) {
                    validateField(field);
                    if (!field.validity.valid) {
                        isValid = false;
                    }
                });

                if (!isValid) {
                    event.preventDefault();
                    event.stopPropagation();
                    // 跳到第一個錯誤欄位
                    const firstInvalid = form.querySelector('.is-invalid');
                    if (firstInvalid) {
                        firstInvalid.focus();
                        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }
            });
        });
    }

    // DOM 載入後執行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFormValidation);
    } else {
        initFormValidation();
    }
})();
