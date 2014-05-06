This document and it's described processes is only applicable to Features and is not applicable to any other model within our system (e.g., Application, Template, Field, User)

# Loading a template safely

1. Get type_ hash from URL
2. Check to see if user has access to that Template ... via is_public or permissions and if user has access continue to next step
3. Load the template and proceed
4. Loop over all fields, checking to see if is_public or permission and continue
5. Display final template

----

# Loading a list of Features safely

## Part 1
1. Get type_ has from URL
2. Check to see if user has access to that Template ... via is_public or permissions and if user has access continue to next step
3. Peform the search and return a list of objects

## Part 2
4. Check the Extension type
5. Based on the extension type take the list of objects from Step 3 and make any necessary modifications (i.e., GeoJSON only)
6. After all modifications are made, pass final object to Model.endpoint_response(**args)