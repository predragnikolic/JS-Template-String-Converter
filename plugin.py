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
            return
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
        # validate if the template string spams only one line
        first_row, _ = self.view.rowcol(first_quote)
        last_row, _ = self.view.rowcol(last_quote)
        if first_row != last_row:
            # to transform to a regular string, the template string must be on the same line
            # if it doesn't bail out
            return
        are_backticks = is_backtick([self.view.substr(first_quote), self.view.substr(last_quote)])
        if not are_backticks:
            return # sanity check, just to remove something that is not a quote bracket
        # replace quotes
        if is_jsx_attribute(self.view, point) and is_jsx_attribute_wrapped_with_curly_brackets(self.view, point):
            self.view.replace(
                edit, sublime.Region(last_quote, last_quote + 1), "'")
            self.view.replace(
                edit, sublime.Region(first_quote, first_quote + 1), "'")
            curly_bracket_region = get_surrounding_curly_brackets_region(self.view, point)
            if not curly_bracket_region:
                return
            first_bracket = curly_bracket_region.begin()
            last_bracket = curly_bracket_region.end() - 1
            are_curly_brackets = is_curly_bracket([self.view.substr(first_bracket), self.view.substr(last_bracket)])
            if not are_curly_brackets:
                return  # sanity check, just to remove something that is not a curly bracket
            self.view.erase(
                edit, sublime.Region(last_bracket, last_bracket + 1))
            self.view.erase(
                edit, sublime.Region(first_bracket, first_bracket + 1))
            return
        self.view.replace(
            edit, sublime.Region(last_quote, last_quote + 1), "'")
        self.view.replace(
            edit, sublime.Region(first_quote, first_quote + 1), "'")


def is_jsx_attribute(view: sublime.View, point: int) -> bool:
    return view.match_selector(point, "meta.jsx meta.tag.attributes")


def is_jsx_attribute_wrapped_with_curly_brackets(view: sublime.View, point: int) -> bool:
    return view.match_selector(point, "meta.jsx meta.tag.attributes meta.interpolation meta.string string.quoted")


def get_surrounding_curly_brackets_region(view: sublime.View, point: int) -> Optional[sublime.Region]:
    higher_specificity = view.expand_to_scope(point, "meta.jsx meta.tag.attributes meta.interpolation source.js.embedded meta.jsx meta.tag.attributes meta.interpolation")
    if higher_specificity:
        # handles this case, where Dashboard is nested in with {}
        # let Route = <Route element={<Dashboard type={`test ${}`} />}></Route>
        return higher_specificity
    # handles this case
    # let div = <div class={'test ${}'}></div>
    return view.expand_to_scope(point, "meta.jsx meta.tag.attributes meta.interpolation")


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


def is_curly_bracket(chars: List[str]) -> bool:
    for c in chars:
        if c not in ["{", '}']:
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