// ==========================================
// 1. БАЗА ДАННЫХ КВЕСТОВ И ЛОКАЛЬНОЕ ХРАНИЛИЩЕ
// ==========================================
const COOLDOWN_CHALLENGES = [
    { title: "Режим Поэта", desc: "Продержись 3 часа, отвечая людям в мессенджерах или лично исключительно рифмованными строчками.", difficulty: "Сложно", reward: 150 },
    { title: "Охота на Желтый", desc: "Найди на улице, сфоткай и пришли в чат 5 абсолютно разных желтых автомобилей.", difficulty: "Легко", reward: 50 },
    { title: "Шеф-Повар из Будущего", desc: "Приготовь съедобное блюдо, используя только микроволновку, сыр и чипсы. Сними обзор.", difficulty: "Средне", reward: 100 },
    { title: "Лев Толстой", desc: "Напиши старому знакомому, с которым не общался больше года, сообщение длиной не менее 50 слов в викторианском стиле.", difficulty: "Средне", reward: 100 },
    { title: "Каменный Человек", desc: "Просиди 15 минут в людном месте, абсолютно не меняя выражения лица и позы (как статуя).", difficulty: "Сложно", reward: 200 }
];

function getRandomChallenge() {
    const idx = Math.floor(Math.random() * COOLDOWN_CHALLENGES.length);
    return { ...COOLDOWN_CHALLENGES[idx], id: 'q_' + Date.now() };
}

function getArchive() { return JSON.parse(localStorage.getItem('cz_archive')) || []; }
function saveArchive(data) { localStorage.setItem('cz_archive', JSON.stringify(data)); }
function getActiveQuest() { return JSON.parse(localStorage.getItem('cz_active')); }
function saveActiveQuest(quest) { localStorage.setItem('cz_active', JSON.stringify(quest)); }

// ==========================================
// 2. УВЕДОМЛЕНИЯ И КАЛЕНДАРЬ АКТИВНОСТИ
// ==========================================
function initNotification() {
    if (Notification.permission === 'default') Notification.requestPermission();
}

function triggerNotification(title, body) {
    if (Notification.permission === 'granted') {
        new Notification(title, { body });
    }
}

function renderYearHeatmap(containerId, archive) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';

    const today = new Date();
    const yearAgo = new Date();
    yearAgo.setFullYear(today.getFullYear() - 1);

    const dateCounts = {};
    archive.forEach(item => {
        if (item.status === 'success' && item.date) {
            dateCounts[item.date] = (dateCounts[item.date] || 0) + 1;
        }
    });

    let current = new Date(yearAgo);
    while (current <= today) {
        const dateStr = current.toISOString().split('T')[0];
        const dayCell = document.createElement('div');
        dayCell.className = 'heatmap-day';
        dayCell.title = `${dateStr}: Выполнено ${dateCounts[dateStr] || 0} квестов`;

        if (dateCounts[dateStr] > 0) {
            const level = Math.min(dateCounts[dateStr], 4);
            dayCell.setAttribute('data-level', level);
        }

        container.appendChild(dayCell);
        current.setDate(current.getDate() + 1);
    }
}

// ==========================================
// 3. ГЛАВНАЯ ЛОГИКА И ИНТЕРФЕЙС
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initNotification();
    updateUI();

    // Кнопка генерации
    const genBtn = document.getElementById('btn-generate');
    if (genBtn) {
        genBtn.addEventListener('click', () => {
            if (getActiveQuest()) {
                alert('У тебя уже есть активный квест! Выполни его или слей.');
                return;
            }
            const quest = getRandomChallenge();
            saveActiveQuest(quest);
            triggerNotification('Новый вызов! ⚡', `Задание: ${quest.title}`);
            updateUI();
        });
    }

    // Кнопки успеха/провала
    const successBtn = document.getElementById('btn-challenge-success');
    if (successBtn) successBtn.addEventListener('click', () => completeQuest('success'));

    const failBtn = document.getElementById('btn-challenge-fail');
    if (failBtn) failBtn.addEventListener('click', () => completeQuest('fail'));

    // Импорт/Экспорт
    const expBtn = document.getElementById('btn-export');
    if (expBtn) expBtn.addEventListener('click', exportSave);

    const impTrigger = document.getElementById('btn-import-trigger');
    if (impTrigger) impTrigger.addEventListener('click', () => document.getElementById('file-import').click());

    const fileImp = document.getElementById('file-import');
    if (fileImp) fileImp.addEventListener('change', importSave);
});

function initNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            document.querySelectorAll('.app-section').forEach(s => s.classList.add('hidden'));

            link.classList.add('active');
            const targetId = link.getAttribute('data-target');
            const targetSec = document.getElementById(targetId);
            if (targetSec) targetSec.classList.remove('hidden');
        });
    });
}

function completeQuest(status) {
    const quest = getActiveQuest();
    if (!quest) return;

    const archive = getArchive();
    archive.push({
        ...quest,
        status: status,
        date: new Date().toISOString().split('T')[0]
    });

    saveArchive(archive);
    saveActiveQuest(null);
    
    if (status === 'success') {
        triggerNotification('Красава! 🎉', `+${quest.reward} XP в твою копилку.`);
    }
    
    updateUI();
}

function updateUI() {
    const quest = getActiveQuest();
    const box = document.getElementById('active-challenge-box');

    if (quest && box) {
        box.classList.remove('hidden');
        document.getElementById('challenge-title').textContent = quest.title;
        document.getElementById('challenge-desc').textContent = quest.desc;
        document.getElementById('challenge-difficulty').textContent = quest.difficulty.toUpperCase();
        document.getElementById('challenge-reward').textContent = quest.reward;
    } else if (box) {
        box.classList.add('hidden');
    }

    renderArchive();
    renderYearHeatmap('heatmap-grid', getArchive());
}

function renderArchive() {
    const container = document.getElementById('archive-container');
    if (!container) return;
    container.innerHTML = '';
    const archive = getArchive();

    const reversed = [...archive].reverse();
    reversed.forEach(item => {
        const div = document.createElement('div');
        div.className = `archive-card-item ${item.status === 'success' ? 'status-done' : 'status-fail'}`;
        div.innerHTML = `
            <h4>${item.title} (${item.date})</h4>
            <p style="font-size:0.85rem; margin-top:5px;">${item.status === 'success' ? '✅ Пройдено' : '💀 Провалено'} | Очки: ${item.reward} XP</p>
        `;
        container.appendChild(div);
    });
}

function exportSave() {
    const data = { archive: getArchive(), active: getActiveQuest() };
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data));
    const dl = document.createElement('a');
    dl.setAttribute("href", dataStr);
    dl.setAttribute("download", "tracker_backup.json");
    dl.click();
}

function importSave(e) {
    const file = e.target.files;
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
        try {
            const parsed = JSON.parse(event.target.result);
            saveArchive(parsed.archive || []);
            saveActiveQuest(parsed.active || null);
            updateUI();
            alert('Сейв успешно загружен!');
        } catch(err) {
            alert('Ошибка чтения файла бэкапа');
        }
    };
    reader.readAsText(file);
}
