
## 1. Project Structure

```text
data-analysis/
├── 01_datacleaning.ipynb
├── 02_plotting.ipynb
├── dashboard.py
├── requirements.txt
├── README.md
├── .gitignore
└── data/
	└── dataset files
```

### File Descriptions

| File or folder | Description |
| --- | --- |
| `01_datacleaning.ipynb` | Cleans and prepares the datasets for analysis. |
| `02_plotting.ipynb` | Performs exploratory analysis and creates visualisations. |
| `dashboard.py` | Contains the Streamlit dashboard and interactive visualisations. |
| `requirements.txt` | Lists the Python dependencies required to run the project. |
| `data/` | Stores the datasets used in the project, if permitted. |
| `README.md` | Provides project documentation and setup instructions. |
| `.gitignore` | Excludes specified files and folders from Git tracking. |

## 2. Technologies Used

- **Python** — Data analysis and processing.
- **Jupyter Notebook** — Interactive data cleaning and exploration.
- **Pandas** — Data manipulation and analysis.
- **Matplotlib / Plotly** — Data visualisation.
- **Streamlit** — Interactive dashboard development.
- **Git and GitHub** — Version control and team collaboration.

## 3. Getting Started

### Prerequisites

Install Python and Git before getting started.

### Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

Replace `<repository-url>` with the GitHub repository URL.

### Set Up a Virtual Environment

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

### Run the Jupyter Notebooks

```bash
jupyter notebook
```

Open the notebooks in the project directory to explore the data cleaning and visualisation workflow.

### Run the Streamlit Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open in your default browser, or the terminal will display a local URL that you can open manually.

## 4. Team Collaboration

This project uses GitHub for version control and collaboration. Team members should:

1. Pull the latest changes before starting work.
2. Create a separate branch when developing a new feature.
3. Commit changes with clear and descriptive messages.
4. Push changes to GitHub.
5. Review and merge changes through pull requests where appropriate.

Example commands:

```bash
git pull
git add .
git commit -m "Describe your changes"
git push
```

Avoid committing temporary files, virtual environments, credentials, or datasets that are restricted from sharing.

## 5. Data Management

The project may use Excel datasets as input for data cleaning, analysis, and visualisation. Before sharing datasets through GitHub, confirm that they can be redistributed and that their file sizes are appropriate for the repository.

If processed datasets are generated during analysis, document their format and location so that all team members can reproduce the workflow.

## 6. Project Status

**Current stage:** Data cleaning and visualisation.  
**Planned development:** Interactive dashboard using Streamlit.

Update this section as the project progresses.

