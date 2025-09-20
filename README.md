<p align="center">
  <img width="256" height="256" alt="NTU_STARS_Logo" src="https://github.com/user-attachments/assets/3280a11d-d212-43c0-a76a-33f6d562ad6b" />
</p>


<h1 align="center">
  NTU STARs Timetable Extractor 
</h1>
<p align="center">
  Python tool to extract module details and timings from your NTU STARs Timetable HTML file.
</p>
<p align="center">
  Simplify your schedule management, sharing, and analysis.  
</p>

![Demo](https://github.com/NabilAidilreza/NTU_STARS_Project/assets/58650657/97596935-beaa-4098-ba9c-eefd5cbf31ef)  

## Features  
- **Generate .ics files**: Import your timetable into Outlook, Google Calendar, or other calendar apps.  
- **Compare timetables**: Easily compare schedules with friends.
- **Check exam schedules**: Easily compare exam dates with friends.

## Quick Start  
1. Clone the repo.  
2. Install dependencies: `pip install -r requirements.txt`.  
3. Download your STARs Planner HTML file (from the main planning page, **not** weekly view).  
4. Save the file in the project directory and rename it to `STARS_{placeholder}.html` (e.g., `STARS_YourName.html`).  
5. Run `local_terminal.py`.  

> [!NOTE]
> **Start Date**: Update the start date in the script to match your semester (e.g., `14/08/2023` for Sem 1, `15/01/2024` for Sem 2).  
> **Color Coding**: Calendar events are categorized by course code (e.g., `IE1005`). Set colors in your calendar app for better visualization.  

