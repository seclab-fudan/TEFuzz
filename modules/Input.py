class Input:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_fuzz_char_1() -> list:
        fuzz_char_1 = [chr(i) for i in range(0, 127)]
        return fuzz_char_1

    @staticmethod
    def get_close_char() -> list:
        close_char = [
            '*/',
            '//\na',
            "')",
            "\")",
            "###",
            "\"\"",
            "''"
        ]
        return close_char

    @staticmethod
    def get_format_char() -> list:
        format_char = [
            '%.2f',
            '%d',
            '%s',
            '%.3e'
        ]
        return format_char

    @staticmethod
    def get_filename_input() -> list:
        filename = [
            'test.tpl',
            'test.conf',
            'test.html'
        ]
        return filename



