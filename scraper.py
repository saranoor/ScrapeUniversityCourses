from playwright.sync_api import sync_playwright
import time

campuses_codes = [
    "IUBLA",
    "IUINA",
    "IUCOA",
    "IUEAA",
    "IUFTW",
    "IUKOA",
    "IUNWA",
    "IUSBA",
    "IUSEA",
]
results = []
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://sisjee.iu.edu/sisigps-prd/web/igps/course/search/")

    for campus_code in campuses_codes:
        page.select_option("#cs-campus-search__select", f"{campus_code}")
        page.select_option("#cs-term-search__select", "4265")  # Summer 2026
        page.select_option("#cs-term-search__select", "4262")  # Spring 2026
        subjects = page.locator("#cs-subject-search__select option").all_text_contents()
        time.sleep(1)
        subject_values = page.locator("#cs-subject-search__select option").evaluate_all(
            "options => options.map(opt => opt.value).filter(v => v !== '')"
        )
        time.sleep(5)

        for dept in subject_values[2:5]:
            page.select_option("#cs-subject-search__select", value=dept)
            page.wait_for_load_state("networkidle")
            time.sleep(2)

            # Locate all course containers
            course_elements = page.locator(".cs-course-results .rvt-border-bottom")

            courses_data = []

            for i in range(course_elements.count()):
                element = course_elements.nth(i)

                # Extract data using specific paragraph/button classes
                course_id = element.locator(
                    ".cs-course-results__summary-left p"
                ).first.inner_text()
                credits = element.locator(
                    ".cs-course-results__summary-left p"
                ).last.inner_text()
                title = element.locator(
                    ".cs-course-results__summary-right p"
                ).inner_text()

                courses_data = {
                    "id": course_id,
                    "credits": credits,
                    "title": title,
                    "sections": [],
                }
                view_classes_btn = element.locator(
                    ".cs-course-results__view-classes-button"
                )
                view_classes_btn.click()
                page.wait_for_timeout(1000)
                try:
                    page.wait_for_selector("table.rvt-m-bottom-sm")
                except:
                    print("Failed to find table selector")
                    page.keyboard.press("Escape")
                    continue

                # 2. Target the rows in the table body
                # Each 'cs-single-component-class-summary__row' represents one class section
                class_rows = page.locator(
                    "tr.cs-single-component-class-summary__row"
                ).all()

                sections = []
                for row in class_rows:
                    # Use the column indices (0-based) to get specific data
                    # 3rd index = Instructor, 4th index = Open Seats
                    instructor = (
                        row.locator("td.cs-class-data-container")
                        .nth(3)
                        .inner_text()
                        .strip()
                    )
                    open_seats = (
                        row.locator("td.cs-class-data-container")
                        .nth(4)
                        .inner_text()
                        .strip()
                    )

                    # Clean up the instructor name (it often has newlines or commas)
                    instructor = instructor.replace("\n", " ")

                    # Clean up seats (removes 'Waitlist 0' text if you just want the ratio)
                    # This splits by newline and takes the first line (e.g., "32/58")
                    seat_ratio = open_seats.split("\n")[0]

                    sections.append({"instructor": instructor, "seats": seat_ratio})
                    print(f"instructor: {instructor}")
                    print(f"seat_ratio: {seat_ratio}")

                    courses_data["sections"].append(
                        {"instructor": instructor, "open_seats": open_seats}
                    )

                page.keyboard.press("Escape")

                page.wait_for_timeout(1000)
                print(courses_data)
    browser.close()
