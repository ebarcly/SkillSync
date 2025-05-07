import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
import re # For later use, for more advance parsing

load_dotenv()

# Sample data for projects
projects = [
    {
        'id': 1,
        'name': 'Personal Website v1',
        'description': 'My first personal website built to showcase my basic HTML and CSS skills.',
        'link': 'https://example.com/websitev1',
        'skills': ['HTML', 'CSS', 'Basic Web Design']
    },
    {
        'id': 2,
        'name': 'Simple Python Script',
        'description': 'A Python script to automate file renaming in a directory.',
        'link': 'https://github.com/yourusername/file-renamer',
        'skills': ['Python', 'File Handling', 'Automation']
    }
]

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

@app.route('/')
def index():
    return render_template('index.html')


# Route to list all projects
@app.route('/projects')
def list_projects():
    return render_template('list_projects.html', projects=projects)

# Route to serve the HTML form
@app.route('/add')
def add_project_form():
    return render_template('add_project.html')

# Route to handle form submission and add a new project
@app.route('/add_project', methods=['POST'])
def add_new_project():
    name = request.form['name']
    description = request.form['description']
    link = request.form.get('link')
    skills_str = request.form.get('skills')
    skills = [skill.strip() for skill in skills_str.split(',')] if skills_str else []

    # Create a new project dictionary
    new_project = {
        'id': len(projects) + 1,  #  need to change with a database
        'name': name,
        'description': description,
        'link': link,
        'skills': skills
    }
    projects.append(new_project)

    flash(f"Project '{name}' added successfully!", 'success')  
    return redirect(url_for('list_projects'))

# Route to serve the HTML form for job description analysis
@app.route('/analyze_form')
def analyze_job_form():
    return render_template('analyze_job.html')

# TODO
# Route to handle form submission and analyze job description
@app.route('/analyze', methods=['POST'])
def analyze_job_description():
    job_description = request.form['job_description']
    job_description_lower = job_description.lower()

    # --- Gathering all unique skills from the projects ---
    all_skills = set()
    for project in projects:
        # Some projects might have no skills, .get('skills', []) will safely handle that casw
        for skill in project.get('skills', []):
            # lowercase version of the skill for consitent matching
            all_skills.add(skill.lower())
    
    # --- Finding which known skills are in the job description --
    found_skills_in_jd = set()
    for skill in all_skills:
        # Simple check to see if the skill string apear anywhere in the lowercase JD
        if skill in job_description_lower:
            # We found this skill in the job description
            found_skills_in_jd.add(skill) # lowercase version

    # --- Finding which projects match the found skill ---
    matching_projects = []
    for project in projects:
        project_skills_lower = set(skill.lower() for skill in project.get('skills', []))
        # Check for any overlap between skills found in JD and skills in this project
        if found_skills_in_jd.intersection(project_skills_lower):
            # If at least one match is found we can add the project (Refiment needed later)
            matching_projects.append({
                'name': project.get('name', 'Unnamed Project'),
                # finding exact skills match for this project
                'matched_skills': list(found_skills_in_jd.intersection(project_skills_lower))
            })
    
    # --- JSON output for now, improve later ---
    return render_template('analysis_results.html',
                           job_description=job_description,
                           skills_found_in_jd=list(found_skills_in_jd), 
                           matching_projects=matching_projects)

if __name__ == '__main__':
    app.run(debug=True)
