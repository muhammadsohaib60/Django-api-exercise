# Project Description and Completion Summary:

1. **Setup Django version 3.2.23**
   - **Status** : Completed
   - **Details** : Django version 3.2.23 was successfully set up as the framework for the project.
2. **Build an API to pull sample truck ELD data**
   - **Status** : Completed
   - **Details** : An API was created to fetch sample truck ELD data using a function that interacts with the provided endpoint.
   - **API Endpoint** : `/api/trucks/`
   - **Subtasks** :
   - **Request API test environment access through DMs** : Handled outside the scope of code implementation.
3. **Build a function to detect FMCSA HOS violations**
   - **Status** : Completed
   - **Details** : Functions were created to check for Hours of Service (HOS) violations based on FMCSA regulations.
   - **API Endpoints** :
   - `/api/check_truck_hos/`
   - `/api/check_driver_hos/`
   - **Resources** : [FMCSA HOS Regulations](https://www.fmcsa.dot.gov/regulations/hours-service/summary-hours-service-regulations)
4. **Build a function to plan out a driver's driving schedule based on pickup and dropoff times and conditions**
   - **Status** : Completed
   - **Details** : A function was built to optimize a driver's driving schedule, incorporating the "Sleeper Berth Provision" and excluding "Adverse Driving Conditions" and "Short-Haul Exception".
   - **API Endpoint** : `/api/schedule/`
   - **Subtasks** :
   - **Make this function as optimal as possible to leave the maximum future flexibility on HOS** : Implemented with optimization logic.
   - **"Sleeper Berth Provision" needs to be built into this function** : Integrated into the scheduling function.
   - **"Adverse Driving Conditions" and "Short-Haul Exception" does not need to be built into this function** : Excluded from the function as per requirements.
5. **Build a function that**
   - **Status** : Completed
   - **Details** : A function was built to evaluate whether inputs constitute an HOS violation and provide suggestions if a violation occurs.
   - **API Endpoint** : `/api/check_hos_with_conditions/`
   - **Subtasks** :
   - **Takes Pickup and Dropoff conditions along with Duty Status and times as inputs**
     - **Resources** : [Using ELDs](https://www.fmcsa.dot.gov/hours-service/elds/using-elds)
     - **Functionality** : Evaluate HOS conditions and return detailed violation messages.
   - **Returns**
     - **Whether inputs constitute an HOS violation** : Provided in the response.
     - **If so, how could the HOS have been entered instead while maintaining pickup and dropoff requirements to not result in an HOS violation** : Included in the response.

### Additional Implementations:

- **Frontend Enhancements** : The homepage was updated to include forms and a display for planning optimal schedules and checking HOS violations.
- **HOS Rules Display** : A section was added on the homepage to display key HOS rules for user reference.

### Summary of Implementations:

- **API Endpoints** :
- `/api/trucks/`: Fetch sample truck ELD data.
- `/api/check_truck_hos/`: Check HOS violations for trucks.
- `/api/drivers/`: Fetch driver data.
- `/api/check_driver_hos/`: Check HOS violations for drivers.
- `/api/schedule/`: Plan optimal schedule for a driver.
- `/api/check_hos_with_conditions/`: Evaluate HOS conditions based on provided inputs.

## How to Run project

- cd prologs_project
- python manage.py migrate
- python manage.py runserver
