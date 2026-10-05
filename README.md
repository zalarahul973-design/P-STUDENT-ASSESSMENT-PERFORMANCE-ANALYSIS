# 🎓 Student Assessment Performance — Streamlit Dashboard

This project converts the Student Assessment Performance Power BI dashboard into an interactive **Streamlit web application**.

## Features
- KPI cards: Assessment Count, Average Score, Pass Rate, Average Attendance
- Batch, Department and Month filters
- Average score by department
- Pass rate by department
- Monthly average score trend
- Course performance
- Batch performance
- Interactive assessment table
- Filtered CSV download

## Files
- `app.py` — Streamlit dashboard
- `assessments.csv` — assessment data
- `courses.csv` — course lookup data
- `requirements.txt` — Python packages

## Run locally

Open PowerShell/Terminal inside this folder:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal, normally:
`http://localhost:8501`

## Project Data
The dashboard joins `assessments` with `courses` using `course_id`.

**Pass rule:** Score >= 50 = Pass; Score < 50 = Fail.

## Portfolio
This Streamlit version can be used as a portfolio/demo project alongside the original Power BI dashboard.
