const API_BASE = '../api/v1';
let currentUser = null;
let wallets = [];
let operations = [];

function showToast(title, message, isError = false) {
    const toastEl = document.getElementById('toastNotification');
    const toastTitle = document.getElementById('toastTitle');
    const toastBody = document.getElementById('toastBody');
    const toastHeader = toastEl.querySelector('.toast-header');
    
    toastTitle.textContent = title;
    toastBody.textContent = message;
    
    // Colors based on notification type
    if (isError) {
        toastHeader.style.background = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
        toastHeader.style.color = 'white';
    } else {
        toastHeader.style.background = 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)';
        toastHeader.style.color = 'white';
    }
    
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: 3000
    });
    toast.show();
}

function showError(message) {
    showToast('❌ Error', message, true);
}

function showSuccess(message) {
    showToast('✅ Success', message, false);
}

function closeModal(modalId) {
    const modalEl = document.getElementById(modalId);
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();
}

async function register() {
    const username = document.getElementById('username').value.trim();
    if (!username) {
        showError('Enter login');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ login: username })
        });

        if (response.ok) {
            showSuccess('Registration successful!');
            currentUser = username;
            showMainSection();
        } else {
            const error = await response.json();
            showError(error.detail || 'Registration error');
        }
    } catch (e) {
        showError('Failed to connect to the server');
    }
}

async function login() {
    const username = document.getElementById('username').value.trim();
    if (!username) {
        showError('Enter login');
        return;
    }
    currentUser = username;
    // Verify user exists via /users/me
    try {
        const resp = await fetch(`${API_BASE}/users/me`, {
            headers: { 'Authorization': `Bearer ${encodeURIComponent(currentUser)}` }
        });
        if (!resp.ok) {
            const data = await resp.json().catch(() => ({}));
            showError(data.detail || 'User not found');
            return;
        }
        showMainSection();
    } catch (e) {
        showError('Failed to connect to the server');
    }
}

function logout() {
    currentUser = null;
    wallets = [];
    operations = [];
    document.getElementById('authSection').style.display = 'block';
    document.getElementById('mainSection').style.display = 'none';
    document.getElementById('username').value = '';
}

function showMainSection() {
    document.getElementById('authSection').style.display = 'none';
    document.getElementById('mainSection').style.display = 'block';
    document.getElementById('currentUser').textContent = currentUser;
    loadAllData();
}

async function loadAllData() {
    await loadWallets();
    await loadOperations();
    await updateTotalBalance();
    updateWalletSelects();
}

async function loadWallets() {
    try {
        const response = await fetch(`${API_BASE}/wallets`, {
            headers: { 'Authorization': `Bearer ${encodeURIComponent(currentUser)}` }
        });

        if (response.ok) {
            const rawWallets = await response.json();
            // Normalize backend data: currency -> lowercase, balance -> number
            wallets = rawWallets.map(w => {
                // Convert balance to a number (handle strings, Decimal-like values, etc.)
                let balance = 0;
                if (typeof w.balance === 'number') {
                    balance = w.balance;
                } else if (typeof w.balance === 'string') {
                    balance = parseFloat(w.balance) || 0;
                } else if (w.balance != null) {
                    balance = Number(w.balance) || 0;
                }
                
                return {
                    ...w,
                    currency: String(w.currency || '').toLowerCase(),
                    balance: balance
                };
            });
            renderWalletsTable();
            updateWalletSelects();
            await updateTotalBalance();
        } else if (response.status === 401) {
            console.log('User is not authorized, no wallets');
            wallets = [];
            renderWalletsTable();
            updateWalletSelects();
            await updateTotalBalance();
        } else if (response.status === 404) {
            console.log('GET /wallets endpoint not found, using empty list');
            wallets = [];
            renderWalletsTable();
            updateWalletSelects();
            await updateTotalBalance();
        } else {
            console.error('Failed to load wallets:', response.status);
            wallets = [];
            renderWalletsTable();
            updateWalletSelects();
            await updateTotalBalance();
        }
    } catch (e) {
        console.error('Connection error:', e);
        wallets = [];
        renderWalletsTable();
        updateWalletSelects();
        await updateTotalBalance();
    }
}

async function loadOperations() {
    try {
        const response = await fetch(`${API_BASE}/operations`, {
            headers: { 'Authorization': `Bearer ${encodeURIComponent(currentUser)}` }
        });

        if (response.ok) {
            const rawOperations = await response.json();
            // Normalize backend data: currency -> lowercase, amount -> number
            operations = rawOperations.map(op => {
                // Convert amount to a number (handle strings, Decimal-like values, etc.)
                let amount = 0;
                if (typeof op.amount === 'number') {
                    amount = op.amount;
                } else if (typeof op.amount === 'string') {
                    amount = parseFloat(op.amount) || 0;
                } else if (op.amount != null) {
                    amount = Number(op.amount) || 0;
                }
                
                return {
                    ...op,
                    currency: String(op.currency || '').toLowerCase(),
                    amount: amount
                };
            });
            renderOperationsTable();
        } else if (response.status === 401) {
            console.log('User is not authorized, no operations');
            operations = [];
            renderOperationsTable();
        }
    } catch (e) {
        console.error('Failed to load operations', e);
    }
}

function renderWalletsTable() {
    const tbody = document.getElementById('walletsTable');
    
    if (wallets.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">You don\'t have any wallets yet</td></tr>';
        return;
    }

    const currencySymbols = {
        'rub': '₽',
        'usd': '$',
        'eur': '€'
    };

    tbody.innerHTML = wallets.map(w => {
        // Ensure balance is a number
        const balance = typeof w.balance === 'number' ? w.balance : (parseFloat(w.balance) || 0);
        const currency = String(w.currency || '').toLowerCase();
        const symbol = currencySymbols[currency] || currency.toUpperCase();
        return `
            <tr>
                <td><strong>${w.name}</strong></td>
                <td><span class="badge bg-secondary">${currency.toUpperCase()}</span></td>
                <td class="text-end"><strong>${balance.toFixed(2)} ${symbol}</strong></td>
            </tr>
        `;
    }).join('');
}

function renderOperationsTable() {
    const tbody = document.getElementById('transactionsTable');
    
    if (operations.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No transactions</td></tr>';
        return;
    }

    const last10 = operations.slice(-10).reverse();
    
    tbody.innerHTML = last10.map(t => {
        const wallet = wallets.find(w => w.id === t.wallet_id);
        const walletName = wallet ? wallet.name : 'Unknown';
        let typeClass, typeIcon, typeLabel;
        if (t.type === 'income') {
            typeClass = 'text-success';
            typeIcon = '➕';
            typeLabel = 'Income';
        } else if (t.type === 'expense') {
            typeClass = 'text-danger';
            typeIcon = '➖';
            typeLabel = 'Expense';
        } else if (t.type === 'transfer') {
            typeClass = 'text-info';
            typeIcon = '🔄';
            typeLabel = 'Transfer';
        } else {
            typeClass = 'text-secondary';
            typeIcon = '❓';
            typeLabel = 'Unknown';
        }
        const date = new Date(t.created_at).toLocaleString('en-US', {
            day: '2-digit',
            month: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        // Ensure amount is a number
        const amount = typeof t.amount === 'number' ? t.amount : (parseFloat(t.amount) || 0);
        const currency = String(t.currency || '').toLowerCase();
        
        return `
            <tr>
                <td>${date}</td>
                <td>${typeIcon} <span class="${typeClass}">${typeLabel}</span></td>
                <td>${walletName}</td>
                <td>${t.category || t.description || '-'}</td>
                <td class="text-end ${typeClass}"><strong>${amount.toFixed(2)} ${currency}</strong></td>
            </tr>
        `;
    }).join('');
}

async function updateTotalBalance() {
    if (wallets.length === 0) {
        document.getElementById('totalBalance').innerHTML = `
            0.00 ₽
            <div class="fs-6 text-muted mt-2">Create a wallet to get started</div>
        `;
        return;
    }

    try {
        // Fetch total balance in RUB from server (with currency conversion)
        const response = await fetch(`${API_BASE}/balance`, {
            headers: { 'Authorization': `Bearer ${encodeURIComponent(currentUser)}` }
        });

        if (response.ok) {
            const data = await response.json();
            const total = typeof data.total_balance === 'number' ? data.total_balance : (parseFloat(data.total_balance) || 0);
            document.getElementById('totalBalance').innerHTML = `
                ${total.toFixed(2)} ₽
                <div class="fs-6 text-muted mt-2">Total balance across all wallets</div>
            `;
        } else {
            // If request fails, show 0
            document.getElementById('totalBalance').innerHTML = `
                0.00 ₽
                <div class="fs-6 text-muted mt-2">Failed to load balance</div>
            `;
        }
    } catch (e) {
        console.error('Failed to load total balance:', e);
        // On error, show 0
        document.getElementById('totalBalance').innerHTML = `
            0.00 ₽
            <div class="fs-6 text-muted mt-2">Connection error</div>
        `;
    }
}

function updateWalletSelects() {
    const selects = [
        'incomeWallet', 'expenseWallet', 'transferFrom', 'transferTo'
    ];

    const currencySymbols = {
        'rub': '₽',
        'usd': '$',
        'eur': '€'
    };

    selects.forEach(id => {
        const select = document.getElementById(id);
        if (!select) return;
        
        if (wallets.length === 0) {
            select.innerHTML = '<option value="">Create a wallet first</option>';
        } else {
            select.innerHTML = wallets.map(w => {
                // Ensure balance is a number
                const balance = typeof w.balance === 'number' ? w.balance : (parseFloat(w.balance) || 0);
                const currency = String(w.currency || '').toLowerCase();
                const symbol = currencySymbols[currency] || currency.toUpperCase();
                return `<option value="${w.id}">${w.name} - ${balance.toFixed(2)} ${symbol}</option>`;
            }).join('');
        }
    });
}

async function addWallet() {
    const name = document.getElementById('walletName').value.trim();
    const currency = document.getElementById('walletCurrency').value;
    const balance = parseFloat(document.getElementById('walletBalance').value);

    if (!name) {
        showError('Enter wallet name');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/wallets`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${encodeURIComponent(currentUser)}`
            },
            body: JSON.stringify({ name, currency, initial_balance: balance })
        });

        if (response.ok) {
            showSuccess('Wallet created!');
            closeModal('addWalletModal');
            document.getElementById('walletName').value = '';
            document.getElementById('walletBalance').value = '0';
            await loadAllData();
        } else {
            const error = await response.json();
            showError(error.detail || 'Failed to create wallet');
        }
    } catch (e) {
        showError('Connection error');
    }
}

async function addIncome() {
    if (wallets.length === 0) {
        showError('Create a wallet first');
        return;
    }

    const wallet_id = parseInt(document.getElementById('incomeWallet').value);
    const amount = parseFloat(document.getElementById('incomeAmount').value);
    const description = document.getElementById('incomeDescription').value.trim();

    if (!amount || amount <= 0) {
        showError('Enter a valid amount');
        return;
    }

    const wallet = wallets.find(w => w.id === wallet_id);
    if (!wallet) {
        showError('Wallet not found');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/operations/income`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${encodeURIComponent(currentUser)}`
            },
            body: JSON.stringify({ 
                wallet_name: wallet.name, 
                amount, 
                description,
                category: description || 'income'
            })
        });

        if (response.ok) {
            showSuccess('Income added!');
            closeModal('addIncomeModal');
            document.getElementById('incomeAmount').value = '';
            document.getElementById('incomeDescription').value = '';
            await loadAllData();
        } else {
            const error = await response.json();
            showError(error.detail || 'Failed to add income');
        }
    } catch (e) {
        showError('Connection error');
    }
}

async function addExpense() {
    if (wallets.length === 0) {
        showError('Create a wallet first');
        return;
    }

    const wallet_id = parseInt(document.getElementById('expenseWallet').value);
    const amount = parseFloat(document.getElementById('expenseAmount').value);
    const category = document.getElementById('expenseCategory').value.trim();
    const description = document.getElementById('expenseDescription').value.trim();

    if (!amount || amount <= 0) {
        showError('Enter a valid amount');
        return;
    }

    if (!category) {
        showError('Enter a category');
        return;
    }

    const wallet = wallets.find(w => w.id === wallet_id);
    if (!wallet) {
        showError('Wallet not found');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/operations/expense`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${encodeURIComponent(currentUser)}`
            },
            body: JSON.stringify({ 
                wallet_name: wallet.name, 
                amount, 
                category, 
                description 
            })
        });

        if (response.ok) {
            showSuccess('Expense added!');
            closeModal('addExpenseModal');
            document.getElementById('expenseAmount').value = '';
            document.getElementById('expenseCategory').value = '';
            document.getElementById('expenseDescription').value = '';
            await loadAllData();
        } else {
            const error = await response.json();
            showError(error.detail || 'Failed to add expense');
        }
    } catch (e) {
        showError('Connection error');
    }
}

async function transfer() {
    if (wallets.length < 2) {
        showError('You need at least 2 wallets to transfer');
        return;
    }

    const from_wallet_id = parseInt(document.getElementById('transferFrom').value);
    const to_wallet_id = parseInt(document.getElementById('transferTo').value);
    const amount = parseFloat(document.getElementById('transferAmount').value);

    if (from_wallet_id === to_wallet_id) {
        showError('You cannot transfer to the same wallet');
        return;
    }

    if (!amount || amount <= 0) {
        showError('Enter a valid amount');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/operations/transfer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${encodeURIComponent(currentUser)}`
            },
            body: JSON.stringify({ from_wallet_id, to_wallet_id, amount })
        });

        if (response.ok) {
            showSuccess('Transfer completed!');
            closeModal('transferModal');
            document.getElementById('transferAmount').value = '';
            await loadAllData();
        } else {
            const error = await response.json();
            showError(error.detail || 'Transfer failed');
        }
    } catch (e) {
        showError('Connection error');
    }
}

function initReportDates() {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    
    document.getElementById('reportDateFrom').valueAsDate = firstDay;
    document.getElementById('reportDateTo').valueAsDate = tomorrow;
}

async function loadReport() {
    const dateFrom = document.getElementById('reportDateFrom').value;
    const dateTo = document.getElementById('reportDateTo').value;

    if (!dateFrom || !dateTo) {
        showError('Select a date range');
        return;
    }

    if (dateFrom > dateTo) {
        showError('Start date cannot be later than end date');
        return;
    }

    try {
        const params = new URLSearchParams({
            date_from: `${dateFrom}T00:00:00`,
            date_to: `${dateTo}T23:59:59`
        });

        const response = await fetch(`${API_BASE}/operations?${params}`, {
            headers: { 'Authorization': `Bearer ${encodeURIComponent(currentUser)}` }
        });

        if (response.ok) {
            const rawReportOperations = await response.json();
            // Normalize backend data: currency -> lowercase, amount -> number
            const reportOperations = rawReportOperations.map(op => {
                // Convert amount to a number (handle strings, Decimal-like values, etc.)
                let amount = 0;
                if (typeof op.amount === 'number') {
                    amount = op.amount;
                } else if (typeof op.amount === 'string') {
                    amount = parseFloat(op.amount) || 0;
                } else if (op.amount != null) {
                    amount = Number(op.amount) || 0;
                }
                
                return {
                    ...op,
                    currency: String(op.currency || '').toLowerCase(),
                    amount: amount
                };
            });
            const tbody = document.getElementById('reportTable');
            
            if (reportOperations.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No operations for the selected period</td></tr>';
            } else {
                tbody.innerHTML = reportOperations.reverse().map(t => {
                    const wallet = wallets.find(w => w.id === t.wallet_id);
                    const walletName = wallet ? wallet.name : 'Unknown';
                    let typeClass, typeIcon, typeLabel;
                    if (t.type === 'income') {
                        typeClass = 'text-success';
                        typeIcon = '➕';
                        typeLabel = 'Income';
                    } else if (t.type === 'expense') {
                        typeClass = 'text-danger';
                        typeIcon = '➖';
                        typeLabel = 'Expense';
                    } else if (t.type === 'transfer') {
                        typeClass = 'text-info';
                        typeIcon = '🔄';
                        typeLabel = 'Transfer';
                    } else {
                        typeClass = 'text-secondary';
                        typeIcon = '❓';
                        typeLabel = 'Unknown';
                    }
                    const date = new Date(t.created_at).toLocaleString('en-US', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                    
                    const currencySymbols = {
                        'rub': '₽',
                        'usd': '$',
                        'eur': '€'
                    };
                    // Ensure amount is a number
                    const amount = typeof t.amount === 'number' ? t.amount : (parseFloat(t.amount) || 0);
                    const currency = String(t.currency || '').toLowerCase();
                    const symbol = currencySymbols[currency] || currency.toUpperCase();
                    
                    return `
                        <tr>
                            <td>${date}</td>
                            <td>${typeIcon} <span class="${typeClass}">${typeLabel}</span></td>
                            <td>${walletName}</td>
                            <td>${t.category || t.description || '-'}</td>
                            <td class="text-end ${typeClass}"><strong>${amount.toFixed(2)} ${symbol}</strong></td>
                        </tr>
                    `;
                }).join('');
            }

            document.getElementById('reportContent').style.display = 'block';
            showSuccess('Report generated!');
        } else {
            const error = await response.json();
            showError(error.detail || 'Failed to load report');
        }
    } catch (e) {
        console.error('Failed to load report:', e);
        showError('Failed to connect to the server');
    }
}