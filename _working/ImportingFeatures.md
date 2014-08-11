#1 User uploads a file via the feature collection's Import page

#1a File is upload to the server (S3, DO)

#1b A new job is created in the queue

#2 User is taken to a "Pending Imports" page that displays all of the current
   imports for that current Application, imports are not limited to the current
   user. If the user has the correct permissions, they can see all current imports
   for their applications

#3 Job is enqueued and eventually executed when resources are available

#3a Job executes a process that opens the CSV, loops over it, and execute's a
    `feature_create` for each line.

#3b Owner for each Feature is set to the user importing the content, unless there
    is an 'owner' column in the CSV file being imported

#3c 