import requests
import csv
from bs4 import BeautifulSoup
from tqdm import tqdm


def getFinalLink(link):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            link = response.url
        else:
            link = " "
    except:
        link = " "
    return link


def getCourseGroup(code):
    areaCode = int("".join([char for char in list(code) if char.isdigit()]))
    areaDigit = areaCode // 10 ** 1 % 10
    areaMap = {
        0: "Introductory, miscellaneous",
        1: "Hardware Systems",
        2: "Artificial Intelligence",
        3: "Numerical Analysis",
        4: "Software Systems",
        5: "Mathematical Foundations of Computing",
        6: "Analysis of Algorithms",
        7: "Computational Biology and Interdisciplinary Topics",
        8: "Technology and Society",
        9: "Independent Study and Practicum"
    }
    return areaMap[areaDigit]


def scrapePage(academicYear, quarter):
    # make GET request
    prefix = "https://cs.stanford.edu/courses/schedules"
    url = f"{prefix}/{academicYear}.{quarter}.php"
    print(f"scraping {url}")
    page = requests.get(url)

    if page.status_code != 200:
        print(f"bad request for {url}")
        return

    # parse table
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find("table")
    courses = []
    trs = table.find_all('tr')
    for idx, tr in enumerate(tqdm(trs[1:])):
        tds = tr.find_all('td')
        code = tds[0].get_text(strip=True)
        # make sure we have correct link
        link = getFinalLink(tds[0].find_all("a")[0]["href"].lower())
        course = {
            "id": f"{academicYear}-{quarter}-{idx:03d}",
            "AY": academicYear,
            "Quarter": quarter,
            "Group": getCourseGroup(code),
            "Sub-Group": " ",
            "Code": code[:2].lower() + code[2:],
            "Link": link,
            "Title": tds[1].get_text(strip=True),
            "Instructor": tds[2].get_text(strip=True)
        }
        courses.append(course)

    # write to csv
    with open(f"{academicYear}.{quarter}.csv", 'w', newline='') as csvfile:
        fieldnames = ["id", "AY", "Quarter", "Group", "Sub-Group",
                      "Code", "Title", "Link", "Instructor"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for course in courses:
            writer.writerow(course)


def main():
    academicYears = ["2020-2021"]
    quarters = ["autumn", "winter", "spring", "summer"]
    for academicYear in academicYears:
        for quarter in quarters:
            scrapePage(academicYear, quarter)


if __name__ == "__main__":
    main()
