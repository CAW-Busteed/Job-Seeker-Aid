from cs50 import SQL
import string
import sqlite3
from statistics import mode
from flask import Flask, flash, redirect, render_template

#Set globals
positive = ['y', 'yes']
negative = ['n', 'no']

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
            keys.append(key_id)
    #TODO:(H/L) account for duplicates or more common keys
    keys = keys[0][0]['key_id']
    return keys

# insert skills and job history into program
def connect_experiences(experiences, db):
    key = []
    for x in experiences:
        key.append(read(x, db))
    return key        

def add_projects(job_id, job, project, description, db):      #not in use yet
    #connect to keywords by function: iterate_keys
    key_id = str((read(description, db)))

    if job == None:
        db.execute("INSERT INTO projects (project, explanation, key_id) VALUES (?, ?, ?)", project, description, key_id)
    else:
        db.execute("INSERT INTO projects (project, explanation, job_id, key_id) VALUES (?, ?, ?, ?)", project, description, job_id, key_id)
    return True

def add_job_history(job, start, end, experiences, db):
    #input into TABLE:jobs via sql
    db.execute("INSERT INTO jobs (job, start_date, end_date) VALUES (?, ?, ?)", job, start, end)
    job_id = str((db.execute("SELECT id FROM jobs WHERE job= ?", job))[0]["id"])

    #input string and job_id into TABLE: experiences
    key = connect_experiences(experiences, db)
    if len(key) == len(experiences):
        for x in range(len(experiences)):
            db.execute("INSERT INTO experiences (job_id, summary, key_id) VALUES (?, ?, ?)", job_id, experiences[x], key[x])


def add_skills(skill, db):
    key_id = read(skill, db)
    db.execute("INSERT INTO skills (skill, key_id) VALUES (?, ?)", skill, key_id)
    return True

# Read job listing
def read_listing(listing, db):
    keys = []
    projects = []
    skills = []
    jobs = []
    keys.append(read(listing, db))
    for x in keys:
        project_id = db.execute("SELECT id FROM projects WHERE key_id = ?", x)
        for y in project_id:
            projects.append(y)
        skill_id = db.execute("SELECT id FROM skills WHERE key_id = ?", x)
        for y in skill_id:
            skills.append(y)
        job_id = db.execute("SELECT id FROM jobs WHERE key_id = ?", x)
        for y in job_id:
            jobs.append(y)
        # TODO: (L/L) add experiences
    return projects, skills, jobs


def build_resume(project_ids, skill_ids, job_ids, db):
    #TODO: (M/M) the following loops iterate over last, edit so it adds onto it instead
    skills, jobs, projects, experiences =[]
    #relevant skills 
    skills = db.execute("SELECT skill FROM skills WHERE id in ?", skill_ids)
        #consider removing difference between soft and hard skills
    #relevant job history + experiences 
    jobs = db.execute("SELECT job, start_date, end_date FROM jobs WHERE id in ?", job_ids)
    experiences = db.execute("SELECT summary FROM experiences WHERE job_id in ?", job_ids)

    #relevant project
    projects = db.execute("SELECT project, explanation FROM projects WHERE id in ?", project_ids)

    return render_template("resume_inf.html", skills = skills, jobs = jobs, experiences = experiences, projects = projects)

def output_resume(desc, db):
    projects, skills, jobs = read_listing(desc, db)
    build_resume(projects, skills, jobs)

def build_coverletter():        #not in use yet
    #take a frame
    #pull more information by lookup of company
    #input necessary info

    pass

def build_thanks():             #not in use yet
    pass

