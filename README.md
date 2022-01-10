# archivesspace-gokm-scripts
Repo for scripts to assist with batch processes in ASpace

Scripts that have been tested and documented for use within the GOKM workflow are in the archivesspace-gokm-scripts/python/gokm_documented/ folder. The assocuated documentation resides in the CIM handbook. GOKM team, please use the tested and documented versions of the scripts unless working on a new process.


<h1>Archival Objects</h1>
<b>add_copyright_notes.py</b>
<p>Script reads in a 1 column CSV containing archival object ref IDs and creates a new usestrict note with label "Copyright Management." Adapted from https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/duke_as_replace_notes.py</p>

<b>add_ownership_and_rights_notes.py</b>
<p>Script reads in a 2 column CSV containing archival object ref IDs and copyright notes and creates a legalstatus note with label "Ownership and Rights" and content fed from the CSV copyright notes column. Adapted from https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/duke_as_replace_notes.py</p>

<b>aspace_delete_note.py</b>
<p>Script reads in a 1 column CSV containing archival object ref IDs and removes acqinfo notes. Adapted from https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/duke_as_replace_notes.py</p>

<b>update_ao_subjects.py</b>
<p>Script reads in a 2 column CSV containing archival object ref IDs and subject record IDs and adds ONE subject to the archival object's existing list of subjects. Adapted from https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/duke_update_archival_object.py</p>

<b>unpublish_physloc_note.py</b>
<p>Script reads in a 1 column CSV containing archival object ref IDs and unpulishes all physloc notes. Adapted from https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/duke_as_replace_notes.py</p>

<b>gokm_update_ao_subjects.py</b>
<p>Python script reads in a 2 column CSV containing archival object ref IDs and subject record IDs and appends subjects to existing archival object records. Only appends one subject per archival object. Adapted from https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/duke_update_ao_titles_and_dates.py</p> 

<h1>Digital Objects</h1>
<b>create_and_link_do.py</b>
<p>Script reads in a 2 column CSV containing archival object ref IDs and digital object unique IDs and creates new digital object records and attaches them to existing archival records. Titles of the new digital objects are pulled from the archival objects they are linked to. Adapted from https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/duke_update_archival_object.py</p>

<b>update_do_file_uri.py</b>
<<p>Script reads in a 2 column CSV containing digital object IDs and file URIs and udpates the digital object's file URI. Adapted from https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/duke_update_archival_object.py</p>

<h1>CSV Generators</h1>
<b>create_depicted_subject_csv.py</b>
<p>Script takes an EAD file and uses a dictionary containing possible subjects to assign subject IDs to archival object ref IDs based on names found in the archival object's title.</p>

<b>ead_to_csv.py</b>
<p>Script takes an EAD file and creates a CSV of archival object ref IDs.</p>
