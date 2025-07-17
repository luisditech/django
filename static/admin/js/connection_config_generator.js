document.addEventListener('DOMContentLoaded', function () {
    const nameField = document.getElementById('id_name');
    const typeField = document.getElementById('id_type');
    const ownerField = document.getElementById('id_owner');
    const dynamicSectionId = 'dynamic-fields';

    // Campos para conexión a Shopify
    const dynamicFormFields = {
        shopify: [
            {name: 'api_key', label: 'API Key', type: 'text', placeholder: 'My Shopify API Key'},
            {name: 'password', label: 'Password', type: 'password', placeholder: '******'},
            {name: 'shop_url', label: 'Shop URL', type: 'url', placeholder: 'https://my-store-name.myshopify.com'},
            {name: 'api_version', label: 'API Version', type: 'text', placeholder: 'example: 2023-01'},
        ],
        sftp: [
            {
                name: 'host',
                label: 'Host',
                type: 'text',
                placeholder: 'sftp://example.yourserver.com or sftp://your-ip-address'
            },
            {name: 'port', label: 'Port', type: 'number', placeholder: '23767 or your custom port'},
            {name: 'username', label: 'Username', type: 'text', placeholder: 'username'},
            {name: 'password', label: 'Password', type: 'password', placeholder: 'password'}
        ],
        ftp: [
            {
                name: 'host',
                label: 'Host',
                type: 'text',
                placeholder: 'ftp://example.yourserver.com or ftp://your-ip-address'
            },
            {name: 'port', label: 'Port', type: 'number', placeholder: '21 or your custom port'},
            {name: 'username', label: 'Username', type: 'text', placeholder: 'username'},
            {name: 'password', label: 'Password', type: 'password', placeholder: 'password'}
        ],
        rest: [
            {name: 'base_url', label: 'Base URL', type: 'url', placeholder: 'https://my-api.example.com or ip-address'},
            {
                name: 'auth_type',
                label: 'Authentication Type',
                type: 'select',
                options: ['none', 'basic', 'bearer', 'api_key']
            }
        ],
        graphql: [
            {
                name: 'endpoint_url',
                label: 'Endpoint URL',
                type: 'url',
                placeholder: 'https://my-api.example.com or ip-address'
            },
            {
                name: 'auth_type',
                label: 'Authentication Type',
                type: 'select',
                options: ['none', 'basic', 'bearer', 'api_key']
            }
        ],
        restlet: [
            {
                name: 'restlet_url',
                label: 'Restlet Endpoint URL',
                type: 'url',
                placeholder: 'https://my-api.example.com or ip-address'
            },
            {name: 'account_id', label: 'Account ID', type: 'text', placeholder: 'Account ID'},
            {name: 'consumer_key', label: 'Consumer Key', type: 'text', placeholder: 'Consumer Key'},
            {name: 'consumer_secret', label: 'Consumer Secret', type: 'text', placeholder: 'Consumer Secret'},
            {name: 'token_id', label: 'Token ID', type: 'text', placeholder: 'Token ID'},
            {name: 'token_secret', label: 'Token Secret', type: 'text', placeholder: 'Token Secret'},
        ],
        netsuite: [
            {name: 'account', label: 'Account ID', type: 'text', placeholder: 'Account ID'},
            {name: 'consumer_key', label: 'Consumer Key', type: 'text', placeholder: 'Consumer Key'},
            {name: 'consumer_secret', label: 'Consumer Secret', type: 'text', placeholder: 'Consumer Secret'},
            {name: 'token_key', label: 'Token Key', type: 'text', placeholder: 'Token Key'},
            {name: 'token_secret', label: 'Token Secret', type: 'text', placeholder: 'Token Secret'},
            {name: 'realm', label: 'Realm', type: 'text', placeholder: 'Realm'},
            {name: 'script_id', label: 'Script ID', type: 'text', placeholder: 'Script ID'},
            {name: 'deploy_id', label: 'Deploy ID', type: 'text', placeholder: 'Deploy ID'},
        ]
    };

    // Auth fields api rest connection.
    const authFields = {
        basic: [
            {name: 'auth_username', label: 'Username', type: 'text', placeholder: 'username'},
            {name: 'auth_password', label: 'Password', type: 'password', placeholder: 'password'}
        ],
        bearer: [
            {name: 'auth_token', label: 'Bearer Token', type: 'text', placeholder: 'Bearer token'},
        ],
        api_key: [
            {
                name: 'auth_api_key_header_name',
                label: 'Header Name (e.g. Authorization)',
                type: 'text',
                placeholder: 'api key'
            },
            {name: 'auth_api_key_header_value', label: 'Header Value', type: 'text', placeholder: 'username'}
        ]
    };

    // Validación de campos obligatorios general information
    function areRequiredFieldsFilled() {
        return nameField.value.trim() !== '' &&
            typeField.value.trim() !== '' &&
            ownerField.value.trim() !== '';
    }

    // Evitar que pase de tabs en tabs hasta llenar los campos de general info
    function blockTabs() {
        const tabs = document.getElementById('jazzy-tabs');
        Array.from(tabs.children).forEach((tab, i) => {
            if (i > 0) {
                tab.onclick = function (e) {
                    if (!areRequiredFieldsFilled()) {
                        e.preventDefault();
                        e.stopPropagation();
                        alert('Por favor completa la sección "Información General" antes de continuar.');
                    }
                };
            }
        });
    }

    // Agrega el evento de clic a los botones next y prev
    function setTabClickEvent(position) {
        const tabs = document.getElementById('jazzy-tabs');
        const currentTab = Array.from(tabs.children)[position - 1];
        currentTab.querySelector('a').click();
    }

    // Agrega dinámicamente el botón siguiente (next)
    function addNextButton(position) {
        const button = document.createElement('button');
        button.id = `next-tab-button-${position}`;
        button.className = 'btn btn-primary mt-3';
        button.type = 'button';
        button.innerText = 'Next';

        button.onclick = function () {
            if (areRequiredFieldsFilled()) {
                const tabs = document.getElementById('jazzy-tabs');
                const currentTab = Array.from(tabs.children)[position + 1];
                currentTab.querySelector('a').click();
                renderFields();
            } else {
                alert('Debes completar todos los campos obligatorios antes de continuar.');
            }
        };
        return button;
    }

    // Agrega dinámicamente el botón atrás (Back)
    function addPreviousButton(position) {
        const button = document.createElement('button');
        button.id = `previous-tab-button-${position}`;
        button.className = 'btn btn-outline-primary mt-3';
        button.type = 'button';
        button.innerText = 'Back';
        button.style = "margin-right: 1rem !important;";

        button.onclick = function () {
            setTabClickEvent(position);
        };
        return button;
    }

    // Agrega los botones (Back, Next) en cada tab dinámicamente.
    function addButtons() {
        const tabsContentContainer = document.getElementsByClassName('tab-content')[0];
        if (tabsContentContainer.length === 0 || !tabsContentContainer) return;
        const tabsContent = Array.from(tabsContentContainer.children);
        setTimeout(() => {
            setTabClickEvent(1);
        }, 500);
        tabsContent.forEach((tabContent, i) => {
            let nextButton = document.createElement('button');
            nextButton.id = 'not-assigned-value';
            let prevButton = document.createElement('button');
            prevButton.id = 'not-assigned-value';
            const validateLastItem = tabsContent[i + 1];
            const validatePreviousItem = tabsContent[i - 1];
            if (validateLastItem && !validatePreviousItem) {
                nextButton = addNextButton(i);
            }
            if (validateLastItem && validatePreviousItem) {
                nextButton = addNextButton(i);
                prevButton = addPreviousButton(i);
            }
            if (!validateLastItem && validatePreviousItem) {
                prevButton = addPreviousButton(i);
            }
            if (prevButton.id !== 'not-assigned-value') {
                tabContent.appendChild(prevButton);
            }
            if (nextButton.id !== 'not-assigned-value') {
                tabContent.appendChild(nextButton);
            }
        });
    }

    blockTabs(); // Inicia el bloqueo de tabs
    addButtons(); // Inicia la adición de botones back y next :)

    const configField = document.getElementById('id_config'); // Campo donde se arma el json de configuraciones.

    /**
     * RENDER DYNAMIC FIELDS FORM
     */

    function renderFields() {
        const old = document.getElementById(dynamicSectionId);
        if (old) old.remove(); // Eliminamos el container anterior para generar le nuevo.

        if (!typeField.value) return; // Validamos que efectivamente se seleccionó Shopify en el select

        const container = document.createElement('div');
        container.id = dynamicSectionId;
        container.className = 'mt-3';

        const config = JSON.parse(configField.value || '{}');

        dynamicFormFields[typeField.value].forEach(field => {
            const wrapper = document.createElement('div');
            wrapper.className = 'form-group';

            const label = document.createElement('label');
            label.setAttribute('for', `config-${field.name}`);
            label.textContent = field.label;

            if (field.type === 'select') {
                const select = document.createElement('select');
                select.className = 'form-control';
                select.id = `config-${field.name}`;
                field.options.forEach(opt => {
                    const option = document.createElement('option');
                    option.value = opt;
                    option.text = opt.charAt(0).toUpperCase() + opt.slice(1);
                    if (config[field.name] === opt) option.selected = true;
                    select.appendChild(option);
                });
                select.onchange = function () {
                    updateConfig();
                    renderAuthFields(select.value);
                };
                wrapper.appendChild(label);
                wrapper.appendChild(select);
            } else {
                const input = document.createElement('input');
                input.type = field.type;
                input.className = 'form-control';
                input.id = `config-${field.name}`;
                input.value = config[field.name] || '';
                input.oninput = updateConfig;
                input.placeholder = field.placeholder;
                wrapper.appendChild(label);
                wrapper.appendChild(input);
            }

            container.appendChild(wrapper);
        });

        configField.parentElement.insertBefore(container, configField);
        renderCustomHeaders(config);
        addTestConnectionButton(configField.parentElement);
        updateConfig();

    }

    /**
     * Render authfields api rest authentication.
     * @param authType
     */
    function renderAuthFields(authType) {
        const existing = document.getElementById('auth-fields');
        if (existing) existing.remove();

        if (!authFields[authType]) return;

        const authWrapper = document.createElement('div');
        authWrapper.id = 'auth-fields';
        authWrapper.className = 'mt-3';

        const config = JSON.parse(configField.value || '{}');

        authFields[authType].forEach(field => {
            const wrapper = document.createElement('div');
            wrapper.className = 'form-group';

            const label = document.createElement('label');
            label.setAttribute('for', `config-${field.name}`);
            label.textContent = field.label;

            const input = document.createElement('input');
            input.type = field.type;
            input.className = 'form-control';
            input.id = `config-${field.name}`;
            input.value = config[field.name] || '';
            input.placeholder = field.placeholder;
            input.oninput = updateConfig;

            wrapper.appendChild(label);
            wrapper.appendChild(input);
            authWrapper.appendChild(wrapper);
        });

        const insertAfter = document.getElementById('config-auth_type');
        insertAfter.parentElement.parentElement.insertBefore(authWrapper, insertAfter.parentElement.nextSibling);
    }

    /**
     * Render custom headers
     * @param config
     */
    function renderCustomHeaders(config) {
        let existing = document.getElementById('custom-headers');
        if (existing) existing.remove();

        const wrapper = document.createElement('div');
        wrapper.id = 'custom-headers';
        wrapper.className = 'mt-3';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = 'toggle-custom-headers';

        const label = document.createElement('label');
        label.textContent = ' Add or modify custom headers';
        label.htmlFor = 'toggle-custom-headers';
        label.style.marginLeft = '0.5rem';

        const toggleWrapper = document.createElement('div');
        toggleWrapper.appendChild(checkbox);
        toggleWrapper.appendChild(label);
        wrapper.appendChild(toggleWrapper);

        const inputsWrapper = document.createElement('div');
        inputsWrapper.id = 'custom-headers-inputs';
        inputsWrapper.style.display = 'none';
        inputsWrapper.className = 'mt-2';

        const keyInput = document.createElement('input');
        keyInput.type = 'text';
        keyInput.placeholder = 'Header name';
        keyInput.className = 'form-control mb-2';
        keyInput.id = 'custom-header-key';

        const valueInput = document.createElement('input');
        valueInput.type = 'text';
        valueInput.placeholder = 'Header value';
        valueInput.className = 'form-control mb-2';
        valueInput.id = 'custom-header-value';

        const addBtn = document.createElement('button');
        addBtn.className = 'btn btn-outline-primary mb-2';
        addBtn.type = 'button';
        addBtn.textContent = 'Agregar header';
        addBtn.onclick = function () {
            const k = keyInput.value.trim();
            const v = valueInput.value.trim();
            if (k && v) {
                const current = JSON.parse(configField.value || '{}');
                const entry = `${k}:${v}`;
                let existing = current.custom_headers || '';
                if (existing) existing += `;${entry}`;
                else existing = entry;
                current.custom_headers = existing;
                configField.value = JSON.stringify(current, null, 2);
                renderCustomHeaders(current);
            }
        };

        inputsWrapper.appendChild(keyInput);
        inputsWrapper.appendChild(valueInput);
        inputsWrapper.appendChild(addBtn);

        if (config.custom_headers) {
            const table = document.createElement('ul');
            table.className = 'list-group';

            config.custom_headers.split(';').forEach((entry, index) => {
                const headerItem = document.createElement('li');
                headerItem.className = 'list-group-item d-flex justify-content-between align-items-center py-1 px-2';
                headerItem.textContent = entry;
                headerItem.style = "margin-bottom: 1rem !important;";

                const deleteBtn = document.createElement('button');
                deleteBtn.type = 'button';
                deleteBtn.className = 'btn btn-sm btn-danger ml-2';
                deleteBtn.textContent = 'Delete';
                deleteBtn.onclick = function () {
                    const current = JSON.parse(configField.value || '{}');
                    const headers = (current.custom_headers || '').split(';').filter((_, i) => i !== index);
                    current.custom_headers = headers.join(';');
                    configField.value = JSON.stringify(current, null, 2);
                    renderCustomHeaders(current);
                };

                headerItem.appendChild(deleteBtn);
                table.appendChild(headerItem);
            });

            inputsWrapper.appendChild(table);
        }

        checkbox.onchange = function () {
            inputsWrapper.style.display = checkbox.checked ? 'block' : 'none';
        };

        wrapper.appendChild(inputsWrapper);
        configField.parentElement.insertBefore(wrapper, configField);
    }

    // Actualiza el body del json con los valores agregados en los campos dinámicos
    function updateConfig() {
        const config = {};
        const inputs = document.querySelectorAll('[id^="config-"]');
        inputs.forEach(input => {
            const key = input.id.replace('config-', '');
            config[key] = input.value;
        });

        const current = JSON.parse(configField.value || '{}');
        if (current.custom_headers) {
            config.custom_headers = current.custom_headers;
        }

        configField.value = JSON.stringify(config, null, 2);
    }

    /**
     * TEST CONNECTIONS
     */
    function addTestConnectionButton(container) {
        if (document.getElementById('test-connection-button')) return;

        container.appendChild(document.createElement('br'));
        const button = document.createElement('button');
        button.className = 'btn btn-success mt-3';
        button.id = 'test-connection-button';
        button.type = 'button';
        button.innerText = 'Probar conexión';

        const resultBox = document.createElement('div');
        resultBox.className = 'mt-2';

        button.onclick = async function () {
            const type = typeField.value;
            let config;
            try {
                config = JSON.parse(configField.value);
            } catch (e) {
                alert("El JSON de configuración no es válido.");
                return;
            }

            const res = await fetch("/api/connections/test/", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({type, config})
            });

            const data = await res.json();
            if (res.ok) {
                switch (data.status) {
                    case 200 || 201:
                        resultBox.innerHTML = `<div class="alert alert-success">✅ Connection successfully (Status: ${data.status})</div>`;
                        break;
                    case 401:
                        resultBox.innerHTML = `<div class="alert alert-warning">✅ You are connected but the credentials are not authorized. (Status: ${data.status})</div>`;
                        break;
                    case 404:
                        resultBox.innerHTML = `<div class="alert alert-danger">❌ Not found. (Status: ${data.status})</div>`;
                        break;
                }
            } else {
                resultBox.innerHTML = `<div class="alert alert-danger">❌ Error: ${data.error || 'Connection failed'}</div>`;
            }
        };

        container.appendChild(button);
        container.appendChild(resultBox);
    }

});
