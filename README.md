
# Sintonia - Mental Assessment Integration

## Files Overview
- `mental_assessment.py`: New module for mental assessments (anxiety, stress, mental fatigue)
- `main.py`: Modified main application file with mental assessment integration

## Installation Instructions

1. Clone your existing Sintonia repository (if you haven't already):
   ```
   git clone https://github.com/your-username/sintonia.git
   cd sintonia
   ```

2. Add the new files to your repository:
   - Place `mental_assessment.py` in the root directory of your project
   - Replace your existing `main.py` with the new version

3. Create a data directory for storing assessment results:
   ```
   mkdir -p data
   ```

4. Commit and push the changes:
   ```
   git add mental_assessment.py main.py
   git commit -m "Add mental assessment functionality"
   git push origin main
   ```

## Usage
1. Run the application:
   ```
   python main.py
   ```

2. From the main menu, select "Avaliação Mental"

3. Choose one of the three assessments:
   - Ansiedade (GAD-7)
   - Estresse (PSS-10)
   - Fadiga Mental (MFS)

4. Complete the questionnaire and view your results

## Features
- Three validated mental assessment questionnaires
- Automatic scoring and interpretation
- Personalized recommendations based on results
- Results saved to JSON file for future reference
