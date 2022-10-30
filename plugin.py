from typing import List, Optional
import sublime
import sublime_plugin


class TextChangeListener(sublime_plugin.TextChangeListener):
    def on_text_changed(self, changes: List[sublime.TextChange]):
        if not self.buffer:
            return
        view = self.buffer.primary_view()
        if not view:
            return
        for c in changes:
            if c.str in ['{', "{}"]:
                sublime.set_timeout(lambda: view.run_command('convert_to_template_string'), 0)


class ConvertToTemplateString(sublime_plugin.TextCommand):
    """ This command is guaranteed to executed when { is pressed """
    def run(self, edit):
        point = get_cursor_point(self.view)
        if not point:
            return
        in_supported_file = self.view.match_selector(point, "source.js | source.jsx | source.ts | source.tsx | text.html.ngx | text.html.svelte | text.html.vue")
        if not in_supported_file:
            return None
        string_region = self.view.expand_to_scope(point, "string.quoted.single | string.quoted.double")
        if not string_region:
            return
        prev_char = self.view.substr(sublime.Region(point-2, point))
        if prev_char != "${":
            return
        first_quote = string_region.begin()
        last_quote = string_region.end() - 1
        # replace quotes
        if is_jsx_attribute(self.view, point) and not is_jsx_attribute_wrapped_with_curly_brackets(self.view, point):
            # insert surrounding curly brackets
            self.view.replace(
                edit, sublime.Region(last_quote, last_quote + 1), '`}')
            self.view.replace(
                edit, sublime.Region(first_quote, first_quote + 1), '{`')
            return
        self.view.replace(
            edit, sublime.Region(last_quote, last_quote + 1), '`')
        self.view.replace(
            edit, sublime.Region(first_quote, first_quote + 1), '`')


def is_jsx_attribute(view: sublime.View, point: int) -> bool:
    return view.match_selector(point, "meta.jsx meta.tag.attributes")


def is_jsx_attribute_wrapped_with_curly_brackets(view: sublime.View, point: int) -> bool:
    return view.match_selector(point, "meta.jsx meta.tag.attributes meta.interpolation")


def get_cursor_point(view: sublime.View) -> Optional[int]:
    sel = view.sel()
    if not sel:
        return
    return sel[0].b


def is_quote(chars: List[str]) -> bool:
    for c in chars:
        if c not in ["'", '"']:
            return False
    return True
