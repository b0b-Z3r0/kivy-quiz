import random
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.animation import Animation
from kivy.clock import Clock
import pygame

pygame.init()

# Load sound effects
correct_sound = pygame.mixer.Sound("correct.wav")
wrong_sound = pygame.mixer.Sound("wrong.wav")

def generate_question(operation, level):
    min_val = 10 ** (level - 1)
    max_val = (10 ** level) - 1

    while True:
        a = random.randint(min_val, max_val)
        b = random.randint(min_val, max_val if operation != "÷" else max_val // 2)

        if operation == "+":
            answer = a + b
        elif operation == "-":
            if a < b:
                a, b = b, a
            answer = a - b
        elif operation == "×":
            answer = a * b
        elif operation == "÷":
            if b == 0:
                continue
            a = a * b  # Ensure divisible
            answer = a // b

        return a, b, answer

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        for op in ["+", "-", "×", "÷"]:
            btn = Button(text=f"{op} Practice")
            btn.bind(on_release=lambda b, o=op: self.select_operation(o))
            layout.add_widget(btn)
        self.add_widget(layout)

    def select_operation(self, operation):
        self.manager.current = 'difficulty'
        self.manager.get_screen('difficulty').selected_operation = operation

class DifficultyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        for level in range(1, 4):
            btn = Button(text=f"{level}-digit numbers")
            btn.bind(on_release=lambda b, l=level: self.start_quiz(l))
            layout.add_widget(btn)

        mastery_btn = Button(text="Mastery Mode")
        mastery_btn.bind(on_release=lambda b: self.start_quiz(1, mastery=True))
        layout.add_widget(mastery_btn)

        back = Button(text="Back to Menu")
        back.bind(on_release=lambda b: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(back)

        self.layout = layout
        self.add_widget(layout)
        self.selected_operation = None

    def start_quiz(self, level, mastery=False):
        quiz_screen = self.manager.get_screen('quiz')
        quiz_screen.start_quiz(self.selected_operation, level, mastery)
        self.manager.current = 'quiz'

class QuizScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.question_label = Label(font_size=32)
        self.input = TextInput(multiline=False, input_filter='int')
        self.feedback = Label()
        self.submit_btn = Button(text="Submit", on_release=self.check_answer)
        self.back_btn = Button(text="Back", on_release=self.back_to_menu)

        self.mastery_stop_btn = Button(text="Stop Mastery", on_release=self.stop_mastery)
        self.mastery_timer_label = Label(font_size=18)

        self.layout.add_widget(self.question_label)
        self.layout.add_widget(self.input)
        self.layout.add_widget(self.submit_btn)
        self.layout.add_widget(self.feedback)
        self.layout.add_widget(self.mastery_timer_label)
        self.layout.add_widget(self.mastery_stop_btn)
        self.layout.add_widget(self.back_btn)
        self.add_widget(self.layout)

        self.correct_streak = 0
        self.mastery = False
        self.start_time = 0

    def start_quiz(self, operation, level, mastery=False):
        self.operation = operation
        self.level = level
        self.mastery = mastery
        self.correct_streak = 0
        self.mastery_timer_label.text = ""
        self.feedback.text = ""
        self.mastery_stop_btn.opacity = 1 if mastery else 0
        self.mastery_stop_btn.disabled = not mastery
        self.start_time = time.time() if mastery else 0
        self.next_question()

    def next_question(self):
        self.a, self.b, self.answer = generate_question(self.operation, self.level)
        self.question_label.text = f"{self.a} {self.operation} {self.b} = ?"
        self.input.text = ""
        self.feedback.color = (1, 1, 1, 1)  # Reset color

    def check_answer(self, instance):
        try:
            user_answer = int(self.input.text)
            if user_answer == self.answer:
                self.feedback.text = "✅ Correct!"
                correct_sound.play()
                self.correct_streak += 1
                self.animate_feedback((0, 1, 0, 1))  # Green
            else:
                self.feedback.text = f"❌ Wrong! Answer: {self.answer}"
                wrong_sound.play()
                self.correct_streak = 0
                self.animate_feedback((1, 0, 0, 1))  # Red

            if self.correct_streak == 10 and not self.mastery:
                self.feedback.text = "🎉 Level up!"
                self.level += 1
                self.correct_streak = 0

            Clock.schedule_once(lambda dt: self.next_question(), 1.0)
        except ValueError:
            self.feedback.text = "Please enter a valid number."

    def animate_feedback(self, color):
        anim = Animation(color=color, duration=0.3) + Animation(color=(1, 1, 1, 1), duration=0.3)
        anim.start(self.feedback)

    def stop_mastery(self, instance):
        end_time = time.time()
        elapsed = end_time - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        self.mastery_timer_label.text = f"⏱️ Finished in {minutes} min {seconds} sec"
        self.mastery_stop_btn.disabled = True
        self.mastery_stop_btn.opacity = 0

    def back_to_menu(self, instance):
        self.manager.current = 'menu'

class QuizApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(DifficultyScreen(name='difficulty'))
        sm.add_widget(QuizScreen(name='quiz'))
        return sm

if __name__ == '__main__':
    QuizApp().run()
