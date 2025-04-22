# -*- coding: utf-8 -*-
import logging
import os
import sys

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, BotCommand
from aiogram.utils.markdown import text, bold, hlink, escape_md # Используем HTML, но escape_md может пригодиться

# --- Константы и Конфигурация ---

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not API_TOKEN:
    logging.error("CRITICAL: TELEGRAM_BOT_TOKEN environment variable not set!")
    sys.exit("Environment variable TELEGRAM_BOT_TOKEN is required.")

# --- Ссылки (ВАЖНО: Проверь!) ---
REGISTRATION_URL = "https://revvy.prmonline.ru/"
PARTNER_CABINET_URL = "https://revvy.prmonline.ru/"
# Ссылка на Партнерское Соглашение из PDF (стр. 6)
PARTNER_AGREEMENT_URL = "https://docs.google.com/document/d/1GF8bWcroSKTa9CgHIpLPn-f-yDoKHytT/edit#heading=h.30j0zll"
# Инструкция по созданию ЛК из Teamly (если нужна отдельно)
LK_INSTRUCTION_URL = "https://revvy-space.teamly.ru/space/ce9ca057-8849-476c-a3fb-8c0935f1746c/article/d29f7b00-2a54-41ec-9b89-4ef277ebb9d3"
HEAD_CONTACT_TG_LINK = "https://t.me/tsycunoff" # Контакт руководителя TG
GENERAL_SUPPORT_EMAIL = "v.tsykunov@revvy.ru" # Общая поддержка Email
# --- Конец секции ссылок ---


# --- Тексты и Данные из PDF (RU) ---
TEXTS_RU = {
    "welcome": "🚀 <b>Добро пожаловать в онбординг партнёрской программы Revvy!</b>\n\nЗарабатывайте, Помогая Бизнесу Расти!\n\nРекомендуйте. Подключайте. Зарабатывайте вместе с лидером рынка автоматизации работы с отзывами!\n\nДавайте начнём! Пожалуйста, выберите ваш формат:",
    "choose_role": "👇 <b>1. Как это работает? Выберите свой формат:</b>",
    "role_referral_btn": "🤝 Реферал (Рекомендую)",
    "role_integrator_btn": "⚙️ Интегратор (Продаю и Внедряю)",

    # --- Общие разделы ---
    "why_revvy_title": "✨ <b>Почему партнеры выбирают Revvy?</b>",
    "why_revvy_text": text(
        "✅ <b>Доход Lifetime:</b> Получайте % со всех платежей ваших клиентов, пока они пользуются Revvy. Привели качественного клиента — получаете доход годами!",
        "📈 <b>Высокие Ставки:</b> Зарабатывайте до <b>40%</b> пожизненной комиссии — одна из самых щедрых программ на рынке!",
        "✌️ <b>Два Пути к Успеху:</b> Выбирайте модель (Реферал или Интегратор), которая вам удобнее.",
        "💎 <b>Прозрачный Рост:</b> Понятная система уровней — чем больше ваш вклад, тем выше ваш % и статус.",
        "🎁 <b>Бонусы и Геймификация:</b> Зарабатывайте баллы за активность, обменивайте их на классный мерч и подарки. Участвуйте в акциях и получайте денежные бонусы!",
        "🤝 <b>Поддержка и Ресурсы:</b> Мы предоставляем все необходимые материалы, обучение и персональную поддержку для вашего успеха.",
        "💯 <b>Честные Правила:</b> Понятная система атрибуции сделок и прозрачные условия сотрудничества.",
        sep="\n\n"
    ),
    "points_title": "💰 <b>5. Больше Чем Деньги: Баллы за Активность!</b>",
    "points_text": text(
        "Зарабатывайте баллы за ключевые действия и обменивайте их на крутые призы!",
        "\n<b>Начисление баллов:</b>",
        "  • Успешная рекомендация (Реф. модель): <b>+2</b>",
        "  • Самостоятельное подключение (Инт. модель): <b>+5</b>",
        "  • Продажа подписки на 3 мес. (квартал): <b>+10</b>",
        "  • Продажа подписки на 6 мес. (полгода): <b>+15</b>",
        "  • Участие и победы в акциях: <b>+Баллы</b>",
        "\n⚠️ <b>Важно:</b> Баллы действительны <b>12 месяцев</b> с момента начисления. Не копите — тратьте!",
        f"\n👀 Актуальный баланс баллов смотрите в {hlink('Личном кабинете', PARTNER_CABINET_URL)}.",
        sep="\n"
    ),
     "prizes_title": "🎁 <b>6. Каталог Призов: Ваш Мерч и Подарки</b>",
     "prizes_text": text(
         "Обменяйте накопленные баллы на фирменный мерч Revvy и другие ценные призы!",
         "\n<b>Примеры призов (стоимость в баллах):</b>",
         "  <code> 25</code> - Набор фирменных стикеров Revvy",
         "  <code> 75</code> - Ручка + блокнот",
         "  <code>150</code> - Футболка с логотипом",
         "  <code>250</code> - Термос / термокружка",
         "  <code>350</code> - Power Bank",
         "  <code>400</code> - Худи с логотипом",
         "  <code>600</code> - Рюкзак Revvy",
         "  <code>700</code> - Сертификат на 3000 ₽ (Ozon и т.п.)",
         "  <code>1100</code> - Сертификат на 5000 ₽",
         f"\n👀 Актуальный каталог и ваш баланс — всегда доступны в {hlink('Личном кабинете партнера', PARTNER_CABINET_URL)}!",
         sep="\n"
     ),
    "bonuses_title": "🚀 <b>7. Ускоряем Ваш Доход: Акции и Бонусы</b>",
    "bonuses_text": text(
        "Мы регулярно запускаем акции, чтобы вы могли заработать еще больше!",
        "\n<b>Постоянные бонусы:</b>",
        "  •⚡️ <b>Турбо-старт (Для Новичков):</b> Сделайте первые 3 продажи/рекомендации за <b>14 дней</b> и получите <b>+5%</b> к выплатам за них!",
        "  •⬆️ <b>Подними уровень!:</b> Перешли на уровень выше? Получите <b>5 000 ₽</b> бонусом к выплате!",
        "  •🏆 <b>Лучший партнёр месяца:</b> Покажите лучший результат (мин. 10 сделок) и получите <b>15 000 ₽ + 50 баллов</b> на мерч! (Критерии публикуются заранее).",
        "\n<b>Периодические акции:</b>",
        "  • \"Реванш!\", \"Челленджи\", Сезонные предложения — следите за новостями в ЛК!",
        "\n⚠️ <b>Важно:</b> Если не указано иное, бонусы от разных акций <b>суммируются!</b>",
        sep="\n"
    ),
    "rules_title": "⚖️ <b>8. Честная Игра: Как Мы Закрепляем Сделки</b>",
    "rules_text": text(
        "Мы ценим ваш вклад и стремимся к максимальной прозрачности:",
        "\n• <b>Приоритет Партнера:</b> Если вы первым инициировали работу с клиентом (передали лид по ссылке/коду или заполнили Анкету на передачу), сделка закрепляется за вами.",
        "• <b>Правило \"Первого Счета\":</b> В редких спорных ситуациях, когда и вы, и наш менеджер выставили счет, приоритет отдается тому, кто сделал это <b>раньше</b>.",
        "• <b>Проверка на Дубли:</b> Мы проверяем, не является ли переданный вами клиент уже нашим действующим клиентом или не находится ли он в активной работе у нашего отдела продаж. В таких случаях клиент не может быть закреплен за партнером.",
        sep="\n\n"
    ),
    "how_to_start_title": "🏁 <b>9. Как Стать Партнёром Revvy? (Это Просто!)</b>",
    "how_to_start_text": lambda reg_link=REGISTRATION_URL, agr_link=PARTNER_AGREEMENT_URL, cabinet_link=PARTNER_CABINET_URL: text(
        f"1. <b>Зарегистрируйтесь:</b> Перейдите по ссылке [{hlink('Регистрация', reg_link)}] и заполните форму.",
        f"2. <b>Ознакомьтесь с Соглашением:</b> Прочитайте и примите условия нашего {hlink('Партнерского Соглашения', agr_link)}.",
        f"3. <b>Получите Доступ:</b> Вам откроется {hlink('Личный кабинет', cabinet_link)} с уникальными ссылками, промокодами, обучающими материалами и статистикой.",
        "4. <b>Начинайте Зарабатывать:</b> Рекомендуйте Revvy или продавайте его сами, отслеживайте результаты и получайте вознаграждение!",
        sep="\n"
    ),
    "important_details_title": "❗️ <b>10. Важные Детали</b>",
    "important_details_text": lambda agr_link=PARTNER_AGREEMENT_URL: text(
        f"• <b>Партнерское Соглашение:</b> Все условия программы подробно описаны в {hlink('официальном документе', agr_link)}, который доступен в ЛК. Принимая участие, вы соглашаетесь с ним.",
        "• <b>Оставайтесь Активными:</b> Чтобы ваш статус партнера был активным и вы продолжали получать LTV-выплаты, необходимо совершать <b>хотя бы 1 успешную рекомендацию или подключение каждые 6 месяцев</b>.",
        f"• <b>Возвраты:</b> Если клиент получает возврат средств за Revvy, соответствующая партнерская комиссия может быть аннулирована (согласно {hlink('Соглашению', agr_link)}).",
        sep="\n\n"
    ),
    "contacts_title": "🆘 <b>11. Нужна Помощь? Мы Рядом!</b>",
    "contacts_text": lambda head_link=HEAD_CONTACT_TG_LINK, support_email=GENERAL_SUPPORT_EMAIL, cabinet_link=PARTNER_CABINET_URL: text(
        f"• <b>Руководитель Партнерского Департамента:</b> {hlink('@tsycunoff', head_link)}",
        f"• <b>Общая Поддержка:</b> Пишите нам на {support_email}",
        f"• <b>Личный Кабинет:</b> Вся статистика, материалы и новости здесь: {hlink(cabinet_link, cabinet_link)}",
        "\nУ каждого активного партнера также есть персональный менеджер!",
        sep="\n"
    ),
    "final_cta_title": "🚀 <b>Готовы Увеличить Свой Доход с Revvy?</b>",


    # --- Тексты для Реферальной модели ---
    "referral_menu_title": "🤝 <b>Реферальная Модель: Меню</b>",
    "referral_details_title": "ℹ️ <b>Реферальная Модель: Детали</b>",
    "referral_details_text": text(
        "<b>Ваша Роль:</b> Вы — источник доверия. Рекомендуете Revvy своей аудитории, используя уникальную ссылку или промокод.",
        "<b>Основная Задача:</b> Передача качественных лидов в наш отдел продаж.",
        "<b>Ключевое Преимущество:</b> Легкий старт, пассивный доход за рекомендации.",
        "\n<b>Как это работает?</b> Вы делитесь своей уникальной ссылкой/кодом. Клиент регистрируется и оплачивает Revvy. Вы начинаете получать % со <b>всех</b> его платежей (lifetime), пока ваш партнерский статус активен.",
        sep="\n\n"
    ),
    "referral_levels_title": "💰 <b>Реферал: Уровни и Выплаты</b>",
    "referral_levels_text": text(
        "Ваш % вознаграждения зависит от количества <b>успешных рекомендаций</b> (клиент оплатил) за последние <b>30 дней</b>.",
        "\n•   <b>Новичок</b> (до 3 рек.): <b>12%</b> lifetime",
        "•   <b>Партнёр</b> (от 4 до 34 рек.): <b>15%</b> lifetime",
        "•   <b>Профи</b> (от 35 рек.): <b>20%</b> lifetime",
        "•   👑 <b>Ключевой партнёр</b> (Стабильно 20+/мес, среднее за 3 мес.): <b>25%</b> lifetime + Индивидуальные бонусы",
        "\n<i>Уровень пересматривается каждый месяц.</i>",
        sep="\n"
    ),

    # --- Тексты для Интеграционной модели ---
    "integrator_menu_title": "⚙️ <b>Интеграционная Модель: Меню</b>",
    "integrator_details_title": "ℹ️ <b>Интеграционная Модель: Детали</b>",
    "integrator_details_text": text(
        "<b>Ваша Роль:</b> Вы — эксперт и полноценный канал продаж. Самостоятельно продаете, подключаете и сопровождаете клиентов.",
        "<b>Основная Задача:</b> Полный цикл продажи и внедрения Revvy для клиента.",
        "<b>Ключевое Преимущество:</b> Максимальный % комиссии (до 40%), больше контроля.",
        "\n<b>Как это работает?</b> Вы находите клиента, проводите презентацию, продаете, помогаете с настройкой и передаете нам через специальную форму. Клиент совершает первую оплату. Вы получаете максимальный % со <b>всех</b> его платежей (lifetime), пока ваш партнерский статус активен.",
        sep="\n\n"
    ),
    "integrator_levels_title": "💰 <b>Интегратор: Уровни и Выплаты</b>",
    "integrator_levels_text": text(
        "Ваш % вознаграждения зависит от вашей <b>Активности</b> (количество подключенных и активных клиентов) за последние <b>30 дней</b>.",
        "\n•   <b>Новичок</b> (до 3 Подключений): <b>25%</b> lifetime",
        "•   <b>Партнёр</b> (4-15 Активных клиентов*): <b>30%</b> lifetime",
        "•   <b>Профи</b> (от 16 Активных клиентов*): <b>35%</b> lifetime",
        "•   👑 <b>Ключевой партнёр</b> (Стабильно 10+ Подключений/мес, среднее за 3 мес.): <b>40%</b> lifetime + Совместные активности**",
        "\n<i>*Активный клиент: Подключенный вами клиент, оплачивающий сервис в течение последних 90 дней.</i>",
        "<i>**Совместные активности: Приоритет в бета-тестах, совместные вебинары, кейс-стади и др.</i>",
        "\n💼 <b>Особое Преимущество: Работа с Сетями!</b> Привели сетевого клиента на 'пилот'? У вас есть <b>эксклюзивное окно в 2 месяца</b>, чтобы самостоятельно допродать Revvy остальным филиалам этой сети и получить комиссию за всю сеть!",
        sep="\n"
     ),

    # --- Общие тексты ---
    "main_menu_title": "📖 <b>Главное Меню</b>",
    "faq_title": "🤔 <b>Часто задаваемые вопросы:</b>",
    "faq_q_levels": "Как считаются/меняются уровни?",
    "faq_a_levels": "Уровни зависят от ваших результатов за <b>последние 30 дней</b> (рекомендации для Рефералов, подключения/активные клиенты для Интеграторов). Уровень пересматривается <b>каждый месяц</b>. Если вы достигли планки нового уровня - сразу получаете повышенный %! Уровень понижается только если вы не выполняете минимальные условия своего уровня <b>два месяца подряд</b> (анализируются последние 60 дней).",
    "faq_q_payout": "Когда я получу выплату?",
    "faq_a_payout": "Выплаты партнёрского вознаграждения производятся <b>ежемесячно</b>, обычно до 15 числа месяца, следующего за отчётным. Минимальная сумма для выплаты может быть указана в Партнерском Соглашении. Убедитесь, что вы предоставили все необходимые реквизиты в ЛК.",
    "faq_q_client_referral": "Как передать клиента (реферал)?",
    "faq_a_client_referral": f"Очень просто! В вашем {hlink('Личном Кабинете', PARTNER_CABINET_URL)} вы найдете свою <b>уникальную реферальную ссылку</b> или промокод. Отправьте их потенциальному клиенту. Когда он перейдет по ссылке и зарегистрируется/оплатит, он автоматически закрепится за вами.",
    "faq_q_client_integrator": "Как передать клиента (интегратор)?",
    "faq_a_client_integrator": f"Как интегратор, вы сами регистрируете клиента (после продажи и настройки) через специальную форму в {hlink('Личном Кабинете', PARTNER_CABINET_URL)}. Следуйте инструкциям из обучающих материалов или обратитесь к вашему менеджеру/руководителю.",
    "faq_q_points_prizes": "Где посмотреть баллы и призы?",
    "faq_a_points_prizes": f"Вся информация о ваших накопленных баллах, истории начислений и актуальный каталог призов находятся в вашем {hlink('Личном Кабинете Revvy', PARTNER_CABINET_URL)}. Обычно для этого есть специальный раздел.",
    "faq_q_agreement": "Где найти Партнерское Соглашение?",
    "faq_a_agreement": f"Полное Партнерское Соглашение доступно в вашем ЛК, а также по этой ссылке: {hlink('Документ', PARTNER_AGREEMENT_URL)}.",
    "faq_q_activity": "Что значит 'оставаться активным'?",
    "faq_a_activity": "Чтобы ваш партнерский статус не был деактивирован и вы продолжали получать LTV-выплаты, нужно совершать минимум <b>1 успешное действие</b> (рекомендация или подключение) <b>каждые 6 месяцев</b>.",

    "faq_back_btn": "⬅️ Назад к вопросам",
    "back_to_main_menu_btn": "⬅️ Главное Меню",
    "back_to_role_menu_btn": "⬅️ Меню Модели", # Общая кнопка назад в меню роли
    "unknown_command": "🤔 Хм, не знаю такой команды. Попробуйте /start или используйте кнопки меню.",
    "state_reset": "Хорошо, давайте начнем сначала. Выберите ваш формат:",
    "coming_soon": "⚙️ Этот раздел в разработке.",
    "error_occurred": "❗️ Произошла ошибка. Пожалуйста, попробуйте позже или начните сначала /start.",
}
# --- Конец секции текстов ---


# --- Настройка Логгирования ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s')

# --- Инициализация ---
storage = MemoryStorage()
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

# --- Состояния FSM ---
class PartnerOnboarding(StatesGroup):
    awaiting_role = State()
    showing_referral_menu = State()
    showing_integrator_menu = State()
    showing_faq = State()
    showing_faq_answer = State()
    # Дополнительные состояния для потенциальных подменю
    showing_points_prizes = State()
    showing_bonuses = State()
    showing_rules = State()
    showing_details = State()
    showing_contacts = State()

# --- Клавиатуры ---

# Кнопка "Назад" (универсальная)
def get_back_button(callback_data="back_to_main_menu"):
    return InlineKeyboardButton("⬅️ Назад", callback_data=callback_data)

def get_role_kb():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(TEXTS_RU["role_referral_btn"], callback_data="role_referral"),
        InlineKeyboardButton(TEXTS_RU["role_integrator_btn"], callback_data="role_integrator")
    )

# Меню для РЕФЕРАЛА
def get_referral_menu_kb():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("ℹ️ О Модели Подробнее", callback_data="ref_show_details"),
        InlineKeyboardButton("💰 Уровни и Выплаты", callback_data="ref_show_levels"),
        InlineKeyboardButton("🏆 Баллы и Призы", callback_data="show_points_prizes"), # Общий раздел
        InlineKeyboardButton("🚀 Акции и Бонусы", callback_data="show_bonuses"),     # Общий раздел
        InlineKeyboardButton("📜 Важные Детали", callback_data="show_details"),     # Общий раздел
        InlineKeyboardButton("⚖️ Правила Закрепления Сделок", callback_data="show_rules"),# Общий раздел
        InlineKeyboardButton("🏁 Как Начать / Стать Партнером", callback_data="show_how_to_start"),# Общий раздел
        InlineKeyboardButton("❓ FAQ", callback_data="show_faq"),
        InlineKeyboardButton("📞 Контакты", callback_data="show_contacts"),         # Общий раздел
        InlineKeyboardButton(TEXTS_RU["back_to_main_menu_btn"], callback_data="back_to_main_menu") # Возврат в главное меню
    )

# Меню для ИНТЕГРАТОРА
def get_integrator_menu_kb():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("ℹ️ О Модели Подробнее", callback_data="int_show_details"),
        InlineKeyboardButton("💰 Уровни и Выплаты", callback_data="int_show_levels"),
        InlineKeyboardButton("🏆 Баллы и Призы", callback_data="show_points_prizes"), # Общий раздел
        InlineKeyboardButton("🚀 Акции и Бонусы", callback_data="show_bonuses"),     # Общий раздел
        InlineKeyboardButton("📜 Важные Детали", callback_data="show_details"),     # Общий раздел
        InlineKeyboardButton("⚖️ Правила Закрепления Сделок", callback_data="show_rules"),# Общий раздел
        InlineKeyboardButton("🏁 Как Начать / Стать Партнером", callback_data="show_how_to_start"),# Общий раздел
        InlineKeyboardButton("❓ FAQ", callback_data="show_faq"),
        InlineKeyboardButton("📞 Контакты", callback_data="show_contacts"),         # Общий раздел
        InlineKeyboardButton(TEXTS_RU["back_to_main_menu_btn"], callback_data="back_to_main_menu") # Возврат в главное меню
    )

# Клавиатура для общих разделов (Баллы, Бонусы и т.д.)
def get_common_section_kb(back_callback="back_to_role_menu"):
     # По умолчанию кнопка Назад ведет в меню роли
    return InlineKeyboardMarkup().add(get_back_button(callback_data=back_callback))


# Клавиатура FAQ
def get_faq_kb(role):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(TEXTS_RU["faq_q_levels"], callback_data="faq_a_levels"))
    kb.add(InlineKeyboardButton(TEXTS_RU["faq_q_payout"], callback_data="faq_a_payout"))
    # Вопрос про передачу клиента зависит от роли
    if role == 'referral':
        kb.add(InlineKeyboardButton(TEXTS_RU["faq_q_client_referral"], callback_data="faq_a_client_referral"))
    else:
        kb.add(InlineKeyboardButton(TEXTS_RU["faq_q_client_integrator"], callback_data="faq_a_client_integrator"))
    kb.add(InlineKeyboardButton(TEXTS_RU["faq_q_points_prizes"], callback_data="faq_a_points_prizes"))
    kb.add(InlineKeyboardButton(TEXTS_RU["faq_q_agreement"], callback_data="faq_a_agreement"))
    kb.add(InlineKeyboardButton(TEXTS_RU["faq_q_activity"], callback_data="faq_a_activity"))
    # Добавить кнопку "Назад"
    kb.add(get_back_button(callback_data="back_to_role_menu")) # Назад в меню роли
    return kb

# Кнопка Назад для ответа FAQ
def get_back_to_faq_kb():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(TEXTS_RU["faq_back_btn"], callback_data="show_faq") # Возврат к списку вопросов
    )

# Клавиатура Главного Меню (для /menu и кнопки Назад)
def get_main_menu_kb():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(TEXTS_RU["role_referral_btn"], callback_data="role_referral"),
        InlineKeyboardButton(TEXTS_RU["role_integrator_btn"], callback_data="role_integrator"),
        InlineKeyboardButton("🏆 Баллы и Призы", callback_data="show_points_prizes"),
        InlineKeyboardButton("🚀 Акции и Бонусы", callback_data="show_bonuses"),
        InlineKeyboardButton("📞 Контакты", callback_data="show_contacts"),
        InlineKeyboardButton("❓ Общий FAQ", callback_data="show_faq") # Ведет в FAQ без контекста роли, если нужно
    )

# --- Вспомогательные функции отправки сообщений ---
async def send_or_edit(message: types.Message, text: str, reply_markup: types.InlineKeyboardMarkup = None, disable_web_page_preview=False):
    """ Пытается отредактировать сообщение, если не выходит - отправляет новое. """
    try:
        # Проверяем, можно ли редактировать (сообщение от бота и не слишком старое)
        # В aiogram 2.x нет простого способа проверить is_bot, делаем через try-except
        await message.edit_text(text, reply_markup=reply_markup, disable_web_page_preview=disable_web_page_preview)
        logging.debug(f"Message {message.message_id} edited.")
    except Exception as e:
        logging.warning(f"Cannot edit message {message.message_id}, sending new one. Reason: {e}")
        await message.answer(text, reply_markup=reply_markup, disable_web_page_preview=disable_web_page_preview)

async def show_main_menu(message: types.Message, state: FSMContext):
    """ Отправляет главное меню """
    logging.info(f"Showing main menu to user {message.chat.id}")
    await state.finish() # Сбрасываем состояние при показе главного меню
    await send_or_edit(message, TEXTS_RU["main_menu_title"], reply_markup=get_main_menu_kb())


# --- Хендлеры Команд ---
@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message, state: FSMContext):
    logging.info(f"Command /start received from user {message.from_user.id}")
    await state.finish()
    await message.answer(TEXTS_RU["welcome"], reply_markup=ReplyKeyboardRemove())
    await message.answer(TEXTS_RU["choose_role"], reply_markup=get_role_kb())
    await PartnerOnboarding.awaiting_role.set()
    logging.info(f"Set state to {await state.get_state()} for user {message.from_user.id}")

@dp.message_handler(commands=['menu'], state='*')
async def cmd_menu(message: types.Message, state: FSMContext):
    logging.info(f"Command /menu received from user {message.from_user.id}")
    await show_main_menu(message, state)

@dp.message_handler(commands=['faq'], state='*')
async def cmd_faq(message: types.Message, state: FSMContext):
    logging.info(f"Command /faq received from user {message.from_user.id}")
    current_state = await state.get_state()
    user_data = await state.get_data()
    role = user_data.get('chosen_role')
    logging.info(f"Current state: {current_state}, role from data: {role}")

    # Если роль неизвестна (например, вызвали /faq до выбора роли), ставим 'referral' для показа вопросов
    role_for_faq = role if role in ['referral', 'integrator'] else 'referral'
    await message.answer(TEXTS_RU["faq_title"], reply_markup=get_faq_kb(role=role_for_faq))
    await PartnerOnboarding.showing_faq.set() # Устанавливаем состояние FAQ
    logging.info(f"Set state to {await state.get_state()} for user {message.from_user.id}")

@dp.message_handler(commands=['points', 'prizes'], state='*')
async def cmd_points(message: types.Message, state: FSMContext):
    logging.info(f"Command /points received from user {message.from_user.id}")
    await state.set_state(PartnerOnboarding.showing_points_prizes) # Устанавливаем состояние, чтобы кнопка Назад работала
    await message.answer(TEXTS_RU["points_title"], disable_web_page_preview=True)
    # Кнопка Назад будет вести в главное меню, т.к. мы не знаем контекст роли
    await message.answer(TEXTS_RU["prizes_title"], reply_markup=get_common_section_kb("back_to_main_menu"), disable_web_page_preview=True)

@dp.message_handler(commands=['bonuses', 'actions'], state='*')
async def cmd_bonuses(message: types.Message, state: FSMContext):
    logging.info(f"Command /bonuses received from user {message.from_user.id}")
    await state.set_state(PartnerOnboarding.showing_bonuses)
    await message.answer(TEXTS_RU["bonuses_title"], reply_markup=get_common_section_kb("back_to_main_menu"), disable_web_page_preview=True)

@dp.message_handler(commands=['rules'], state='*')
async def cmd_rules(message: types.Message, state: FSMContext):
    logging.info(f"Command /rules received from user {message.from_user.id}")
    await state.set_state(PartnerOnboarding.showing_rules)
    await message.answer(TEXTS_RU["rules_title"], reply_markup=get_common_section_kb("back_to_main_menu"), disable_web_page_preview=True)

@dp.message_handler(commands=['contacts'], state='*')
async def cmd_contacts(message: types.Message, state: FSMContext):
    logging.info(f"Command /contacts received from user {message.from_user.id}")
    await state.set_state(PartnerOnboarding.showing_contacts)
    await message.answer(TEXTS_RU["contacts_title"], reply_markup=get_common_section_kb("back_to_main_menu"), disable_web_page_preview=True)

@dp.message_handler(commands=['help'], state='*')
async def cmd_help(message: types.Message, state: FSMContext):
     logging.info(f"Command /help received from user {message.from_user.id}")
     help_text = text(
         bold("Доступные команды:"),
         "/start - Начать работу с ботом / Выбрать роль",
         "/menu - Показать основное меню",
         "/faq - Часто задаваемые вопросы",
         "/points - Баллы за активность и призы",
         "/bonuses - Акции и бонусы",
         "/rules - Правила закрепления сделок",
         "/contacts - Контакты поддержки",
         "/help - Показать это сообщение",
         sep="\n"
     )
     await message.answer(help_text)


# --- Хендлеры Колбэков ---

# Обработка выбора роли
@dp.callback_query_handler(lambda c: c.data.startswith('role_'), state=PartnerOnboarding.awaiting_role)
async def cq_process_role_choice(callback_query: types.CallbackQuery, state: FSMContext):
    role = callback_query.data.split('_')[1]
    logging.info(f"Role '{role}' chosen by user {callback_query.from_user.id}")
    await bot.answer_callback_query(callback_query.id)
    await state.update_data(chosen_role=role) # Сохраняем роль в FSM

    # Отправляем меню для выбранной роли
    if role == 'referral':
        await PartnerOnboarding.showing_referral_menu.set()
        await send_or_edit(callback_query.message, TEXTS_RU["referral_menu_title"], reply_markup=get_referral_menu_kb())
    elif role == 'integrator':
        await PartnerOnboarding.showing_integrator_menu.set()
        await send_or_edit(callback_query.message, TEXTS_RU["integrator_menu_title"], reply_markup=get_integrator_menu_kb())
    else:
        logging.error(f"Unknown role callback: {callback_query.data}")
        await callback_query.message.answer(TEXTS_RU["error_occurred"])
        await state.finish()
    logging.info(f"Set state to {await state.get_state()} for user {callback_query.from_user.id}")

# Обработка кнопок "Назад"
@dp.callback_query_handler(lambda c: c.data == 'back_to_main_menu', state='*')
async def cq_back_to_main_menu(callback_query: types.CallbackQuery, state: FSMContext):
    logging.info(f"Back to main menu requested by user {callback_query.from_user.id}")
    await bot.answer_callback_query(callback_query.id)
    await show_main_menu(callback_query.message, state) # Показываем главное меню

@dp.callback_query_handler(lambda c: c.data == 'back_to_role_menu', state='*')
async def cq_back_to_role_menu(callback_query: types.CallbackQuery, state: FSMContext):
    logging.info(f"Back to role menu requested by user {callback_query.from_user.id}")
    await bot.answer_callback_query(callback_query.id)
    user_data = await state.get_data()
    role = user_data.get('chosen_role')
    if role == 'referral':
        await PartnerOnboarding.showing_referral_menu.set()
        await send_or_edit(callback_query.message, TEXTS_RU["referral_menu_title"], reply_markup=get_referral_menu_kb())
    elif role == 'integrator':
        await PartnerOnboarding.showing_integrator_menu.set()
        await send_or_edit(callback_query.message, TEXTS_RU["integrator_menu_title"], reply_markup=get_integrator_menu_kb())
    else:
        logging.warning(f"Cannot go back to role menu, role unknown for user {callback_query.from_user.id}. Showing main menu.")
        await show_main_menu(callback_query.message, state) # Если роль не найдена, показываем главное меню
    logging.info(f"Set state to {await state.get_state()} for user {callback_query.from_user.id}")


# --- Хендлеры для МЕНЮ РЕФЕРАЛА ---
@dp.callback_query_handler(lambda c: c.data.startswith('ref_'), state=PartnerOnboarding.showing_referral_menu)
async def cq_referral_menu_handler(callback_query: types.CallbackQuery, state: FSMContext):
    action = callback_query.data.split('_')[1] # show_details, show_levels
    logging.info(f"Referral menu action '{action}' requested by user {callback_query.from_user.id}")
    await bot.answer_callback_query(callback_query.id)
    back_button_kb = get_common_section_kb("back_to_role_menu") # Кнопка Назад ведет в меню реферала

    if action == 'show_details':
        await send_or_edit(callback_query.message, TEXTS_RU["referral_details_title"] + "\n\n" + TEXTS_RU["referral_details_text"], reply_markup=back_button_kb)
    elif action == 'show_levels':
        await send_or_edit(callback_query.message, TEXTS_RU["referral_levels_title"] + "\n\n" + TEXTS_RU["referral_levels_text"], reply_markup=back_button_kb)
    # Другие кнопки меню реферала обрабатываются общими хендлерами ниже (show_points_prizes и т.д.)


# --- Хендлеры для МЕНЮ ИНТЕГРАТОРА ---
@dp.callback_query_handler(lambda c: c.data.startswith('int_'), state=PartnerOnboarding.showing_integrator_menu)
async def cq_integrator_menu_handler(callback_query: types.CallbackQuery, state: FSMContext):
    action = callback_query.data.split('_')[1] # show_details, show_levels
    logging.info(f"Integrator menu action '{action}' requested by user {callback_query.from_user.id}")
    await bot.answer_callback_query(callback_query.id)
    back_button_kb = get_common_section_kb("back_to_role_menu") # Кнопка Назад ведет в меню интегратора

    if action == 'show_details':
        await send_or_edit(callback_query.message, TEXTS_RU["integrator_details_title"] + "\n\n" + TEXTS_RU["integrator_details_text"], reply_markup=back_button_kb)
    elif action == 'show_levels':
        await send_or_edit(callback_query.message, TEXTS_RU["integrator_levels_title"] + "\n\n" + TEXTS_RU["integrator_levels_text"], reply_markup=back_button_kb)
    # Другие кнопки меню интегратора обрабатываются общими хендлерами ниже


# --- ОБЩИЕ Хендлеры для разделов (из любого меню) ---
@dp.callback_query_handler(lambda c: c.data == 'show_points_prizes', state='*')
async def cq_show_points_prizes(callback_query: types.CallbackQuery, state: FSMContext):
    logging.info(f"Points/Prizes section requested by user {callback_query.from_user.id}")
    await bot.answer_callback_query(callback_query.id)
    await state.set_state(PartnerOnboarding.showing_points_prizes)
    await send_or_edit(callback_query.message, TEXTS_RU["points_title"] + "\n\n" + TEXTS_RU["points_text"], disable_web_page_preview=True)
    await callback_query.message.answer(TEXTS_RU["prizes_title"]+ "\n\n" + TEXTS_RU["prizes_text"], reply_markup=get_common_section_kb("back_to_role_menu"), disable_web_page_preview=True)

@dp.callback_query_handler(lambda c: c.data == 'show_bonuses', state='*')
async def cq_show_bonuses(callback_query: types.CallbackQuery, state: FSMContext):
    logging.info(f"Bonuses section requested by user {callback_query.from_user.id}")
    await bot.answer_callback_query(callback_query.id)
    await state.set_state(PartnerOnboarding.showing_bonuses)
    await send_or_edit(callback_query.message, TEXTS_RU["bonuses_title"] + "\n\n" + TEXTS_RU["bonuses_text"], reply_markup=get_common_section_kb("back_to_role_menu"), disable_web_page_preview=True)

@dp.callback_query_handler(lambda c: c.data == 'show_rules', state='*')
async def cq_show_rules(callback_query: types.CallbackQuery, state: FSMContext):
    logging.info(f"Rules section requested by user {callback_query.from_user.id}")
    await bot.answer_callback_query(callback_query.id)
    await state.set_state(PartnerOnboarding.showing_rules)
    await send_or_edit(callback_query.message, TEXTS_RU["rules_title"] + "\n\n" + TEXTS_RU["rules_text"], reply_markup=get_common_section_kb("back_to_role_menu"), disable_web_page_preview=True)

@dp.callback_query_handler(lambda c: c.data == 'show_details', state='*')
async def cq_show_details(callback_query: types.CallbackQuery, state: FSMContext):
    logging.info(f"Details section requested by user {callback_query.from_user.id}")
    await bot.answer_callback_query(callback_query.id)
    await state.set_state(PartnerOnboarding.showing_details)
    # Используем lambda для форматирования ссылки на соглашение
    details_text = TEXTS_RU["important_details_text"](agr_link=PARTNER_AGREEMENT_URL)
    await send_or_edit(callback_query.message, TEXTS_RU["important_details_title"] + "\n\n" + details_text, reply_markup=get_common_section_kb("back_to_role_menu"), disable_web_page_preview=True)

@dp.callback_query_handler(lambda c: c.data == 'show_how_to_start', state='*')
async def cq_show_how_to_start(callback_query: types.CallbackQuery, state: FSMContext):
    logging.info(f"How to Start section requested by user {callback_query.from_user.id}")
    await bot.answer_callback_query(callback_query.id)
    # Используем lambda для форматирования всех ссылок
    start_text = TEXTS_RU["how_to_start_text"]()
    await send_or_edit(callback_query.message, TEXTS_RU["how_to_start_title"] + "\n\n" + start_text, reply_markup=get_common_section_kb("back_to_role_menu"), disable_web_page_preview=True)

@dp.callback_query_handler(lambda c: c.data == 'show_contacts', state='*')
async def cq_show_contacts(callback_query: types.CallbackQuery, state: FSMContext):
    logging.info(f"Contacts section requested by user {callback_query.from_user.id}")
    await bot.answer_callback_query(callback_query.id)
    await state.set_state(PartnerOnboarding.showing_contacts)
    # Используем lambda для форматирования контактов
    contacts_text = TEXTS_RU["contacts_text"]()
    await send_or_edit(callback_query.message, TEXTS_RU["contacts_title"] + "\n\n" + contacts_text, reply_markup=get_common_section_kb("back_to_role_menu"), disable_web_page_preview=True)


# --- Хендлеры для FAQ ---
@dp.callback_query_handler(lambda c: c.data == 'show_faq', state='*')
async def cq_show_faq_list(callback_query: types.CallbackQuery, state: FSMContext):
    logging.info(f"FAQ list requested by user {callback_query.from_user.id}")
    await bot.answer_callback_query(callback_query.id)
    user_data = await state.get_data()
    role = user_data.get('chosen_role', 'referral') # По умолчанию реферал, если роль не выбрана
    logging.info(f"Showing FAQ for role: {role}")
    await send_or_edit(callback_query.message, TEXTS_RU["faq_title"], reply_markup=get_faq_kb(role))
    await PartnerOnboarding.showing_faq.set()
    logging.info(f"Set state to {await state.get_state()} for user {callback_query.from_user.id}")


@dp.callback_query_handler(lambda c: c.data.startswith('faq_a_'), state=PartnerOnboarding.showing_faq)
async def cq_show_faq_answer(callback_query: types.CallbackQuery, state: FSMContext):
    answer_key = callback_query.data
    logging.info(f"FAQ answer '{answer_key}' requested by user {callback_query.from_user.id}")
    await bot.answer_callback_query(callback_query.id)

    answer_text = TEXTS_RU.get(answer_key, "Извините, ответ на этот вопрос пока не добавлен.")

    # Форматируем ссылки, если нужно (для ответов, где они есть)
    try:
         answer_text = answer_text.format(
             cabinet_url=PARTNER_CABINET_URL,
             agreement_url=PARTNER_AGREEMENT_URL
         )
    except KeyError:
         pass # Ничего страшного, если плейсхолдеров нет
    except Exception as e:
         logging.error(f"Error formatting FAQ answer {answer_key}: {e}")
         answer_text = TEXTS_RU["error_occurred"]

    await send_or_edit(callback_query.message, answer_text, reply_markup=get_back_to_faq_kb(), disable_web_page_preview=True)
    await PartnerOnboarding.showing_faq_answer.set()
    logging.info(f"Set state to {await state.get_state()} for user {callback_query.from_user.id}")


# --- Обработка неизвестных сообщений ---
@dp.message_handler(state='*')
async def handle_unknown_message(message: types.Message, state: FSMContext):
    current_state_name = await state.get_state()
    logging.warning(f"Unknown message '{message.text}' from user {message.from_user.id} in state {current_state_name}")
    # В зависимости от состояния можно давать более конкретные подсказки
    # Но пока ограничимся общим сообщением
    await message.answer(TEXTS_RU["unknown_command"])


# --- Запуск и Остановка ---
async def set_bot_commands(dp: Dispatcher):
    """Установка команд бота"""
    commands = [
        BotCommand(command="/start", description="🚀 Начать / Выбрать роль"),
        BotCommand(command="/menu", description="📖 Главное меню"),
        BotCommand(command="/faq", description="❓ Частые вопросы"),
        BotCommand(command="/points", description="🏆 Баллы и Призы"),
        BotCommand(command="/bonuses", description="🚀 Акции и Бонусы"),
        BotCommand(command="/rules", description="⚖️ Правила закрепления сделок"),
        BotCommand(command="/contacts", description="📞 Контакты"),
        BotCommand(command="/help", description="ℹ️ Помощь по командам"),
    ]
    await dp.bot.set_my_commands(commands)
    logging.info("Bot commands set.")

async def on_startup(dp: Dispatcher):
    logging.warning('Bot starting polling...')
    await set_bot_commands(dp) # Устанавливаем команды при старте

async def on_shutdown(dp: Dispatcher):
    logging.warning('Bot shutting down...')
    await dp.storage.close()
    await dp.storage.wait_closed()
    # Корректное закрытие сессии в aiogram 2.x
    session = await dp.bot.get_session()
    if session and not session.closed:
       await session.close()
       logging.info("Bot session closed.")
    logging.warning('Bot shutdown complete.')


if __name__ == '__main__':
    logging.info("Initializing bot...")
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
