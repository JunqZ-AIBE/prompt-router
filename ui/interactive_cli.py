import sys

class InteractiveCLI:
    def __init__(self):
        self.prompt = ""
        self.llm = None
        self.optimization_enabled = False
        self.output = ""
        self.history = []

    def run(self):
        while True:
            self.show_main_menu()
            choice = input("Escolha uma opção: ").strip()
            if choice == "1":
                self.insert_prompt()
            elif choice == "2":
                self.select_llm()
            elif choice == "3":
                self.toggle_optimization()
            elif choice == "4":
                self.view_output()
            elif choice == "5":
                self.export_result()
            elif choice == "6":
                self.show_history()
            elif choice == "0":
                print("Saindo...")
                break
            else:
                print("Opção inválida. Tente novamente.")

    def show_main_menu(self):
        print("\n=== Prompt Router CLI ===")
        print("1. Inserir prompt cru")
        print("2. Selecionar LLM de destino")
        print("3. Ativar/desativar otimização")
        print("4. Visualizar saída otimizada")
        print("5. Exportar resultado")
        print("6. Histórico de prompts")
        print("0. Sair")

    def insert_prompt(self):
        print("\n[Inserir Prompt]")
        # Placeholder
        pass

    def select_llm(self):
        print("\n[Selecionar LLM]")
        # Placeholder
        pass

    def toggle_optimization(self):
        print("\n[Ativar/Desativar Otimização]")
        # Placeholder
        pass

    def view_output(self):
        print("\n[Visualizar Saída]")
        # Placeholder
        pass

    def export_result(self):
        print("\n[Exportar Resultado]")
        # Placeholder
        pass

    def show_history(self):
        print("\n[Histórico de Prompts]")
        # Placeholder
        pass

if __name__ == "__main__":
    cli = InteractiveCLI()
    cli.run()
