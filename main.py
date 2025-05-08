# main.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from readiness_assessment import ReadinessAssessment
from trimp_evaluation import TrimpEvaluation
from mental_assessment import MentalAssessment

class SintoniaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sintonia - Análise de Treinamento")
        self.root.geometry("600x500")

        # Set up the main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.setup_main_menu()

    def setup_main_menu(self):
        # Clear the frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Title
        ttk.Label(self.main_frame, text="Sintonia", font=("Arial", 24, "bold")).pack(pady=10)
        ttk.Label(self.main_frame, text="Análise de Treinamento", font=("Arial", 16)).pack(pady=5)

        # Menu buttons
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=30)

        # Readiness Assessment button
        ttk.Button(btn_frame, text="Avaliação de Prontidão", 
                  command=self.open_readiness_assessment,
                  width=30).pack(pady=10)

        # TRIMP Evaluation button
        ttk.Button(btn_frame, text="Avaliação de TRIMP", 
                  command=self.open_trimp_evaluation,
                  width=30).pack(pady=10)

        # Mental Assessment button (new)
        ttk.Button(btn_frame, text="Avaliação Mental", 
                  command=self.open_mental_assessment,
                  width=30).pack(pady=10)

        # Exit button
        ttk.Button(self.main_frame, text="Sair", 
                  command=self.root.quit,
                  width=15).pack(pady=20)

    def open_readiness_assessment(self):
        ReadinessAssessment(self.root, self.setup_main_menu)

    def open_trimp_evaluation(self):
        TrimpEvaluation(self.root, self.setup_main_menu)

    def open_mental_assessment(self):
        MentalAssessment(self.root, self.setup_main_menu)

def main():
    root = tk.Tk()
    app = SintoniaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
