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
     * 顯示／更新欄位的錯誤文字（不只靠紅色邊框傳達，符合無障礙：狀態不可只靠顏色）
     * 使用與伺服器端錯誤相同的樣式（.text-danger.small），並標記 js-field-error 以利清除
     */
    function setFieldError(field, message) {
        let holder = field.parentNode.querySelector('.js-field-error');
        if (!holder) {
            holder = document.createElement('div');
            holder.className = 'text-danger small mt-1 js-field-error';
            field.insertAdjacentElement('afterend', holder);
        }
        holder.textContent = message;
    }

    function clearFieldError(field) {
        const holder = field.parentNode.querySelector('.js-field-error');
        if (holder) holder.remove();
    }

    /**
     * 確認密碼欄位的等值檢查（HTML5 約束無法表達 EqualTo，需前端補強，
     * 否則確認密碼不一致時仍會顯示通過、與伺服器結果矛盾）。
     * 回傳錯誤訊息字串；通過則回傳空字串。
     */
    function confirmPasswordError(field) {
        if (field.name !== 'confirm_password' && field.id !== 'confirm_password') return '';
        const form = field.form;
        if (!form) return '';
        const source = form.querySelector('#new_password') || form.querySelector('#password');
        if (source && source.value !== field.value) return '密碼不一致';
        return '';
    }

    /**
     * 對單一欄位執行驗證，更新 .is-invalid 狀態與錯誤文字。
     * 不再加 .is-valid（綠勾）—避免在 EqualTo 等伺服器端規則上顯示假性通過。
     * 回傳 true 表示通過。
     */
    function validateField(field) {
        const extraError = field.validity.valid ? confirmPasswordError(field) : '';
        const ok = field.validity.valid && !extraError;
        if (ok) {
            field.classList.remove('is-valid', 'is-invalid');
            clearFieldError(field);
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
            // 說明「如何修正」而非只給紅框
            setFieldError(field, extraError || field.validationMessage || '此欄位填寫有誤');
        }
        return ok;
    }

    /**
     * 清除欄位的驗證狀態
     */
    function clearValidation(field) {
        field.classList.remove('is-valid', 'is-invalid');
        clearFieldError(field);
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
                    if (!validateField(field)) {
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
