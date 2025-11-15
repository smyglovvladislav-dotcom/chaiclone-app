import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.switch import Switch
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
import json
import os
import random
from datetime import datetime

# 🔧 КОНФИГУРАЦИЯ
class Config:
    def __init__(self):
        self.config_file = "chaiclone_config.json"
        self.load_config()
    
    def load_config(self):
        default_config = {
            "theme": "dark",
            "ai_character": {
                "name": "Ассистент",
                "personality": "дружелюбный",
                "style": "разговорный"
            },
            "cloud_services": {
                "openai": {"enabled": False, "api_key": "", "model": "gpt-3.5-turbo"},
                "google_ai": {"enabled": False, "api_key": "", "model": "gemini-pro"},
                "custom_api": {"enabled": False, "endpoint": "", "api_key": ""}
            },
            "user_profile": {
                "name": "Игрок",
                "level": 1,
                "xp": 0,
                "messages_sent": 0,
                "chats_created": 0,
                "avatar": "default",
                "status": "В сети"
            },
            "admin": {
                "password": "admin123",
                "access_enabled": True
            }
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.data = default_config
            self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

# 🤖 ИИ СИСТЕМА
class AISystem:
    def __init__(self, config):
        self.config = config
        self.personalities = {
            "дружелюбный": ["Привет! Как твои дела?", "Отлично! Рад тебя видеть!", "Как прошел твой день?"],
            "профессиональный": ["Здравствуйте. Чем могу помочь?", "Понимаю вашу ситуацию.", "Готов оказать помощь."],
            "веселый": ["Йоу! Как сам? 😎", "Опа, новое сообщение! 🎉", "Хей! Давай пообщаемся! 🚀"],
            "заботливый": ["Привет, дорогой! Как ты себя чувствуешь?", "Все будет хорошо, я с тобой 💖", "Береги себя!"]
        }
    
    def generate_response(self, user_message):
        character = self.config.data["ai_character"]
        personality = character["personality"]
        style = character["style"]
        
        # Локальные ответы на основе персонажа
        responses = self.personalities.get(personality, self.personalities["дружелюбный"])
        
        # Добавляем стиль
        base_response = random.choice(responses)
        
        if style == "формальный":
            return f"{base_response} (формальный стиль)"
        elif style == "разговорный":
            return f"{base_response} (неформально)"
        elif style == "креативный":
            return f"🎨 {base_response} 🎭"
        
        return f"{character['name']}: {base_response}"

# 🎨 КАСТОМНЫЕ ВИДЖЕТЫ
class RoundedButton(ButtonBehavior, BoxLayout):
    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, None)
        self.height = 50
        self.padding = [10, 5]
        
        with self.canvas.before:
            Color(0.2, 0.6, 0.8, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        label = Label(text=text, color=(1, 1, 1, 1), bold=True)
        self.add_widget(label)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class ProfileCard(BoxLayout):
    def __init__(self, profile_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (1, None)
        self.height = 180
        self.padding = [15, 15]
        self.spacing = 10
        
        with self.canvas.before:
            Color(0.15, 0.15, 0.2, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Аватар и имя
        top_layout = BoxLayout(size_hint_y=0.4)
        avatar = Label(text="👤", font_size='30sp')
        name_layout = BoxLayout(orientation='vertical')
        name_layout.add_widget(Label(text=profile_data["name"], font_size='18sp', bold=True))
        name_layout.add_widget(Label(text=profile_data["status"], font_size='12sp', color=(0.7, 0.7, 0.7, 1)))
        
        top_layout.add_widget(avatar)
        top_layout.add_widget(name_layout)
        
        # Статистика
        stats_layout = BoxLayout(size_hint_y=0.6)
        stats = BoxLayout(orientation='vertical')
        stats.add_widget(Label(text=f"Уровень: {profile_data['level']}", font_size='12sp'))
        stats.add_widget(Label(text=f"Сообщений: {profile_data['messages_sent']}", font_size='12sp'))
        
        progress_layout = BoxLayout(orientation='vertical', size_hint_x=0.6)
        progress_layout.add_widget(Label(text="Прогресс:", font_size='12sp'))
        progress = ProgressBar(max=100, value=profile_data["xp"])
        progress_layout.add_widget(progress)
        
        stats_layout.add_widget(stats)
        stats_layout.add_widget(progress_layout)
        
        self.add_widget(top_layout)
        self.add_widget(stats_layout)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

# 📱 ЭКРАН ЧАТА
class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = Config()
        self.ai_system = AISystem(self.config)
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        main_layout = BoxLayout(orientation='vertical')
        
        # Верхняя панель
        top_panel = BoxLayout(size_hint_y=0.08, padding=[10, 5])
        top_panel.add_widget(Label(text='[b]💬 Chai Clone[/b]', markup=True))
        
        profile_btn = Button(text='👤', size_hint_x=0.2, on_press=self.go_to_profile)
        theme_btn = Button(text='🌙', size_hint_x=0.2, on_press=self.toggle_theme)
        
        top_panel.add_widget(profile_btn)
        top_panel.add_widget(theme_btn)
        
        # История чата
        self.chat_history = ScrollView()
        self.message_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=[10, 10])
        self.message_layout.bind(minimum_height=self.message_layout.setter('height'))
        self.chat_history.add_widget(self.message_layout)
        
        # Панель ввода
        input_panel = BoxLayout(size_hint_y=0.12, padding=[10, 5], spacing=10)
        self.message_input = TextInput(
            hint_text='Введите сообщение...',
            multiline=False,
            size_hint_x=0.7,
            background_color=(0.1, 0.1, 0.1, 1) if self.config.data["theme"] == "dark" else (1, 1, 1, 1)
        )
        self.message_input.bind(on_text_validate=self.send_message)
        
        send_btn = Button(
            text='📤',
            size_hint_x=0.15,
            on_press=self.send_message,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        
        ai_btn = Button(
            text='🤖',
            size_hint_x=0.15,
            on_press=self.go_to_ai_settings,
            background_color=(0.8, 0.2, 0.8, 1)
        )
        
        input_panel.add_widget(self.message_input)
        input_panel.add_widget(send_btn)
        input_panel.add_widget(ai_btn)
        
        main_layout.add_widget(top_panel)
        main_layout.add_widget(self.chat_history)
        main_layout.add_widget(input_panel)
        
        self.add_widget(main_layout)
        
        # Приветственное сообщение
        Clock.schedule_once(self.show_welcome, 0.5)
    
    def show_welcome(self, dt):
        welcome_msg = "Привет! Я твой ИИ-помощник. Напиши мне что-нибудь, и я отвечу!"
        self.add_message(welcome_msg, is_user=False)
    
    def apply_theme(self):
        if self.config.data["theme"] == "dark":
            Window.clearcolor = (0.1, 0.1, 0.15, 1)
        else:
            Window.clearcolor = (0.95, 0.95, 0.95, 1)
    
    def toggle_theme(self, instance):
        self.config.data["theme"] = "light" if self.config.data["theme"] == "dark" else "dark"
        self.config.save_config()
        self.apply_theme()
        self.show_popup("Тема", "Тема изменена!")
    
    def go_to_profile(self, instance):
        self.manager.current = 'profile'
    
    def go_to_ai_settings(self, instance):
        self.manager.current = 'ai_settings'
    
    def send_message(self, instance):
        message = self.message_input.text.strip()
        if not message:
            return
        
        # Сообщение пользователя
        self.add_message(message, is_user=True)
        self.message_input.text = ""
        
        # Имитация загрузки ИИ
        thinking_msg = self.add_message("ИИ печатает...", is_user=False)
        
        # Ответ ИИ
        Clock.schedule_once(lambda dt: self.ai_response(message, thinking_msg), 1)
    
    def ai_response(self, user_message, thinking_msg):
        self.message_layout.remove_widget(thinking_msg)
        
        response = self.ai_system.generate_response(user_message)
        self.add_message(response, is_user=False)
        
        # Обновляем статистику
        self.config.data["user_profile"]["messages_sent"] += 1
        self.config.data["user_profile"]["xp"] += random.randint(5, 15)
        
        # Повышение уровня
        if self.config.data["user_profile"]["xp"] >= 100:
            self.config.data["user_profile"]["level"] += 1
            self.config.data["user_profile"]["xp"] = 0
            self.show_popup("Уровень повышен!", f"Теперь у тебя {self.config.data['user_profile']['level']} уровень!")
        
        self.config.save_config()
    
    def add_message(self, text, is_user=False):
        message_layout = BoxLayout(
            size_hint_y=None, 
            height=60, 
            padding=[15, 5],
            orientation='horizontal' if is_user else 'horizontal-reverse'
        )
        
        with message_layout.canvas.before:
            if is_user:
                Color(0.2, 0.5, 0.8, 0.8)
            else:
                Color(0.3, 0.3, 0.4, 0.8)
            message_layout.rect = RoundedRectangle(pos=message_layout.pos, size=message_layout.size, radius=[15])
        
        message_layout.bind(pos=self.update_message_rect, size=self.update_message_rect)
        
        avatar = Label(text="👤" if is_user else "🤖", font_size='20sp')
        message_label = Label(
            text=text,
            text_size=(Window.width * 0.7, None),
            size_hint_x=0.8
        )
        
        message_layout.add_widget(avatar)
        message_layout.add_widget(message_label)
        self.message_layout.add_widget(message_layout)
        
        self.chat_history.scroll_to(message_layout)
        return message_layout
    
    def update_message_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size
    
    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.7, 0.4)
        )
        popup.open()

# 👤 ЭКРАН ПРОФИЛЯ (В СТИЛЕ STEAM)
class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = Config()
        self.setup_ui()
    
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical')
        
        # Заголовок
        header = BoxLayout(size_hint_y=0.1, padding=[10, 5])
        header.add_widget(Label(text='[b]👤 Мой Профиль[/b]', markup=True))
        back_btn = Button(text='← Назад', size_hint_x=0.3, on_press=self.go_to_chat)
        header.add_widget(back_btn)
        
        # Контент профиля
        content = ScrollView()
        profile_content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=[20, 20])
        profile_content.bind(minimum_height=profile_content.setter('height'))
        
        # Карточка профиля
        profile_card = ProfileCard(self.config.data["user_profile"])
        profile_content.add_widget(profile_card)
        
        # Действия
        actions_label = Label(text='[b]Действия:[/b]', markup=True, size_hint_y=None, height=30)
        profile_content.add_widget(actions_label)
        
        actions = BoxLayout(orientation='vertical', size_hint_y=None, height=200, spacing=10)
        
        ai_settings_btn = Button(text='⚙️ Настройки ИИ', on_press=self.go_to_ai_settings)
        admin_btn = Button(text='🔧 Админ-панель', on_press=self.go_to_admin)
        stats_btn = Button(text='📊 Статистика', on_press=self.show_stats)
        
        actions.add_widget(ai_settings_btn)
        actions.add_widget(admin_btn)
        actions.add_widget(stats_btn)
        
        profile_content.add_widget(actions)
        
        content.add_widget(profile_content)
        layout.add_widget(header)
        layout.add_widget(content)
        
        self.add_widget(layout)
    
    def go_to_chat(self, instance):
        self.manager.current = 'chat'
    
    def go_to_ai_settings(self, instance):
        self.manager.current = 'ai_settings'
    
    def go_to_admin(self, instance):
        # Проверка пароля для админ-панели
        self.show_password_popup()
    
    def show_password_popup(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        password_input = TextInput(hint_text='Введите пароль', password=True)
        submit_btn = Button(text='Войти', on_press=lambda x: self.check_password(password_input.text))
        
        content.add_widget(password_input)
        content.add_widget(submit_btn)
        
        self.popup = Popup(title='Админ доступ', content=content, size_hint=(0.8, 0.4))
        self.popup.open()
    
    def check_password(self, password):
        if password == self.config.data["admin"]["password"]:
            self.popup.dismiss()
            self.manager.current = 'admin'
        else:
            self.show_popup("Ошибка", "Неверный пароль!")
    
    def show_stats(self, instance):
        stats = self.config.data["user_profile"]
        stats_text = f"""
[b]Статистика:[/b]

• Уровень: {stats['level']}
• Опыт: {stats['xp']}/100
• Сообщений отправлено: {stats['messages_sent']}
• Чатов создано: {stats['chats_created']}
• Статус: {stats['status']}
"""
        self.show_popup("📊 Статистика", stats_text)
    
    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message, markup=True),
            size_hint=(0.8, 0.6)
        )
        popup.open()

# ⚙️ НАСТРОЙКИ ИИ
class AISettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = Config()
        self.setup_ui()
    
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical')
        
        header = BoxLayout(size_hint_y=0.1, padding=[10, 5])
        header.add_widget(Label(text='[b]⚙️ Настройки ИИ[/b]', markup=True))
        back_btn = Button(text='← Назад', size_hint_x=0.3, on_press=self.go_to_profile)
        header.add_widget(back_btn)
        
        content = ScrollView()
        settings_content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=[20, 20])
        settings_content.bind(minimum_height=settings_content.setter('height'))
        
        # Настройки персонажа ИИ
        char_label = Label(text='[b]Персонаж ИИ:[/b]', markup=True, size_hint_y=None, height=30)
        settings_content.add_widget(char_label)
        
        # Имя ИИ
        name_layout = BoxLayout(size_hint_y=None, height=50)
        name_layout.add_widget(Label(text='Имя:'))
        self.name_input = TextInput(text=self.config.data["ai_character"]["name"])
        name_layout.add_widget(self.name_input)
        
        # Характер
        personality_layout = BoxLayout(size_hint_y=None, height=50)
        personality_layout.add_widget(Label(text='Характер:'))
        self.personality_spinner = Spinner(
            text=self.config.data["ai_character"]["personality"],
            values=('дружелюбный', 'профессиональный', 'веселый', 'заботливый')
        )
        personality_layout.add_widget(self.personality_spinner)
        
        # Стиль
        style_layout = BoxLayout(size_hint_y=None, height=50)
        style_layout.add_widget(Label(text='Стиль:'))
        self.style_spinner = Spinner(
            text=self.config.data["ai_character"]["style"],
            values=('разговорный', 'формальный', 'креативный')
        )
        style_layout.add_widget(self.style_spinner)
        
        settings_content.add_widget(name_layout)
        settings_content.add_widget(personality_layout)
        settings_content.add_widget(style_layout)
        
        # Облачные сервисы
        cloud_label = Label(text='[b]Облачные сервисы:[/b]', markup=True, size_hint_y=None, height=30)
        settings_content.add_widget(cloud_label)
        
        # OpenAI
        openai_layout = BoxLayout(size_hint_y=None, height=50)
        openai_layout.add_widget(Label(text='OpenAI:'))
        self.openai_switch = Switch(active=self.config.data["cloud_services"]["openai"]["enabled"])
        openai_key_input = TextInput(
            hint_text='API ключ OpenAI',
            text=self.config.data["cloud_services"]["openai"]["api_key"],
            password=True
        )
        openai_layout.add_widget(self.openai_switch)
        openai_layout.add_widget(openai_key_input)
        
        settings_content.add_widget(openai_layout)
        
        # Кнопка сохранения
        save_btn = Button(
            text='💾 Сохранить настройки',
            size_hint_y=None,
            height=50,
            on_press=self.save_settings,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        settings_content.add_widget(save_btn)
        
        content.add_widget(settings_content)
        layout.add_widget(header)
        layout.add_widget(content)
        
        self.add_widget(layout)
    
    def save_settings(self, instance):
        # Сохраняем настройки персонажа
        self.config.data["ai_character"]["name"] = self.name_input.text
        self.config.data["ai_character"]["personality"] = self.personality_spinner.text
        self.config.data["ai_character"]["style"] = self.style_spinner.text
        
        # Сохраняем настройки облачных сервисов
        self.config.data["cloud_services"]["openai"]["enabled"] = self.openai_switch.active
        
        self.config.save_config()
        self.show_popup("Успех", "Настройки сохранены!")
    
    def go_to_profile(self, instance):
        self.manager.current = 'profile'
    
    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.7, 0.4)
        )
        popup.open()

# 🔧 АДМИН-ПАНЕЛЬ
class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = Config()
        self.setup_ui()
    
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical')
        
        header = BoxLayout(size_hint_y=0.1, padding=[10, 5])
        header.add_widget(Label(text='[b]🔧 Админ-панель[/b]', markup=True))
        back_btn = Button(text='← Назад', size_hint_x=0.3, on_press=self.go_to_profile)
        header.add_widget(back_btn)
        
        content = ScrollView()
        admin_content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=[20, 20])
        admin_content.bind(minimum_height=admin_content.setter('height'))
        
        admin_content.add_widget(Label(text='[b]Управление приложением:[/b]', markup=True))
        
        # Админские функции
        functions = [
            ("🔄 Сбросить статистику", self.reset_stats),
            ("🎨 Сменить тему", self.toggle_theme),
            ("👤 Изменить имя", self.change_name),
            ("📊 Системные логи", self.show_system_logs),
            ("🚀 Ускорение ИИ", self.boost_ai),
            ("🎯 Сбросить прогресс", self.reset_progress)
        ]
        
        for text, callback in functions:
            btn = Button(text=text, size_hint_y=None, height=50, on_press=callback)
            admin_content.add_widget(btn)
        
        content.add_widget(admin_content)
        layout.add_widget(header)
        layout.add_widget(content)
        
        self.add_widget(layout)
    
    def reset_stats(self, instance):
        self.config.data["user_profile"]["messages_sent"] = 0
        self.config.data["user_profile"]["chats_created"] = 0
        self.config.save_config()
        self.show_popup("Успех", "Статистика сброшена!")
    
    def toggle_theme(self, instance):
        self.config.data["theme"] = "light" if self.config.data["theme"] == "dark" else "dark"
        self.config.save_config()
        self.show_popup("Тема", "Тема изменена!")
    
    def change_name(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        name_input = TextInput(text=self.config.data["user_profile"]["name"])
        save_btn = Button(text='Сохранить', on_press=lambda x: self.save_name(name_input.text))
        
        content.add_widget(Label(text='Новое имя:'))
        content.add_widget(name_input)
        content.add_widget(save_btn)
        
        popup = Popup(title='Изменение имени', content=content, size_hint=(0.8, 0.4))
        popup.open()
    
    def save_name(self, new_name):
        self.config.data["user_profile"]["name"] = new_name
        self.config.save_config()
        self.show_popup("Успех", f"Имя изменено на: {new_name}")
    
    def show_system_logs(self, instance):
        logs = f"""
[b]Системные логи:[/b]

• Приложение: Chai Clone
• Пользователь: {self.config.data['user_profile']['name']}
• Уровень: {self.config.data['user_profile']['level']}
• Сообщений: {self.config.data['user_profile']['messages_sent']}
• Тема: {self.config.data['theme']}
• Персонаж ИИ: {self.config.data['ai_character']['name']}
• Статус: ✅ Активно
• Время: {datetime.now().strftime('%H:%M:%S')}
"""
        self.show_popup("📊 Системные логи", logs)
    
    def boost_ai(self, instance):
        self.config.data["user_profile"]["level"] += 5
        self.config.data["user_profile"]["xp"] = 100
        self.config.save_config()
        self.show_popup("Буст!", "ИИ ускорен! Уровень повышен!")
    
    def reset_progress(self, instance):
        self.config.data["user_profile"]["level"] = 1
        self.config.data["user_profile"]["xp"] = 0
        self.config.save_config()
        self.show_popup("Сброс", "Прогресс сброшен!")
    
    def go_to_profile(self, instance):
        self.manager.current = 'profile'
    
    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message, markup=True),
            size_hint=(0.8, 0.6)
        )
        popup.open()

# 🎯 ГЛАВНОЕ ПРИЛОЖЕНИЕ
class ChaiCloneApp(App):
    def build(self):
        self.title = "Chai Clone"
        
        # Создаем менеджер экранов
        sm = ScreenManager()
        sm.add_widget(ChatScreen(name='chat'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(AISettingsScreen(name='ai_settings'))
        sm.add_widget(AdminScreen(name='admin'))
        
        return sm

# 🚀 ЗАПУСК
if __name__ == '__main__':
    print("🚀 Запуск Chai Clone...")
    print("💬 ИИ чат приложение")
    print("👤 Стильный профиль как в Steam")
    print("🌙 Дневной/ночной режим")
    print("⚙️ Настройки ИИ и облачных сервисов")
    print("🔧 Админ-панель для создателя")
    print("=" * 50)
    
    ChaiCloneApp().run()
