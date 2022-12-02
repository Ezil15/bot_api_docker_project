import unittest
from dialogue_logic import *


class TestAnswers(unittest.TestCase):
    def setUp(self):
        self.test_dialogue_from = DialogueNode(0, "First Node")
        self.test_dialogue_yes = DialogueNode(1, "Yes Node")
        self.test_dialogue_no = DialogueNode(2, "No Node")

        self.answer_yes = Answer(0)
        yes_vars = ["да", "конечно", "пожалуй", "ага"]
        for var in yes_vars:
            self.answer_yes.add_variant(var)

        self.answer_no = Answer(1)
        no_vars = ["нет", "найн", "нет конечно", "ноуп"]
        for var in no_vars:
            self.answer_no.add_variant(var)

        self.test_dialogue_from.add_transition(self.answer_yes, self.test_dialogue_yes.id)
        self.test_dialogue_from.add_transition(self.answer_no, self.test_dialogue_no.id)

    def test_yes_answer(self):
        variants_to_check = ["да", "Да конечно", "конечно", "ага", "пожалуй"]
        expected_node = self.test_dialogue_yes
        for var in variants_to_check:
            status, selected_transition = self.test_dialogue_from.get_possible_transition(var)

            self.assertTrue(status)
            self.assertEqual(selected_transition.dialogue_to, expected_node.id)

    def test_no_answer(self):
        variants_to_check = ["нет", "НАЙН", "нет, конечно", "ноуп"]
        expected_node = self.test_dialogue_no
        for var in variants_to_check:
            status, selected_transition = self.test_dialogue_from.get_possible_transition(var)

            self.assertTrue(status)
            self.assertEqual(selected_transition.dialogue_to, expected_node.id)
    def test_error(self):
        variants_to_check = ["что", "кто", "котик"]
        for var in variants_to_check:
            status, selected_transition = self.test_dialogue_from.get_possible_transition(var)

            self.assertFalse(status)

if __name__ == "__main__":
  unittest.main()