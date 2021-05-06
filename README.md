# Django Based Careerpedia Project


## Features:
- Provides career guidance to Students
- Courses, subjects, opportunities, Colleges
- Can maintain wishlist
- Colleges can maintain thier data interms of offered courses

# Deployment Steps:
- copy entire folder to project location
- cd careerpedia project folder
- start server 


RestAPIs:


Courses with Colleges:

- API: http://localhost:8000/api/courses_colleges/{level name}/?stream={stream name}&field={field name}
- level is manadatory
- Example: 
	- http://localhost:8000/api/courses_colleges/twelveth/
	- which return json data with courses, subjects, oppotunities and colleges information for all the level "twelveth", icludes intermediate and dipoloma
	- http://localhost:8000/api/courses_colleges/twelveth/?stream=intermediate
	- will give us intermediate data
	- http://localhost:8000/api/courses_colleges/twelveth/?stream=diploma
	- will give us diploma data

Colleges with Courses:
- API: http://localhost:8000/api/college_courses/{level name}/?stream={stream name}&field={field name}
- college name and level mandatory

- Example: 
-	http://localhost:8000/api/college_courses/PAGE%20Junior%20College/twelveth/
-   response would be college name and offered courses with checkbox status
-   checkbox true means they are offering that course present
-   they can disable and enable with courses


Course info:
API: http://localhost:8000/api/courses/{level name}/?stream={stream name}&field={field name}

- Example: 
-	http://localhost:8000/api/courses/twelveth/
-   response would be collegename and courses with checkbox status


'coursesList/' --> all courses data from database as it is, no collges, courses,
'opportunitiesList/?format=api', all opportunities data with course name mappings
'subjectsList/', all subjects data with course name mappings
'collegesList/',  all collegegs data


