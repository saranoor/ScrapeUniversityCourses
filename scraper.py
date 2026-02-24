from playwright.sync_api import sync_playwright
import time
import csv

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

output_file = "iu_courses_2026.csv"

header = [
    "Campus",
    "Subject",
    "Course ID",
    "Title",
    "Credits",
    "Section Type",
    "Instructor",
    "Open Seats",
]

with open(output_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
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

        for dept in subject_values[2:3]:
            page.select_option("#cs-subject-search__select", value=dept)
            page.wait_for_load_state("networkidle")
            time.sleep(2)

            course_elements = page.locator(".cs-course-results .rvt-border-bottom")

            courses_data = []

            for i in range(course_elements.count()):
                element = course_elements.nth(i)

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

                page.wait_for_selector(
                    ".rvt-m-bottom-sm, .rvt-border-top", state="visible", timeout=8000
                )

                class_rows = page.locator(
                    ".cs-single-component-class-summary__row, .cs-multi-component-summary__row"
                ).all()

                sections = []
                with open(output_file, mode="a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    for row in class_rows:
                        cells = row.locator("td.cs-class-data-container")

                        instructor = (
                            cells.nth(3).inner_text().strip().replace("\n", ", ")
                        )
                        open_seats = cells.nth(4).inner_text().strip().split("\n")[0]

                        component_type = "Standard"
                        parent_heading = row.locator("xpath=ancestor::li//h3").first
                        if parent_heading.is_visible():
                            component_type = parent_heading.inner_text().strip()

                        sections.append(
                            {
                                "type": component_type,
                                "instructor": instructor,
                                "open_seats": open_seats,
                            }
                        )
                        writer.writerow(
                            [
                                campus_code,
                                dept,
                                course_id,
                                title,
                                credits,
                                component_type,
                                instructor,
                                open_seats,
                            ]
                        )
                    courses_data["sections"] = sections

                page.keyboard.press("Escape")

                page.wait_for_timeout(1000)
                print(courses_data)
    browser.close()
