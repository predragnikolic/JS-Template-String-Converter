import sublime
import sublime_plugin


class ConvertToTemplateString(sublime_plugin.TextCommand):
    """ This command is guaranteed to executed when { is pressed """
    def run(self, edit):
        sel = self.view.sel()
        if not sel:
            return
        point = sel[0].b
        if not in_supported_file(self.view, point):
            return None
        regular_string_region = get_regular_string_region(self.view, point)
        if not regular_string_region:
            return
        scan_region = self.view.substr(regular_string_region)
        # the user could typed $ or {
        if "${" not in scan_region:
            return
        first_quote = regular_string_region.begin()
        last_quote = regular_string_region.end() - 1
        are_quotes = is_regular_quote(self.view.substr(first_quote)) and is_regular_quote(self.view.substr(last_quote))
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


def is_jsx_attribute(view: sublime.View, point: int) -> bool:
    return view.match_selector(point, "meta.jsx meta.tag.attributes")


def is_jsx_attribute_wrapped_with_curly_brackets(view: sublime.View, point: int) -> bool:
    return view.match_selector(point, "meta.jsx meta.tag.attributes meta.interpolation meta.string string.quoted")


def is_regular_quote(char: str) -> bool:
    return char in ["'", '"']


def in_supported_file(view: sublime.View, point: int) -> bool:
    return view.match_selector(point, "source.js | source.jsx | source.ts | source.tsx | text.html.ngx | text.html.svelte | text.html.vue")


def get_regular_string_region(view: sublime.View, point: int):
    return view.expand_to_scope(point, "string.quoted.single | string.quoted.double")
