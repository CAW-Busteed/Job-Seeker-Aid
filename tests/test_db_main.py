import os
import tempfile
import pytest
from cs50 import SQL
from sqlalchemy.util import deprecations
import db_main

# get rid of gratuitous warning from sqlAlchemy
deprecations.SILENCE_UBER_WARNING = True


@pytest.fixture()
def dbfile():
    db_fd, db_path = tempfile.mkstemp()

    yield db_path

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture()
def db(dbfile):
    db = SQL(f"sqlite:///{dbfile}")

    def exec_script(sqlFile):
        with open(os.path.join(os.path.dirname(__file__), sqlFile), "r") as f:
            for line in f.readlines():
                if not line.strip(): continue  # skip empty lines
                db.execute(line)

    exec_script("schema.sql")  # create tables
    exec_script("data.sql")  # populate_db

    return db

def test_iterate_keys():
    assert db_main.iterate_keys('code') == 1

def test_iterate_keys(db):
    key = db_main.iterate_keys('programming', db)
    assert key[0]['id'] == 1

def test_read(db):
    text = "Seeking someone who can code."
    read=db_main.read(text, db)
    assert read==1


def test_add_projects():
    assert db_main.add_projects() == True

def test_add_projects(db):
    description = "Blah blah blah, code this."
    db_main.add_projects(0, None, 'Programmer', description, db)
    confirm = (db.execute("SELECT explanation FROM projects WHERE key_id=?", 1))[0]['explanation']
    assert description == confirm

def test_add_job_history(db):
    job="Assistant Editor"
    start="March 2010"
    end="May 2014"
    experiences= ["Organized layouts and structure of the Boston Tribune Newsletter.", "Authored over 300 pages of content over my career.", "Took steps to move onto a digital format."]
    db_main.add_job_history(job, start, end, experiences, db)
    test = (db.execute("SELECT job FROM jobs where id=?", 1))[0]['job']
    assert job==test 

def test_read_listing(db):
    job="Assistant Editor"
    start="March 2010"
    end="May 2014"
    experiences= ["Organized layouts and structure of the Boston Tribune Newsletter.", "Authored over 300 pages of content over my career.", "Took steps to move onto a digital format."]
    db_main.add_job_history(job, start, end, experiences, db)
    listing = 'Saint Josephs Medical Center is seeking an Outpatient Coding Supervisor to oversee its Health Information Management Department’s Outpatient Coding functions. The Supervisor must have an in depth knowledge of ICD 10 CM/PCS, CPT coding systems, 3m system encoder software and a thorough understanding of NCCI edits. Must have a Coding Credential 2-3 years Supervisory experience preferred Interested applicants should submit their resumes to: janice.cordola@saintjosephs.org Salary Range $65,000 to $70,000 annually '
    projects, skills, jobs = db_main.read_listing(listing, db)
    assert jobs == ['1']

def test_build_resume(db):
    job="Assistant Editor"
    start="March 2010"
    end="May 2014"
    zexperiences= ["Organized layouts and structure of the Boston Tribune Newsletter.", "Authored over 300 pages of content over my career.", "Took steps to move onto a digital format."]
    listing = 'Saint Josephs Medical Center is seeking an Outpatient Coding Supervisor to oversee its Health Information Management Department’s Outpatient Coding functions. The Supervisor must have an in depth knowledge of ICD 10 CM/PCS, CPT coding systems, 3m system encoder software and a thorough understanding of NCCI edits. Must have a Coding Credential 2-3 years Supervisory experience preferred Interested applicants should submit their resumes to: janice.cordola@saintjosephs.org Salary Range $65,000 to $70,000 annually '
    db_main.add_job_history(job, start, end, zexperiences, db)
    project_ids, skill_ids, job_ids = db_main.read_listing(listing, db)
    skills, jobs, experiences, projects = db_main.build_resume(project_ids, skill_ids, job_ids, db)
    assert zexperiences[2] == experiences[0]
