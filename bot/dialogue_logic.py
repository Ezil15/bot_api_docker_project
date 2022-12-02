from __future__ import annotations
from db_manager import cursor as dbcur, db
import re


class Answer():
    """Класс описывающий возможный ответ пользователя на один из диалогов DialogueNode"""
    def __init__(self, id: int):
        self.id = id
        self.__variants: list[str] = []

    def add_variant(self,text: str):
        """Добавление возможного варианта ответа"""
        self.__variants.append(text)

    def check(self, text: str) -> int:
        """Функция возвращающая длинну самого подходящего варианта под переданный текст"""
        best_len = 0
        for var in self.__variants:
            clear_var = re.sub(r'[^\w\s]', '', var.lower())
            clear_text = re.sub(r'[^\w\s]', '', text.lower())
            if clear_var in clear_text and best_len < len(clear_var):
                best_len = len(clear_var)
        return best_len

class Transition():
    """Класс описывающий переход от определенного ответа к диалогу"""
    def __init__(self, answer: Answer, dialogue_from:int, dialogue_to: int):
        self.answer = answer
        self.dialogue_from = dialogue_from
        self.dialogue_to = dialogue_to

class DialogueNode():
    """Класс хранящий в себе информацию о диалоге, текст который будет выводить бот 
    и его возможные переходы к другим диалогам."""

    def __init__(self, id: int, text: str):
        self.id = id
        self.text = text
        self.transitions: list[Transition] = []
    
    def add_transition(self, answer: Answer, dialogue_to: int ):
        """Функция добавляющая возможный переход от текущего диалога DialogueNode к следующему, 
        в зависимости от ответа Answer"""
        self.transitions.append(Transition(answer, self.id, dialogue_to))
    
    def get_possible_transition(self,message) ->  tuple[bool, Transition]:
        """Функция возвращающая возможность перехода новому диалогу и сам Transition, исходя из пользовательского текста."""
        transitions_best = max(self.transitions, key = lambda t: t.answer.check(message))
        if transitions_best.answer.check(message) > 0:
            return True, transitions_best
        return False, None

class User():
    """Класс описывающий текущее состояние пользователя в цепочке диалога"""

    def __init__(self, id: int, dialogue_id: int):
        self.id = id
        self.dialogue_id = dialogue_id 

    def set_current_dialogue(self, dialogue: DialogueNode):
        """Изменяет текущий айди диалога на котором находится пользователь. Сохраняет значение в базу данных."""
        dbcur.execute(f"UPDATE users SET current_dialogue=%s WHERE id=%s LIMIT 1;",(dialogue.id,self.id))
        db.commit()
        self.dialogue_id = dialogue.id
        
class DialogueSystem():
    """Класс описывающий всю диалоговую систему бота."""
    
    def __init__(self):
        self.__answers: dict[int,Answer] = {}
        self.__dialogues: dict[int,DialogueNode] = {}
        self.__users: dict[int, User] = {}
        self.load_dialogue_chain()
        self.load_users()

    def load_dialogue_chain(self):
        """Функция загружающая всю цепочку диалогов из базы данных и сопоставляющая данные между собой."""
        dbcur.execute("SELECT * FROM answers")
        q_answers = dbcur.fetchall()
        for row in q_answers:
            if row[0] not in self.__answers:
                new_answer: Answer = Answer(row[0])
                new_answer.add_variant(row[1])
                self.__answers[row[0]] = new_answer
            else:
                self.__answers[row[0]].add_variant(row[1])

        dbcur.execute("SELECT * FROM dialogues")
        q_dialogues = dbcur.fetchall()
        for row in q_dialogues:
            self.__dialogues[row[0]] = DialogueNode(row[0],row[1])

        dbcur.execute("SELECT * FROM transitions")
        q_transitions = dbcur.fetchall()
        for row in q_transitions:
            answer: Answer = self.__answers[row[1]]
            dialogue_to: DialogueNode = self.__dialogues[row[2]]
            dialogue_to.add_transition(answer, row[3])


    def load_users(self):
        """Загрузка всех пользователей из базы данных"""
        dbcur.execute("SELECT * FROM users")
        q_users = dbcur.fetchall()
        for row in q_users:
            user: User = User(row[0], row[1])
            self.__users[row[0]] = user

    def add_user(self, id: int):
        """Добавление нового пользователя в базу данных"""
        if id not in self.__users:
            dbcur.execute("INSERT INTO users (id, current_dialogue) VALUES (%s, 0);",(id,))
            db.commit()
            user: User = User(id, 0)
            self.__users[id] = user
            return user
        
    def get_user(self, id: int):
        """Получение пользователя по его айди"""
        if id in self.__users:
            return self.__users[id]
    
    def get_dialogue(self,id: int):
        """Получение диалога по его айди"""
        if id in self.__dialogues:
            return self.__dialogues[id]

    def log_user_input(self, user_id: int, answer_id: int, sended_text: str, from_dialogue: int, to_dialogue: int):
        """Логирование переданного текста пользователем из системы диалога в базу данных"""
        dbcur.execute("INSERT INTO user_logs (user_id, answer_id, sended_text, from_dialogue, to_dialogue) VALUES (%s, %s, %s, %s, %s);",
            (user_id, answer_id, sended_text, from_dialogue, to_dialogue))
        db.commit()
                    


