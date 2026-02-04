# VELO Mockups

Интерактивные прототипы платформы VELO для согласования UI/UX перед разработкой.

## Текущая структура (Вариант 1 — Простой)

```
velo-mockups/
├── index.html              ← Главная страница выбора роли
├── css/
│   ├── variables.css       ← Дизайн-токены
│   ├── components.css      ← Общие компоненты
│   ├── shell.css           ← Device preview оболочка
│   └── navigation-map.css  ← Стили карты навигации
├── js/
│   ├── shell.js            ← Логика превью устройств
│   └── navigation.js       ← Функции навигации
├── user.html               ← Приложение участника
├── master.html             ← Кабинет мастера
└── admin.html              ← Админ-панель
```

## Горячие клавиши

| Клавиша | Действие |
|---------|----------|
| `1` | iPhone SE |
| `2` | iPhone 14 Pro |
| `3` | Desktop (admin) |
| `M` | Открыть карту навигации |
| `Esc` | Закрыть карту навигации |

---

## Вариант 3 — Полноценный фронтенд (будущая реализация)

После согласования мокапов и содержания MVP, прототипы будут преобразованы в production-ready фронтенд на базе **Web Components** или **Vue/React**.

### Архитектура

```
velo-frontend/
├── src/
│   ├── components/           ← Переиспользуемые UI-компоненты
│   │   ├── VeloButton.vue
│   │   ├── VeloCard.vue
│   │   ├── VeloInput.vue
│   │   ├── VeloAvatar.vue
│   │   ├── VeloTabBar.vue
│   │   ├── VeloHeader.vue
│   │   ├── VeloPopup.vue
│   │   ├── VeloToast.vue
│   │   └── ...
│   │
│   ├── layouts/              ← Макеты страниц
│   │   ├── MobileLayout.vue  ← Обёртка для mobile apps
│   │   └── AdminLayout.vue   ← Обёртка для admin panel
│   │
│   ├── apps/                 ← Три приложения
│   │   ├── user/             ← Приложение участника
│   │   │   ├── views/
│   │   │   │   ├── Dashboard.vue
│   │   │   │   ├── Schedule.vue
│   │   │   │   ├── Library.vue
│   │   │   │   ├── Profile.vue
│   │   │   │   └── ...
│   │   │   ├── store/        ← Vuex/Pinia состояние
│   │   │   └── router.js
│   │   │
│   │   ├── master/           ← Кабинет мастера
│   │   │   ├── views/
│   │   │   ├── store/
│   │   │   └── router.js
│   │   │
│   │   └── admin/            ← Админ-панель
│   │       ├── views/
│   │       ├── store/
│   │       └── router.js
│   │
│   ├── api/                  ← Интеграция с бэкендом
│   │   ├── client.js         ← Axios/Fetch обёртка
│   │   ├── auth.js           ← Авторизация
│   │   ├── practices.js      ← API практик
│   │   ├── users.js          ← API пользователей
│   │   └── ...
│   │
│   ├── styles/               ← Глобальные стили
│   │   ├── variables.scss    ← Дизайн-токены (из мокапов)
│   │   ├── mixins.scss
│   │   └── global.scss
│   │
│   └── utils/                ← Утилиты
│       ├── formatters.js     ← Форматирование дат, чисел
│       ├── validators.js     ← Валидация форм
│       └── constants.js
│
├── public/
│   └── assets/               ← Статика (иконки, шрифты)
│
├── package.json
├── vite.config.js            ← Сборщик
└── README.md
```

### Технологический стек (рекомендация)

| Слой | Технология | Причина |
|------|------------|---------|
| **Framework** | Vue 3 + Composition API | Простота, хорошая документация, подходит для команды |
| **State** | Pinia | Современный стейт-менеджер для Vue 3 |
| **Router** | Vue Router 4 | Стандарт для Vue SPA |
| **HTTP** | Axios | Удобная работа с API, интерсепторы |
| **Styling** | SCSS + CSS Variables | Дизайн-токены уже есть в мокапах |
| **Build** | Vite | Быстрая сборка, HMR |
| **Mobile** | Capacitor (опционально) | Обёртка для iOS/Android из веб-кода |

### Этапы миграции

#### Этап 1: Инфраструктура
- [ ] Инициализация проекта (Vite + Vue 3)
- [ ] Настройка линтеров (ESLint, Prettier)
- [ ] Перенос дизайн-токенов из `variables.css` → `variables.scss`
- [ ] Настройка роутинга для трёх приложений

#### Этап 2: UI-компоненты
- [ ] Создание базовых компонентов (Button, Card, Input, Avatar)
- [ ] Создание составных компонентов (Header, TabBar, Popup)
- [ ] Storybook для документации компонентов (опционально)

#### Этап 3: Экраны User App
- [ ] Dashboard (ближайшая практика, статистика)
- [ ] Schedule (расписание, календарь)
- [ ] Library (медитации, курсы)
- [ ] Profile (настройки, подписка)
- [ ] Practice flow (check-in, live, feedback)

#### Этап 4: Экраны Master App
- [ ] Dashboard (сегодняшние практики)
- [ ] Calendar (расписание мастера)
- [ ] Analytics (статистика, отзывы)
- [ ] Profile (настройки, выплаты)

#### Этап 5: Admin Panel
- [ ] Dashboard (метрики платформы)
- [ ] Users management
- [ ] Masters management
- [ ] Practices & content
- [ ] Settings

#### Этап 6: Интеграция с бэкендом
- [ ] Настройка API клиента
- [ ] Авторизация (JWT)
- [ ] Подключение реальных данных
- [ ] WebSocket для real-time (уведомления, чат)

### API контракт (примерный)

```
# Auth
POST   /api/auth/login
POST   /api/auth/register
POST   /api/auth/refresh
POST   /api/auth/logout

# User
GET    /api/user/profile
PATCH  /api/user/profile
GET    /api/user/subscription
GET    /api/user/statistics

# Practices
GET    /api/practices                    # список практик
GET    /api/practices/:id                # детали практики
GET    /api/practices/upcoming           # ближайшие
POST   /api/practices/:id/book           # записаться
POST   /api/practices/:id/checkin        # отметить состояние
POST   /api/practices/:id/feedback       # оставить отзыв

# Master (для мастеров)
GET    /api/master/practices             # мои практики
POST   /api/master/practices             # создать практику
GET    /api/master/analytics             # аналитика
GET    /api/master/earnings              # заработок

# Admin
GET    /api/admin/dashboard              # метрики
GET    /api/admin/users                  # пользователи
GET    /api/admin/masters                # мастера
...
```

---

## Контакты

Вопросы по мокапам и разработке → [добавить контакт]

---

*Версия мокапов: 1.0 · livemockup-studio*
