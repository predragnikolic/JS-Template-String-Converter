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
            is_delete = not c.str
            if c.str in ['$', '{', "{}"]:
                sublime.set_timeout(lambda: view.run_command('convert_to_template_string'), 0)
            if is_delete:
                sublime.set_timeout(lambda: view.run_command('convert_to_regular_string'), 0)


class ConvertToTemplateString(sublime_plugin.TextCommand):
    """ This command is guaranteed to executed when { is pressed """
    def run(self, edit):
        point = get_cursor_point(self.view)
        if not point:
            return
        if not in_supported_file(self.view, point):
            return None
        regular_string_region = get_regular_string_region(self.view, point)
        if not regular_string_region:
            return
        scan_region = self.view.substr(sublime.Region(point-2, point+2))
        # the user could typed $ or {
        if "${" not in scan_region:
            return
        first_quote = regular_string_region.begin()
        last_quote = regular_string_region.end() - 1
        are_quotes = is_regular_quote([self.view.substr(first_quote), self.view.substr(last_quote)])
        if not are_quotes:
            return # sanity check, just to 100% make sure we are replacing quotes
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


class ConvertToRegularString(sublime_plugin.TextCommand):
    def run(self, edit):
        point = get_cursor_point(self.view)
        if not point:
            return
        if not in_supported_file(self.view, point):
            return None
        backtick_string_region = get_backtick_string_region(self.view, point)
        if not backtick_string_region:
            return
        # if there are ${ that means it is still a template string
        if '${' in self.view.substr(backtick_string_region):
            return
        # else transform the template string to a regular string
        first_quote = backtick_string_region.begin()
        last_quote = backtick_string_region.end() - 1
        # to transform to a regular string, the template string must be on the same line
        first_row, _ = self.view.rowcol(first_quote)
        last_row, _ = self.view.rowcol(last_quote)
        if first_row != last_row:
            return
        are_backticks = is_backtick([self.view.substr(first_quote), self.view.substr(last_quote)])
        if not are_backticks:
            return  # sanity check, just to 100% make sure we are replacing backticks
        self.view.replace(
            edit, sublime.Region(last_quote, last_quote + 1), "'")
        self.view.replace(
            edit, sublime.Region(first_quote, first_quote + 1), "'")


def is_jsx_attribute(view: sublime.View, point: int) -> bool:
    return view.match_selector(point, "meta.jsx meta.tag.attributes")


def is_jsx_attribute_wrapped_with_curly_brackets(view: sublime.View, point: int) -> bool:
    return view.match_selector(point, "meta.jsx meta.tag.attributes meta.interpolation meta.string string.quoted")


def get_cursor_point(view: sublime.View) -> Optional[int]:
    sel = view.sel()
    if not sel:
        return
    return sel[0].b


def is_regular_quote(chars: List[str]) -> bool:
    for c in chars:
        if c not in ["'", '"']:
            return False
    return True


def is_backtick(chars: List[str]) -> bool:
    return "`" in chars


def in_supported_file(view: sublime.View, point: int) -> bool:
    return view.match_selector(point, "source.js | source.jsx | source.ts | source.tsx | text.html.ngx | text.html.svelte | text.html.vue")


def get_regular_string_region(view: sublime.View, point: int) -> Optional[sublime.Region]:
    return view.expand_to_scope(point, "string.quoted.single | string.quoted.double")


def get_backtick_string_region(view: sublime.View, point: int) -> Optional[sublime.Region]:
    return view.expand_to_scope(point, "string.quoted.other")