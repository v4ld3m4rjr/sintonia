
# mental_assessment.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class MentalAssessment:
    def __init__(self, master, return_callback):
        self.master = master
        self.return_callback = return_callback
        self.current_assessment = None
        self.results = {}

        # Define questionnaires
        self.questionnaires = {
            "anxiety": {
                "title": "Avaliação de Ansiedade (GAD-7)",
                "questions": [
                    "Sentir-se nervoso, ansioso ou muito tenso",
                    "Não ser capaz de impedir ou de controlar as preocupações",
                    "Preocupar-se muito com diversas coisas",
                    "Dificuldade para relaxar",
                    "Ficar tão agitado que se torna difícil permanecer sentado",
                    "Ficar facilmente aborrecido ou irritado",
                    "Sentir medo como se algo terrível fosse acontecer"
                ],
                "options": ["Nunca", "Vários dias", "Mais da metade dos dias", "Quase todos os dias"],
                "scores": [0, 1, 2, 3]
            },
            "stress": {
                "title": "Escala de Estresse Percebido (PSS-10)",
                "questions": [
                    "Você tem ficado triste por causa de algo que aconteceu inesperadamente?",
                    "Você tem se sentido incapaz de controlar as coisas importantes em sua vida?",
                    "Você tem se sentido nervoso e estressado?",
                    "Você tem tratado com sucesso dos problemas difíceis da vida?",
                    "Você tem sentido que está lidando bem com as mudanças importantes que estão ocorrendo em sua vida?",
                    "Você tem se sentido confiante na sua habilidade de resolver problemas pessoais?",
                    "Você tem sentido que as coisas estão acontecendo de acordo com a sua vontade?",
                    "Você tem achado que não conseguiria lidar com todas as coisas que você tem que fazer?",
                    "Você tem conseguido controlar as irritações em sua vida?",
                    "Você tem sentido que as coisas estão sob o seu controle?"
                ],
                "options": ["Nunca", "Quase nunca", "Às vezes", "Frequentemente", "Muito frequentemente"],
                "scores": [0, 1, 2, 3, 4],
                "reverse_items": [3, 4, 5, 6, 9]  # 0-indexed items that need reverse scoring
            },
            "mental_fatigue": {
                "title": "Escala de Fadiga Mental (MFS)",
                "questions": [
                    "Fadiga em geral",
                    "Necessidade de mais sono/descanso",
                    "Sonolência/torpor",
                    "Irritabilidade",
                    "Sensibilidade ao estresse",
                    "Diminuição da concentração",
                    "Diminuição da memória",
                    "Tempo de recuperação prolongado",
                    "Diminuição da tolerância a ruídos",
                    "Diminuição da tolerância à luz",
                    "Diminuição da tolerância a situações sociais",
                    "Diminuição da iniciativa/capacidade de começar atividades",
                    "Diminuição da resistência/capacidade de lidar com situações estressantes",
                    "Diminuição da capacidade de realizar várias tarefas simultaneamente"
                ],
                "options": ["Nunca presente", "Presente, mas não perturbador", "Presente, perturbador mas não severo", "Presente e severo"],
                "scores": [0, 1, 2, 3]
            }
        }

        self.setup_ui()

    def setup_ui(self):
        # Clear the window
        for widget in self.master.winfo_children():
            widget.destroy()

        # Set up the main frame
        self.main_frame = ttk.Frame(self.master, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(self.main_frame, text="Avaliação Mental", font=("Arial", 16, "bold")).pack(pady=10)

        # Description
        description = "Selecione uma avaliação para começar:"
        ttk.Label(self.main_frame, text=description, wraplength=400).pack(pady=10)

        # Buttons for each assessment
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Ansiedade (GAD-7)", 
                  command=lambda: self.start_assessment("anxiety")).pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Estresse (PSS-10)", 
                  command=lambda: self.start_assessment("stress")).pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Fadiga Mental (MFS)", 
                  command=lambda: self.start_assessment("mental_fatigue")).pack(fill=tk.X, pady=5)

        # Return button
        ttk.Button(self.main_frame, text="Voltar", command=self.return_callback).pack(pady=20)

    def start_assessment(self, assessment_type):
        self.current_assessment = assessment_type
        self.current_question = 0
        self.answers = []

        # Clear the window
        for widget in self.master.winfo_children():
            widget.destroy()

        # Set up the assessment frame
        self.assessment_frame = ttk.Frame(self.master, padding="20")
        self.assessment_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(self.assessment_frame, 
                 text=self.questionnaires[assessment_type]["title"], 
                 font=("Arial", 14, "bold")).pack(pady=10)

        # Instructions
        instructions = "Nas últimas 2 semanas, com que frequência você foi incomodado pelos seguintes problemas?"
        ttk.Label(self.assessment_frame, text=instructions, wraplength=400).pack(pady=10)

        # Display the first question
        self.display_question()

    def display_question(self):
        # Clear previous question widgets
        for widget in self.assessment_frame.winfo_children()[2:]:
            widget.destroy()

        questionnaire = self.questionnaires[self.current_assessment]

        # Question number and text
        question_text = f"Questão {self.current_question + 1}/{len(questionnaire['questions'])}: {questionnaire['questions'][self.current_question]}"
        ttk.Label(self.assessment_frame, text=question_text, wraplength=400, font=("Arial", 11)).pack(pady=15)

        # Options
        self.selected_option = tk.IntVar()
        options_frame = ttk.Frame(self.assessment_frame)
        options_frame.pack(pady=10)

        for i, option in enumerate(questionnaire["options"]):
            ttk.Radiobutton(options_frame, 
                           text=option, 
                           variable=self.selected_option, 
                           value=i).pack(anchor=tk.W, pady=3)

        # Navigation buttons
        nav_frame = ttk.Frame(self.assessment_frame)
        nav_frame.pack(pady=20, fill=tk.X)

        if self.current_question > 0:
            ttk.Button(nav_frame, text="Anterior", 
                      command=self.previous_question).pack(side=tk.LEFT, padx=5)

        ttk.Button(nav_frame, text="Próximo" if self.current_question < len(questionnaire["questions"]) - 1 else "Finalizar", 
                  command=self.next_question).pack(side=tk.RIGHT, padx=5)

    def previous_question(self):
        self.answers[self.current_question] = self.selected_option.get()
        self.current_question -= 1
        self.selected_option.set(self.answers[self.current_question])
        self.display_question()

    def next_question(self):
        # Save the current answer
        if not hasattr(self.selected_option, 'get') or self.selected_option.get() not in range(len(self.questionnaires[self.current_assessment]["options"])):
            messagebox.showwarning("Resposta necessária", "Por favor, selecione uma opção antes de continuar.")
            return

        if len(self.answers) <= self.current_question:
            self.answers.append(self.selected_option.get())
        else:
            self.answers[self.current_question] = self.selected_option.get()

        # Move to next question or finish
        if self.current_question < len(self.questionnaires[self.current_assessment]["questions"]) - 1:
            self.current_question += 1
            # If we already have an answer for this question, select it
            if len(self.answers) > self.current_question:
                self.selected_option.set(self.answers[self.current_question])
            else:
                self.selected_option.set(-1)  # No option selected
            self.display_question()
        else:
            self.calculate_results()

    def calculate_results(self):
        questionnaire = self.questionnaires[self.current_assessment]
        scores = questionnaire["scores"]

        # Calculate total score
        total_score = 0
        for i, answer_index in enumerate(self.answers):
            score = scores[answer_index]

            # Handle reverse scoring for PSS-10
            if self.current_assessment == "stress" and i in questionnaire.get("reverse_items", []):
                score = 4 - score  # Reverse the score (0->4, 1->3, 2->2, 3->1, 4->0)

            total_score += score

        # Interpret the score
        interpretation = self.interpret_score(self.current_assessment, total_score)

        # Save the result
        self.results[self.current_assessment] = {
            "score": total_score,
            "interpretation": interpretation,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save to file
        self.save_results()

        # Display results
        self.display_results(total_score, interpretation)

    def interpret_score(self, assessment_type, score):
        if assessment_type == "anxiety":
            if score < 5:
                return "Mínima"
            elif score < 10:
                return "Leve"
            elif score < 15:
                return "Moderada"
            else:
                return "Severa"

        elif assessment_type == "stress":
            if score < 14:
                return "Baixo"
            elif score < 27:
                return "Moderado"
            else:
                return "Alto"

        elif assessment_type == "mental_fatigue":
            if score < 10.5:
                return "Baixa"
            elif score < 21:
                return "Moderada"
            else:
                return "Alta"

        return "Não interpretado"

    def display_results(self, score, interpretation):
        # Clear the window
        for widget in self.master.winfo_children():
            widget.destroy()

        # Set up the results frame
        results_frame = ttk.Frame(self.master, padding="20")
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(results_frame, 
                 text=f"Resultados: {self.questionnaires[self.current_assessment]['title']}", 
                 font=("Arial", 14, "bold")).pack(pady=10)

        # Score
        ttk.Label(results_frame, 
                 text=f"Pontuação total: {score}", 
                 font=("Arial", 12)).pack(pady=5)

        # Interpretation
        ttk.Label(results_frame, 
                 text=f"Interpretação: {interpretation}", 
                 font=("Arial", 12)).pack(pady=5)

        # Recommendations based on interpretation
        recommendations = self.get_recommendations(self.current_assessment, interpretation)

        ttk.Label(results_frame, text="Recomendações:", 
                 font=("Arial", 12, "bold")).pack(pady=10, anchor=tk.W)

        for rec in recommendations:
            ttk.Label(results_frame, text=f"• {rec}", 
                     wraplength=400, justify=tk.LEFT).pack(pady=2, anchor=tk.W)

        # Buttons
        btn_frame = ttk.Frame(results_frame)
        btn_frame.pack(pady=20, fill=tk.X)

        ttk.Button(btn_frame, text="Nova Avaliação", 
                  command=self.setup_ui).pack(side=tk.LEFT, padx=5)

        ttk.Button(btn_frame, text="Voltar ao Menu Principal", 
                  command=self.return_callback).pack(side=tk.RIGHT, padx=5)

    def get_recommendations(self, assessment_type, interpretation):
        recommendations = []

        if assessment_type == "anxiety":
            if interpretation in ["Mínima", "Leve"]:
                recommendations = [
                    "Pratique técnicas de respiração profunda diariamente",
                    "Mantenha uma rotina regular de exercícios físicos",
                    "Considere a prática de mindfulness ou meditação"
                ]
            else:  # Moderada ou Severa
                recommendations = [
                    "Considere consultar um profissional de saúde mental",
                    "Pratique técnicas de respiração e relaxamento regularmente",
                    "Estabeleça uma rotina de sono saudável",
                    "Limite o consumo de cafeína e álcool",
                    "Pratique exercícios físicos regularmente"
                ]

        elif assessment_type == "stress":
            if interpretation == "Baixo":
                recommendations = [
                    "Continue com suas práticas atuais de gerenciamento de estresse",
                    "Mantenha um equilíbrio saudável entre trabalho e vida pessoal",
                    "Pratique atividades que você goste regularmente"
                ]
            elif interpretation == "Moderado":
                recommendations = [
                    "Incorpore técnicas de relaxamento em sua rotina diária",
                    "Considere limitar o tempo em mídias sociais e notícias",
                    "Priorize o autocuidado e o descanso adequado",
                    "Pratique exercícios físicos regularmente"
                ]
            else:  # Alto
                recommendations = [
                    "Considere consultar um profissional de saúde mental",
                    "Identifique e tente reduzir as principais fontes de estresse",
                    "Pratique técnicas de relaxamento diariamente",
                    "Estabeleça limites claros entre trabalho e vida pessoal",
                    "Priorize o sono e a alimentação saudável"
                ]

        elif assessment_type == "mental_fatigue":
            if interpretation == "Baixa":
                recommendations = [
                    "Mantenha uma rotina regular de sono",
                    "Continue com pausas regulares durante atividades mentalmente exigentes",
                    "Pratique exercícios físicos regularmente"
                ]
            elif interpretation == "Moderada":
                recommendations = [
                    "Aumente a frequência de pausas durante o trabalho mental",
                    "Considere técnicas de gerenciamento de energia",
                    "Priorize o sono de qualidade",
                    "Limite o tempo de tela, especialmente antes de dormir"
                ]
            else:  # Alta
                recommendations = [
                    "Considere consultar um profissional de saúde",
                    "Implemente pausas frequentes e regulares durante atividades mentais",
                    "Pratique técnicas de recuperação cognitiva",
                    "Priorize o sono e o descanso adequado",
                    "Considere reduzir temporariamente a carga de trabalho mental"
                ]

        return recommendations

    def save_results(self):
        # Create directory if it doesn't exist
        if not os.path.exists("data"):
            os.makedirs("data")

        # Load existing data if available
        data_file = "data/mental_assessment_results.json"
        all_results = {}

        if os.path.exists(data_file):
            try:
                with open(data_file, 'r') as f:
                    all_results = json.load(f)
            except:
                all_results = {}

        # Update with new results
        if "results" not in all_results:
            all_results["results"] = {}

        all_results["results"][self.current_assessment] = self.results[self.current_assessment]

        # Save back to file
        with open(data_file, 'w') as f:
            json.dump(all_results, f, indent=4)
