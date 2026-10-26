"""Chat with the help desk in the terminal. Run: python -m scripts.cli_chat"""
from app.rag.chain import HelpDesk

if __name__ == "__main__":
    desk = HelpDesk()
    print("Help desk ready. Ctrl+C to quit.\n")
    while True:
        result = desk.ask(input("You: "))
        print("Bot:", result["answer"])
        if result["sources"]:
            print("     Sources:", ", ".join(result["sources"]))
        print()
