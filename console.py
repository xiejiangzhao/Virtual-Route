from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.contrib.completers import WordCompleter


def main() -> None:
    history = InMemoryHistory()
    completer = WordCompleter(["exit", "history"], ignore_case=True)

    while True:
        text = prompt("Route> ", history=history, auto_suggest=AutoSuggestFromHistory(), completer=completer)
        if text.lower() == "exit":
            break
        elif text.lower() == "history":
            for line in history.strings:
                print(line)
        print(f"You entered: {text}")
    print("Goodbye!")


if __name__ == "__main__":
    main()
