# archivesspace-gokm-scripts
Repo for scripts to assist with batch processes in ASpace

<h1>Subjects</h1>
<b>gokm_update_ao_subjects.py</b>
<p>Python script reads in a 2 column CSV containing archival object ref IDs and subject record IDs and appends subjects to existing archival object records. Only appends one subject per archival object. Adapted from: https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/duke_update_ao_titles_and_dates.py</p> 

<h1>Digital Objects</h1>
<b>create_and_link_do.py</b>
<p>Script reads in a 2 column CSV containing archival object ref IDs and digital object unique IDs and creates new digital object records and attaches them to existing archival records. Titles of the new digital objects are pulled from the archival objects they are linked to. Adapted from: https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/duke_update_archival_object.py</p>
