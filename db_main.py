from cs50 import SQL
import string
import sqlite3
from statistics import mode
from flask import Flask, flash, redirect, render_template

#Set globals
# positive = ['y', 'yes']
# negative = ['n', 'no']

#find the connecting key terms
def iterate_keys(term, db):
    word = term.lower()
    key_id = db.execute('SELECT key_id FROM synonyms where synonym = ?', word)
    if len(key_id) == 0:
        key_id = db.execute('SELECT id FROM keywords where key = ?', word)
        if len(key_id) == 0:
            #TODO:(L/M) Give option to add keys
            print('no variables to pull key')
            return False
    return key_id

#read a document to find terms
def read(text, db):
    keys = []
    
    res = [word.strip(string.punctuation) for word in text.split() if word.strip(string.punctuation).isalnum()]
    for word in res:
        key_id = iterate_keys(word, db)
        if key_id != False:
            for x in range(len(key_id)):
                if 'key_id' in  key_id[x]:
                    keys.append(key_id[x]['key_id'])
                elif 'id' in key_id[x]:
                    keys.append(key_id[x]['id'])
    #TODO:(H/L) account for duplicates or more common keys ^
    return keys

# insert skills and job history into program
def connect_experiences(experiences, db):
    key = []
    for x in experiences:
        key.append(read(x, db)[0])
    return key        

def add_projects(job_id, job, project, description, db):      #not in use yet
    #connect to keywords 
    key_id = (read(description, db))

    if job == None:
        db.execute("INSERT INTO projects (project, explanation, key_id) VALUES (?, ?, ?)", project, description, str(key_id[0]))
    else:
        db.execute("INSERT INTO projects (project, explanation, job_id, key_id) VALUES (?, ?, ?, ?)", project, description, job_id, str(key_id[0]))
    return True

def add_job_history(job, start, end, experiences, db):
    #input into TABLE:jobs via sql
    db.execute("INSERT INTO jobs (job, start_date, end_date) VALUES (?, ?, ?)", job, start, end)
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


def add_skills(skill, db):
    key_id = read(skill, db)
    db.execute("INSERT INTO skills (skill, key_id) VALUES (?, ?)", skill, key_id)
    return True

# Read job listing
def read_listing(listing, db):
    projects = []
    skills = []
    jobs = []
    experiences = []
    keys = set(read(listing, db))
    for x in keys:
        # project_id = db.execute("SELECT id FROM projects WHERE key_id = ?", str(x))
        # for y in project_id:
        #     projects.append(y)
        # skill_id = db.execute("SELECT id FROM skills WHERE key_id = ?", str(x))
        # for y in skill_id:
        #     skills.append(y)
        job_id = db.execute("SELECT id FROM jobs WHERE key_id = ?", str(x))     #TODO: H/H doesn't take from it, why?
        for y in job_id:
            jobs.append(y['id'])
        # exp_id = db.execute("SELECT id FROM experiences WHERE key_id = ?", str(x))
        # for y in exp_id:
        #     exp_data = db.execute("SELECT job_id FROM experiences WHERE key_id = ?", str(x))
        #     experiences.append([exp_id, exp_data])

    return projects, skills, jobs, experiences


def build_resume(project_ids, skill_ids, job_ids, db):
    #TODO: (M/M) the following loops iterate over last, edit so it adds onto it instead
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
            job = db.execute("SELECT job, start_date, end_date FROM jobs WHERE id = ?", str(x))
            experience = db.execute("SELECT summary FROM experiences WHERE job_id = ?", str(x))
            jobs.append(job)
            experiences.append(experience)

    

    #return render_template("resume_inf.html", skills = skills, jobs = jobs, experiences = experiences, projects = projects)
    #TODO: M/H figure out how to output HTML from app
    return skills, jobs, experiences, projects

def output_resume(desc, db):
    projects, skills, jobs = read_listing(desc, db)
    build_resume(projects, skills, jobs, db)

def build_coverletter():        #not in use yet
    #take a frame
    #pull more information by lookup of company---------consider function
    #input necessary info

    pass

def build_thanks():             #not in use yet
    #take a frame
    #pull information by lookup of company
    #input necessary info
    pass

