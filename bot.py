import logging
import os # Добавлен для работы с переменными окружения

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.markdown import text, bold, hlink # Используем HTML

# --- Константы и Конфигурация ---

# Получаем токен из переменной окружения (безопасный способ)
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not API_TOKEN:
    logging.error("Critical: TELEGRAM_BOT_TOKEN environment variable not set!")
    # В реальном проде можно либо выйти, либо установить дефолтный для локальной отладки
    # exit("Environment variable TELEGRAM_BOT_TOKEN is required.")
    # Для локального теста можно раскомментировать строку ниже и вставить токен,
    # но НЕ КОММИТЬ ЭТО В GIT!
    # API_TOKEN = 'YOUR_FALLBACK_TOKEN_FOR_LOCAL_TEST_ONLY'


# --- Ссылки (ЗАМЕНИ НА СВОИ РЕАЛЬНЫЕ ССЫЛКИ!) ---
REGISTRATION_URL = "https://revvy.prmonline.ru" # ЗАМЕНИ!
REFERRAL_REGULATIONS_URL = "https://revvy-space.teamly.ru/space/ce9ca057-8849-476c-a3fb-8c0935f1746c/article/d29f7b00-2a54-41ec-9b89-4ef277ebb9d3" # ЗАМЕНИ!
INTEGRATOR_REGULATIONS_URL = "https://revvy-space.teamly.ru/space/ce9ca057-8849-476c-a3fb-8c0935f1746c/article/d29f7b00-2a54-41ec-9b89-4ef277ebb9d3" # ЗАМЕНИ!
MATERIALS_URL = "https://revvy-space.teamly.ru/space/ce9ca057-8849-476c-a3fb-8c0935f1746c/article/d29f7b00-2a54-41ec-9b89-4ef277ebb9d3" # ЗАМЕНИ!
MANAGER_CONTACT_LINK = "https://t.me/v_tsykunov" # ЗАМЕНИ! (Ссылка на ТГ)
MANAGER_CONTACT_EMAIL = "v.tsykunov@revvy.ru" # ЗАМЕНИ!
PARTNER_CABINET_URL = "https://revvy.prmonline.ru" # ЗАМЕНИ!
VIDEO_INSTRUCTION_URL = "https://revvy-space.teamly.ru/space/ce9ca057-8849-476c-a3fb-8c0935f1746c/article/d29f7b00-2a54-41ec-9b89-4ef277ebb9d3" # ЗАМЕНИ!
# --- Конец секции ссылок ---


# --- Тексты (RU) ---
TEXTS_RU = {
    "welcome": "🚀 <b>Добро пожаловать в партнёрскую программу Revvy!</b>\n\nМы рады, что вы решили к нам присоединиться.\n\nДавайте начнём! Пожалуйста, выберите, как вы планируете сотрудничать:",
    "choose_role": "👇 <b>Выберите вашу роль:</b>",
    "role_referral_btn": "🤝 Рекомендовать Revvy (Реферал)",
    "role_integrator_btn": "⚙️ Продавать и подключать (Интегратор)",
    "referral_info": lambda reg_link=REGISTRATION_URL: text(
        "👋 <b>Отлично! Вы выбрали реферальную модель.</b>\n\n",
        "Это значит, что вы будете рекомендовать Revvy своим знакомым или клиентам и получать вознаграждение за каждую успешную оплату от привлеченных вами компаний.\n\n",
        "✨ <b>Преимущества:</b>\n",
        "   - Легкий старт, не требует глубоких технических знаний.\n",
        "   - Получаете процент с оплат на протяжении всего времени, пока клиент с нами.\n",
        "   - Мы сами занимаемся продажей, подключением и поддержкой.\n\n",
        "👇 <b>Ваши первые шаги:</b>\n",
        f"1️⃣ Зарегистрируйтесь в партнёрском кабинете по ссылке: {hlink('Открыть кабинет', reg_link)}\n",
        "2️⃣ Ознакомьтесь с деталями программы.\n",
        "3️⃣ Получите вашу уникальную реферальную ссылку в кабинете.\n",
        "4️⃣ Начинайте рекомендовать!",
    ),
    "integrator_info": lambda reg_link=REGISTRATION_URL: text(
        "🚀 <b>Супер! Вы выбрали модель Интегратора.</b>\n\n",
        "Это значит, что вы будете самостоятельно продавать Revvy, подключать клиентов и оказывать им первую линию поддержки. За это вы будете получать более высокий процент вознаграждения.\n\n",
        "✨ <b>Преимущества:</b>\n",
        "   - Максимальный процент вознаграждения.\n",
        "   - Полный контроль над процессом продажи и подключения.\n",
        "   - Возможность выстраивать долгосрочные отношения с клиентами.\n\n",
        "👇 <b>Ваши первые шаги:</b>\n",
        f"1️⃣ Зарегистрируйтесь в партнёрском кабинете: {hlink('Открыть кабинет', reg_link)}\n",
        "2️⃣ Внимательно изучите условия и регламент.\n",
        "3️⃣ Ознакомьтесь с обучающими материалами и инструкциями.\n",
        "4️⃣ Свяжитесь с вашим менеджером для старта.",
    ),
    "onboarding_checklist_title": "📋 <b>Ваш чек-лист для старта:</b>\n\nПройдите по шагам, чтобы быстрее начать зарабатывать:",
    "onboarding_step1_btn": "1. 🔑 Открыть/Зарегистрировать кабинет",
    "onboarding_step2_referral_btn": "2. 📄 Прочитать реф. регламент",
    "onboarding_step2_integrator_btn": "2. 📘 Прочитать регламент интегратора",
    "onboarding_step3_materials_btn": "3. 🧰 Изучить материалы и видео",
    "onboarding_step4_manager_btn": "4. 💬 Написать менеджеру",
    "onboarding_step5_ready_btn": "✅ Я всё изучил(а) и готов(а) работать!",
    "onboarding_complete": "🎉 <b>Поздравляем! Вы готовы к работе!</b>\n\nЖелаем вам успешных сделок, довольных клиентов и высокого дохода с Revvy!\n\n💬 Не стесняйтесь задавать вопросы вашему менеджеру.\n💡 Следите за новостями и обновлениями в партнёрском кабинете и наших каналах!",
    "faq_button": "❓ Ответы на частые вопросы (FAQ)",
    "faq_title": "🤔 <b>Часто задаваемые вопросы:</b>\n\nВыберите интересующий вас вопрос:",
    "faq_q1": "Как считаются уровни партнёров?",
    "faq_a1": lambda regulation_url: f"Уровни партнёров (Бронзовый, Серебряный, Золотой, Платиновый) зависят от <b>количества баллов</b>, накопленных за последние <b>90 дней</b>.\n\nБаллы начисляются за различные действия: регистрации по вашей ссылке, оплаты от клиентов, прохождение обучения и т.д. Чем выше уровень, тем больше ваше вознаграждение и доступные бонусы.\n\nПодробная таблица баллов и уровней есть в <a href='{regulation_url}'>регламенте</a>.",
    "faq_q2": "Когда я получу выплату?",
    "faq_a2": "Выплаты партнёрского вознаграждения производятся <b>ежемесячно</b>, обычно до 15 числа месяца, следующего за отчётным. \n\nМинимальная сумма для выплаты может быть указана в вашем договоре или регламенте. Убедитесь, что вы предоставили все необходимые реквизиты в партнёрском кабинете.",
    "faq_q3_referral": "Как передать клиента (реферал)?",
    "faq_a3_referral": lambda cabinet_url: f"Очень просто! В вашем партнёрском кабинете (<a href='{cabinet_url}'>ссылка</a>) вы найдете свою <b>уникальную реферальную ссылку</b>. \n\nОтправьте эту ссылку потенциальному клиенту. Когда он перейдет по ней и зарегистрируется/оплатит, он автоматически закрепится за вами. Также в кабинете может быть форма для ручной регистрации лида.",
    "faq_q3_integrator": "Как передать клиента (интегратор)?",
    "faq_a3_integrator": lambda cabinet_url: f"Как интегратор, вы обычно сами регистрируете клиента через специальную форму или интерфейс в партнёрском кабинете (<a href='{cabinet_url}'>ссылка</a>). \n\nУбедитесь, что вы следуете инструкциям из обучающих материалов. Если сомневаетесь, свяжитесь с вашим партнёрским менеджером.",
    "faq_q4": "Где посмотреть баллы и призы?",
    "faq_a4": lambda cabinet_url: f"Вся информация о ваших накопленных баллах, текущем уровне, истории начислений и доступных призах (если они предусмотрены программой) находится в вашем <b>партнёрском кабинете Revvy</b> (<a href='{cabinet_url}'>ссылка</a>).\n\nОбычно для этого есть специальный раздел 'Статистика', 'Баллы' или 'Мой уровень'.",
    "faq_back_btn": "⬅️ Назад к вопросам",
    "action_cancelled": "Действие отменено.",
    "unknown_command": "🤔 Кажется, я не знаю такой команды. Попробуйте начать с /start или воспользуйтесь кнопками.",
    "state_reset": "Хорошо, давайте начнем сначала. Выберите вашу роль:",
}
# --- Конец секции текстов ---


# --- Настройка Логгирования ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Инициализация ---
storage = MemoryStorage()
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML) if API_TOKEN else None # Не инициализируем бота, если нет токена
dp = Dispatcher(bot, storage=storage) if bot else None

# --- Состояния FSM ---
class OnboardingStates(StatesGroup):
    awaiting_role = State()
    onboarding_referral = State()
    onboarding_integrator = State()
    showing_faq = State()
    showing_faq_answer = State()

# --- Клавиатуры ---
def get_role_kb():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(TEXTS_RU["role_referral_btn"], callback_data="role_referral"),
        InlineKeyboardButton(TEXTS_RU["role_integrator_btn"], callback_data="role_integrator")
    )
    return keyboard

def get_onboarding_kb(role: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(TEXTS_RU["onboarding_step1_btn"], url=PARTNER_CABINET_URL)
    )
    if role == 'referral':
        keyboard.add(InlineKeyboardButton(TEXTS_RU["onboarding_step2_referral_btn"], url=REFERRAL_REGULATIONS_URL))
    else: # integrator
        keyboard.add(InlineKeyboardButton(TEXTS_RU["onboarding_step2_integrator_btn"], url=INTEGRATOR_REGULATIONS_URL))

    keyboard.add(
        InlineKeyboardButton(TEXTS_RU["onboarding_step3_materials_btn"], url=MATERIALS_URL),
        InlineKeyboardButton(TEXTS_RU["onboarding_step4_manager_btn"], url=MANAGER_CONTACT_LINK),
        InlineKeyboardButton(TEXTS_RU["onboarding_step5_ready_btn"], callback_data="onboard_done")
    )
    return keyboard

def get_faq_kb(role: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(TEXTS_RU["faq_q1"], callback_data="faq_q1"),
        InlineKeyboardButton(TEXTS_RU["faq_q2"], callback_data="faq_q2"),
    )
    if role == 'referral':
        keyboard.add(InlineKeyboardButton(TEXTS_RU["faq_q3_referral"], callback_data="faq_q3_referral"))
    else:
        keyboard.add(InlineKeyboardButton(TEXTS_RU["faq_q3_integrator"], callback_data="faq_q3_integrator"))
    keyboard.add(
        InlineKeyboardButton(TEXTS_RU["faq_q4"], callback_data="faq_q4")
    )
    return keyboard

def get_back_to_faq_kb():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(TEXTS_RU["faq_back_btn"], callback_data="faq_back"))
    return keyboard

# --- Хендлеры ---
if dp: # Регистрируем хендлеры только если Dispatcher был создан (т.е. есть токен)

    @dp.message_handler(commands=['start'], state='*')
    async def send_welcome(message: types.Message, state: FSMContext):
        await state.finish()
        await message.answer(TEXTS_RU["welcome"])
        await message.answer(TEXTS_RU["choose_role"], reply_markup=get_role_kb())
        await OnboardingStates.awaiting_role.set()
        try: # Пытаемся убрать старую reply клавиатуру, если вдруг она была
            await message.answer("...", reply_markup=ReplyKeyboardRemove(), show_alert=False)
        except Exception:
            pass # Не страшно, если не получилось

    @dp.callback_query_handler(lambda c: c.data.startswith('role_'), state=OnboardingStates.awaiting_role)
    async def process_role_choice(callback_query: types.CallbackQuery, state: FSMContext):
        await bot.answer_callback_query(callback_query.id)
        role = callback_query.data.split('_')[1]
        await state.update_data(chosen_role=role)

        info_text = ""
        next_state = None
        if role == 'referral':
            info_text = TEXTS_RU["referral_info"]()
            next_state = OnboardingStates.onboarding_referral
        elif role == 'integrator':
            info_text = TEXTS_RU["integrator_info"]()
            next_state = OnboardingStates.onboarding_integrator
        else:
            await callback_query.message.answer("Произошла ошибка. Попробуйте /start")
            await state.finish()
            return

        await state.set_state(next_state)
        try:
            await callback_query.message.edit_text(f"{TEXTS_RU['welcome']}\n\n<i>Выбрана роль: {TEXTS_RU[f'role_{role}_btn']}</i>") # Редактируем приветствие
        except Exception as e:
             logging.warning(f"Could not edit welcome message: {e}") # Не критично
             await callback_query.message.answer(f"<i>Выбрана роль: {TEXTS_RU[f'role_{role}_btn']}</i>")

        await callback_query.message.answer(info_text, disable_web_page_preview=True)
        await callback_query.message.answer(TEXTS_RU["onboarding_checklist_title"], reply_markup=get_onboarding_kb(role))
        faq_kb = InlineKeyboardMarkup().add(InlineKeyboardButton(TEXTS_RU["faq_button"], callback_data="show_faq"))
        await callback_query.message.answer("Есть вопросы? 👇", reply_markup=faq_kb)

    @dp.callback_query_handler(lambda c: c.data == 'onboard_done', state=[OnboardingStates.onboarding_referral, OnboardingStates.onboarding_integrator])
    async def process_onboarding_complete(callback_query: types.CallbackQuery, state: FSMContext):
        await bot.answer_callback_query(callback_query.id)
        try:
             # Ищем сообщение с чек-листом (оно перед FAQ) и убираем кнопки
            await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                                message_id=callback_query.message.message_id -1,
                                                reply_markup=None)
        except Exception as e:
            logging.warning(f"Could not edit checklist message markup: {e}")
            # Если не нашли предыдущее, убираем кнопки FAQ из текущего
            try:
                await callback_query.message.edit_reply_markup(reply_markup=None)
            except Exception as e2:
                 logging.warning(f"Could not edit FAQ button message markup: {e2}")


        await callback_query.message.answer(TEXTS_RU["onboarding_complete"])
        await state.finish()

    @dp.callback_query_handler(lambda c: c.data == 'show_faq', state=[OnboardingStates.onboarding_referral, OnboardingStates.onboarding_integrator, OnboardingStates.showing_faq_answer])
    async def process_show_faq(callback_query: types.CallbackQuery, state: FSMContext):
        await bot.answer_callback_query(callback_query.id)
        user_data = await state.get_data()
        role = user_data.get('chosen_role', 'referral')

        try:
            await callback_query.message.edit_text(TEXTS_RU["faq_title"], reply_markup=get_faq_kb(role))
        except Exception as e:
            logging.warning(f"Could not edit message to show FAQ: {e}")
            # Если редактирование не удалось (например, сообщение старое), отправим новое
            await callback_query.message.answer(TEXTS_RU["faq_title"], reply_markup=get_faq_kb(role))
        await OnboardingStates.showing_faq.set()

    @dp.callback_query_handler(lambda c: c.data.startswith('faq_q'), state=OnboardingStates.showing_faq)
    async def process_faq_question(callback_query: types.CallbackQuery, state: FSMContext):
        await bot.answer_callback_query(callback_query.id)
        question_key = callback_query.data
        answer_key_base = question_key.replace('q', 'a')

        user_data = await state.get_data()
        role = user_data.get('chosen_role', 'referral')

        # Получаем текст ответа (он может быть функцией lambda)
        answer_template = TEXTS_RU.get(answer_key_base)
        if not answer_template:
            answer_text = "Извините, ответ на этот вопрос пока не добавлен."
        elif callable(answer_template): # Если это lambda
             regulation_url = REFERRAL_REGULATIONS_URL if role == 'referral' else INTEGRATOR_REGULATIONS_URL
             # Определяем, какой аргумент нужен lambda-функции
             if 'regulation_url' in answer_template.__code__.co_varnames:
                 answer_text = answer_template(regulation_url=regulation_url)
             elif 'cabinet_url' in answer_template.__code__.co_varnames:
                  answer_text = answer_template(cabinet_url=PARTNER_CABINET_URL)
             else: # Если лямбда без аргументов (на всякий случай)
                  answer_text = answer_template()
        else: # Если это просто строка
             answer_text = answer_template

        try:
            await callback_query.message.edit_text(answer_text, reply_markup=get_back_to_faq_kb(), disable_web_page_preview=True)
        except Exception as e:
             logging.warning(f"Could not edit message to show FAQ answer: {e}")
             # Если не удалось отредактировать, отправим новое
             await callback_query.message.answer(answer_text, reply_markup=get_back_to_faq_kb(), disable_web_page_preview=True)

        await OnboardingStates.showing_faq_answer.set()

    @dp.callback_query_handler(lambda c: c.data == 'faq_back', state=OnboardingStates.showing_faq_answer)
    async def process_faq_back(callback_query: types.CallbackQuery, state: FSMContext):
        # Просто вызываем хендлер показа FAQ, он отредактирует сообщение
        await process_show_faq(callback_query, state)

    @dp.message_handler(state='*')
    async def handle_unknown(message: types.Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is None:
            await message.answer(TEXTS_RU["unknown_command"] + " Начните с /start")
            return

        if current_state == OnboardingStates.awaiting_role.state:
            await message.answer("Пожалуйста, выберите вашу роль с помощью кнопок выше.")
        elif current_state in [OnboardingStates.onboarding_referral.state, OnboardingStates.onboarding_integrator.state]:
            await message.answer("Пожалуйста, используйте кнопки чек-листа, кнопку FAQ или нажмите '✅ Я готов(а)', если всё изучили.")
        elif current_state == OnboardingStates.showing_faq.state:
            await message.answer("Пожалуйста, выберите вопрос из списка FAQ с помощью кнопок.")
        elif current_state == OnboardingStates.showing_faq_answer.state:
            await message.answer("Нажмите кнопку '⬅️ Назад к вопросам', чтобы увидеть другие FAQ, или /start для начала.")
        else:
            await message.answer(TEXTS_RU["unknown_command"] + " Возможно, стоит начать сначала: /start")

# --- Запуск бота ---
if __name__ == '__main__':
    if not API_TOKEN:
        print("Please set the TELEGRAM_BOT_TOKEN environment variable.")
    elif not dp:
         print("Dispatcher not initialized (likely due to missing token).")
    else:
        logging.info("Starting bot...")
        executor.start_polling(dp, skip_updates=True)
        logging.info("Bot stopped.")
