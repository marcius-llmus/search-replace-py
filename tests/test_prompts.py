import unittest

from search_replace.prompts import (
    EditBlockFencedPrompts,
    EditBlockPrompts,
    EditorEditBlockPrompts,
    build_messages,
)


class TestBuildMessages(unittest.TestCase):
    def test_first_message_is_system(self):
        messages = build_messages(EditBlockPrompts)
        self.assertEqual(messages[0]["role"], "system")

    def test_system_contains_search_replace_instructions(self):
        messages = build_messages(EditBlockPrompts)
        system = messages[0]["content"]
        self.assertIn("SEARCH/REPLACE", system)

    def test_system_reminder_is_appended(self):
        messages = build_messages(EditBlockPrompts)
        system = messages[0]["content"]
        self.assertIn("SEARCH/REPLACE block* Rules", system)

    def test_fence_placeholder_expanded_in_system(self):
        fence = ("```", "```")
        messages = build_messages(EditBlockPrompts, fence=fence)
        system = messages[0]["content"]
        self.assertNotIn("{fence[0]}", system)
        self.assertNotIn("{fence[1]}", system)

    def test_fence_placeholder_expanded_in_examples(self):
        fence = ("```", "```")
        messages = build_messages(EditBlockPrompts, fence=fence)
        for msg in messages[1:]:
            self.assertNotIn("{fence[0]}", msg["content"])
            self.assertNotIn("{fence[1]}", msg["content"])

    def test_example_messages_alternate_user_assistant(self):
        messages = build_messages(EditBlockPrompts)
        roles = [m["role"] for m in messages[1:]]
        for i, role in enumerate(roles):
            expected = "user" if i % 2 == 0 else "assistant"
            self.assertEqual(role, expected)

    def test_editor_variant_has_no_shell_sections(self):
        messages = build_messages(EditorEditBlockPrompts)
        system = messages[0]["content"]
        self.assertNotIn("shell command", system.lower())

    def test_fenced_variant_filename_inside_fence_in_examples(self):
        fence = ("```", "```")
        messages = build_messages(EditBlockFencedPrompts, fence=fence)
        assistant_msgs = [m["content"] for m in messages if m["role"] == "assistant"]
        self.assertTrue(any("mathweb/flask/app.py" in m for m in assistant_msgs))

    def test_result_is_extendable_for_llm_call(self):
        messages = build_messages(EditBlockPrompts, fence=("```", "```"))
        messages.append({"role": "user", "content": "Add a docstring to foo()"})
        self.assertEqual(messages[-1]["role"], "user")
        self.assertGreater(len(messages), 1)
