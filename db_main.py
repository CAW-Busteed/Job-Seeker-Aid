import os
import string
from statistics import mode
from fpdf import FPDF

#execute sql
def exec_script(sqlFile, db):
        with open(os.path.join(os.path.dirname(__file__), sqlFile), "r") as f:
            for line in f.readlines():
                if not line.strip(): continue  # skip empty lines
                db.execute(line)

#This set of functions builds a user's database of qualifications
#find the connecting key terms
def iterate_keys(term, db):
    word = term.lower()
    key_id = db.execute('SELECT key_id FROM synonyms where synonym = ?', word)
    if len(key_id) == 0:
        key_id = db.execute('SELECT id FROM keywords where key = ?', word)
        if len(key_id) == 0:
            return False
    return key_id

#read a document to find terms
def read(text, db):
    keys = []
    if text == None:
        print('No Variable')

    text1 = text.replace("'", ' ')
    res = [word.strip(string.punctuation) for word in text1.split() if word.strip(string.punctuation).isalnum()]
    for word in res:
        key_id = iterate_keys(word, db)
        if key_id != False:
            for x in range(len(key_id)):
                if 'key_id' in  key_id[x]:
                    keys.append(key_id[x]['key_id'])
                elif 'id' in key_id[x]:
                    keys.append(key_id[x]['id'])
    if keys == []:
        #if nothing applies, 0 as a id placeholder
        keys.append(0)
    return keys

# insert skills and job history into program
def connect_experiences(experiences, db):
    key = []
    for x in experiences:
        results = read(x, db)
        if mode(results)!=0:
            key.append(mode(results))
        else:
            results.remove(0)
            if len(results)>0:
                key.append(mode(results))
            else:
                key.append(0)
    return key        

def add_projects(job_id, job, project, description, db):      #not in use yet
    #connect to keywords 
    key_id = (read(description, db))

    if job == None:
        db.execute("INSERT INTO projects (project, explanation, key_id) VALUES (?, ?, ?)", project, description, str(key_id[0]))
    else:
        db.execute("INSERT INTO projects (project, explanation, job_id, key_id) VALUES (?, ?, ?, ?)", project, description, job_id, str(key_id[0]))
    return True

def add_job_history(job, location, start, end, experiences, db):
    #check if the job is already there first!
    check_job = db.execute("SELECT job FROM jobs WHERE job = ?", job)
    check_loc = db.execute("SELECT location FROM jobs WHERE location = ?", location)

    if len(check_job) == 0 and len(check_loc) == 0:
        #input into TABLE:jobs via sql
        db.execute("INSERT INTO jobs (job, location, start_date, end_date) VALUES (?, ?, ?, ?)", job, location, start, end)
        job_id = str((db.execute("SELECT id FROM jobs WHERE job= ?", job))[0]["id"])
        job_key = read(job, db)
        if len(job_key)==1:
            job_key = str(job_key[0])
            db.execute("UPDATE jobs SET key_id = ? WHERE job = ?", job_key, job)
        
        #input string and job_id into TABLE: experiences
        key = connect_experiences(experiences, db)
        if len(key) == len(experiences):
            for x in range(len(experiences)):
                db.execute("INSERT INTO experiences (job_id, summary, key_id) VALUES (?, ?, ?)", job_id, experiences[x], str(key[x]))
    elif len(check_job) > 0 and len(check_loc) > 0:
        print('Job already exists')

def add_skills(skill, db):
    key_id = read(skill, db)
    db.execute("INSERT INTO skills (skill, key_id) VALUES (?, ?)", skill, key_id)
    return True


#The following functions are to build from the database
# Read job listing
def read_listing(listing, db):
    projects = []
    skills = []
    jobs = []
    experiences = []
    keys = read(listing, db)
    if keys == [0]:
        print("Error: no related terms, update key")
    for x in keys:
        project_id = db.execute("SELECT id FROM projects WHERE key_id = ?", str(x))
        if project_id != None:
            for y in project_id:
                projects.append(y)

        skill_id = db.execute("SELECT id FROM skills WHERE key_id = ?", str(x))
        if skill_id != None:
            for y in skill_id:
                skills.append(y)

        job_id = db.execute("SELECT id FROM jobs WHERE key_id = ?", str(x))
        for y in job_id:
            jobs.append(y['id'])
        
        exp_id = db.execute("SELECT id FROM experiences WHERE key_id = ?", str(x))
        for y in exp_id:
            exp_data = db.execute("SELECT job_id FROM experiences WHERE key_id = ?", str(x))
            experiences.append([y, exp_data])

    return projects, skills, jobs, experiences


def build_resume(project_ids, skill_ids, job_ids, exp_id, db):
    skills=[]
    jobs =[]
    projects = []
    experiences =[]

    #relevant skills
    if len(skill_ids)>0: 
        skills = db.execute("SELECT skill FROM skills WHERE id in ?", skill_ids)
        #consider removing difference between soft and hard skills
    
    #relevant project
    if len(project_ids)>0: 
        projects = db.execute("SELECT project, explanation FROM projects WHERE id in ?", project_ids)
    
    #relevant job history + experiences
    if len(job_ids)>0:
        for x in job_ids:
            job = db.execute("SELECT job, location, start_date, end_date FROM jobs WHERE id = ?", str(x))
            experience = db.execute("SELECT summary FROM experiences WHERE job_id = ?", str(x))
            jobs.append(job)
            experiences.append(experience)
    
    #relevant experiences, tie in jobs
    if len(exp_id)>0:
        id =[]

        for x in exp_id:

            #get job ids for every relevant experience
            for y in x[1]:
                if y['job_id'] not in id:
                    id.append(y['job_id'])

            #add job to list
            for z in id:   
                job = db.execute("SELECT id, job, location, start_date, end_date FROM jobs WHERE id = ?", str(z))
                if job not in jobs:
                    jobs.append(job)
            
            #now add experiences
            experience = db.execute("SELECT job_id, summary FROM experiences WHERE id = ?", str(x[0]['id']))
            if experience not in experiences:
                experiences.append(experience)
    return skills, jobs, experiences, projects

def output_resume(desc, db):
    proj_fit, skill_fit, job_fit, exp_fit = read_listing(desc, db)
    skills, jobs, experiences, projects = build_resume(proj_fit, skill_fit, job_fit, exp_fit, db)
    content = "Resume\n\nJob History\n\n"

    if len(jobs)>0:        
        for x in jobs:
            j_content = "-"
            e_content = "\n"

            for y in experiences:
                if y[0]['job_id'] == x[0]['id']:
                    e_content = e_content + f"   > {y[0]['summary']}\n"

            j_content= j_content + f"{x[0]['job']} \n  {x[0]['location']} \n  {x[0]['start_date']} to {x[0]['end_date']}\n" + e_content
            content = content + j_content +"\n"
    
    if len(skills)>0:   #not used yet
        pass

    if len(projects)>0: #not used yet
        pass

    #Create html for later pdf formatting
    # with open("resume.html", "w") as html_file:
    #     html_file.write(f"<html><body>{content}</body></html>")

    # Convert to PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size = 10)
    pdf.multi_cell(0, 5, content)
    pdf.output("resume.pdf")
