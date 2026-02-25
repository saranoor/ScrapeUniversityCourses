from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import time
import csv
import asyncio

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


async def scrape_dept(browser, campus_code, dept, semaphore):
    async with semaphore:  # Limits to 2 concurrent runs
        print(f"Starting {campus_code} - {dept}...")
        page = await browser.new_page(no_viewport=True)
        await page.goto("https://sisjee.iu.edu/sisigps-prd/web/igps/course/search/")

        # Select campus and term
        await page.select_option("#cs-campus-search__select", campus_code)
        await page.select_option("#cs-term-search__select", "4262")

        # Select specific department
        await page.select_option("#cs-subject-search__select", value=dept)
        await page.wait_for_load_state("networkidle")

        # ... Insert your course/instructor scraping logic here ...
        course_elements = page.locator(".cs-course-results .rvt-border-bottom")
        try:
            await course_elements.first.wait_for(state="visible", timeout=5000)
        except:
            print(f"Timeout: No course elements appeared for {dept}")
            return

        courses_data = []
        num_courses = await course_elements.count()
        print(f"Found {num_courses} courses for {dept} at {campus_code}")

        for i in range(num_courses):
            print(f"Processing course {i + 1}...")
            element = course_elements.nth(i)

            course_id = await element.locator(
                ".cs-course-results__summary-left p"
            ).first.inner_text()
            credits = await element.locator(
                ".cs-course-results__summary-left p"
            ).last.inner_text()
            title = await element.locator(
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
            await view_classes_btn.click()
            await page.wait_for_timeout(1000)

            await page.wait_for_selector(
                ".rvt-m-bottom-sm, .rvt-border-top",
                state="visible",
                timeout=8000,
            )

            class_rows = await page.locator(
                ".cs-single-component-class-summary__row, .cs-multi-component-summary__row"
            ).all()

            sections = []
            with open(output_file, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for row in class_rows:
                    print(f"Processing section row... {dept}")
                    cells = row.locator("td.cs-class-data-container")

                    instructor = (
                        (await cells.nth(3).inner_text()).strip().replace("\n", ", ")
                    )
                    open_seats = (
                        (await cells.nth(4).inner_text()).strip().split("\n")[0]
                    )

                    component_type = "Standard"
                    parent_heading = row.locator("xpath=ancestor::li//h3").first
                    if await parent_heading.is_visible():
                        component_type = (await parent_heading.inner_text()).strip()

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

            await page.keyboard.press("Escape")

            await page.wait_for_timeout(1000)
            # print(courses_data)

        await page.close()
        print(f"Finished {dept}")


# with sync_playwright() as p:
async def run_scraper():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--start-maximized"])
        page = await browser.new_page(no_viewport=True)
        await page.goto("https://sisjee.iu.edu/sisigps-prd/web/igps/course/search/")
        sem = asyncio.Semaphore(3)
        for campus_code in campuses_codes[0:1]:
            await page.select_option("#cs-campus-search__select", f"{campus_code}")
            await page.select_option("#cs-term-search__select", "4265")  # Summer 2026
            await page.select_option("#cs-term-search__select", "4262")  # Spring 2026
            subjects = await page.locator(
                "#cs-subject-search__select option"
            ).all_text_contents()

            time.sleep(1)
            subject_values = await page.locator(
                "#cs-subject-search__select option"
            ).evaluate_all(
                "options => options.map(opt => opt.value).filter(v => v !== '')"
            )
            print(f"Available subjects for {campus_code}: {subject_values}")
            print(f"subjects to scrape: {subject_values[3:5]}")
            tasks = [
                scrape_dept(browser, campus_code, dept, sem)
                for dept in subject_values[3:7]  # Example slice
            ]

            await asyncio.gather(*tasks)
            # for dept in subject_values[3:4]:
            #     print(f"Scraping {campus_code} - {dept}...")
            #     await page.select_option("#cs-subject-search__select", value=dept)
            #     await page.wait_for_load_state("networkidle")
            #     time.sleep(2)

            #     course_elements = page.locator(".cs-course-results .rvt-border-bottom")

            #     courses_data = []

            #     for i in range(await course_elements.count()):
            #         print(f"Processing course {i + 1}...")
            #         element = course_elements.nth(i)

            #         course_id = await element.locator(
            #             ".cs-course-results__summary-left p"
            #         ).first.inner_text()
            #         credits = await element.locator(
            #             ".cs-course-results__summary-left p"
            #         ).last.inner_text()
            #         title = await element.locator(
            #             ".cs-course-results__summary-right p"
            #         ).inner_text()

            #         courses_data = {
            #             "id": course_id,
            #             "credits": credits,
            #             "title": title,
            #             "sections": [],
            #         }
            #         view_classes_btn = element.locator(
            #             ".cs-course-results__view-classes-button"
            #         )
            #         await view_classes_btn.click()
            #         await page.wait_for_timeout(1000)

            #         await page.wait_for_selector(
            #             ".rvt-m-bottom-sm, .rvt-border-top",
            #             state="visible",
            #             timeout=8000,
            #         )

            #         class_rows = await page.locator(
            #             ".cs-single-component-class-summary__row, .cs-multi-component-summary__row"
            #         ).all()

            #         sections = []
            #         with open(output_file, mode="a", newline="", encoding="utf-8") as f:
            #             writer = csv.writer(f)
            #             for row in class_rows:
            #                 print(f"Processing section row...")
            #                 cells = row.locator("td.cs-class-data-container")

            #                 instructor = (
            #                     (await cells.nth(3).inner_text())
            #                     .strip()
            #                     .replace("\n", ", ")
            #                 )
            #                 open_seats = (
            #                     (await cells.nth(4).inner_text()).strip().split("\n")[0]
            #                 )

            #                 component_type = "Standard"
            #                 parent_heading = row.locator("xpath=ancestor::li//h3").first
            #                 if await parent_heading.is_visible():
            #                     component_type = (
            #                         await parent_heading.inner_text()
            #                     ).strip()

            #                 sections.append(
            #                     {
            #                         "type": component_type,
            #                         "instructor": instructor,
            #                         "open_seats": open_seats,
            #                     }
            #                 )
            #                 writer.writerow(
            #                     [
            #                         campus_code,
            #                         dept,
            #                         course_id,
            #                         title,
            #                         credits,
            #                         component_type,
            #                         instructor,
            #                         open_seats,
            #                     ]
            #                 )
            #             courses_data["sections"] = sections

            #         await page.keyboard.press("Escape")

            #         await page.wait_for_timeout(1000)
            #         # print(courses_data)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(run_scraper())
