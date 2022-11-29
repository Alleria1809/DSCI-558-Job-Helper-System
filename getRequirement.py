import json
import csv
import jsonlines
import en_core_web_sm
from spacy.matcher import Matcher

class extractor():
    def __init__(self):
        self.nlp = en_core_web_sm.load()

    def extractsalary(self, doc):
        matcher = Matcher(self.nlp.vocab)
        salary_pattern = [[{"LOWER": "$"}]]
        matcher.add("extractsalary", salary_pattern)
        finalSalary = []
        for sent in doc:
            sent = self.nlp(sent.lower())
            matches = matcher(sent)
            for match in matches:
                span = sent[match[1]:]
                possible_salary = [ent.text for ent in span.ents if ent.label_ == "MONEY"]
                #print(possible_salary)
                for token in possible_salary:
                    #print(span)
                    if "hour" in " ".join(finalSalary):
                        break
                    if "$" not in token:
                        if ("hour" not in span.text and "hr" not in span.text and "week" not in span.text) and "-" in span.text and "," in token:
                            #print("annual salary")
                            token.replace(",", "")
                            token = "$"+token
                            if token not in finalSalary:
                                finalSalary.append(token)
                        if ("hour" not in span.text and "hr" not in span.text and "week" not in span.text) and ("per year" in span.text or "annually" in span.text) and "," in token:
                            #print("annual salary")
                            token.replace(",", "")
                            token = "$"+token
                            if token not in finalSalary:
                                finalSalary.append(token)
                        elif "per hour" in span.text or "/hour" in span.text or "/ hour" in span.text \
                                or "one hour" in span.text or "an hour" in span.text or "/hr" in span.text \
                                or "per hr" in span.text:
                            #print("hour salary")
                            token = "$" + token
                            if token not in finalSalary:
                                finalSalary.append(token)
                    else:
                        if "billion" not in token and "million" not in token:
                            #print("full salary")
                            token.replace(",", "")
                            if token not in finalSalary:
                                finalSalary.append(token)
                    s = " ".join(finalSalary).lower()
                    s2 = span.text.lower()
                    if ("hour" in s2 or "hr" in s2) and ("hour" not in s and "hr" not in s) and finalSalary != []:
                        finalSalary.append("per hour")
                #print(finalSalary)
        finalSalary = " ".join(finalSalary).lower()
        #print(finalSalary)
        return finalSalary

def main():
    #state = 'Washington'
    #state1 = state.replace("%20", "")
    output = open(f'csvfile_category/job_positions.csv', 'w', newline='', encoding='utf-8')
    head = ["job_category", 'job_title', 'company_name', 'job_location', "work_type", "salary",
            "requirement", "job_description", "url", 'company_url']
    csvwriter = csv.writer(output)
    csvwriter.writerow(head)
    categories = ['Data Scientist', 'HR', 'Lawyer', 'Artist', 'Web Designer', 'Mechanical Engineer', 'Salesman',
                  'Civil Engineer',
                  'Software Developer', 'Business Analyst', 'Automation Tester', 'Electrical Engineer',
                  'Operations Manager',
                  'Network Security Engineer', 'Product Manager']
    urls = []
    for c in categories:
        category = c.lower().replace(" ", "%20")
        with open(f'txtfile_category/links_{category}.txt', "r") as f:
            for line in f:
                urls.append(line)

    with jsonlines.open(f"jsonfile_category/job_positions1.jsonl", "r") as f:
        index = 0

        for line in f:
            print(index)
            requirement = []
            desc = line["job_description"]
            add = "no"

            for i in range(len(desc)):
                sentence = desc[i].lower()
                if add == "yes" and (len(sentence.split(" ")) < 3 or len(sentence.split(" ")) > 31):
                    add = "no"
                if add == "yes":
                    requirement.append(sentence)
                if ("requirement" in sentence or "qualification" in sentence or "education" in sentence or
                        "working with" in sentence or "experience" in sentence or "skill" in sentence or
                        "required" in sentence or "looking for" in sentence) and len(sentence.split(" ")) < 10:
                    add = "yes"
                    if len(sentence.split()) > 8:
                        requirement.append(sentence)

                '''if "$" in sentence:
                    words = sentence.split(" ")
                    for word in words:
                        if "$" in word and len(word) < 10:
                            money.append(word)
                    if "per hour" in sentence:
                        money.append("per hour")'''
            SalaryInfo = extractor()
            salary = SalaryInfo.extractsalary(desc)
            salary = salary.replace("/ hour", "per hour").replace("/hour", "per hour").replace("/ hr", "per hour").replace(
                "/hr", "per hour").replace("hr", "per hour")
            if salary != "":
                if salary[0] != "$":
                    salary = "$"+salary
            csvwriter.writerow([line['job_category'], line['job_title'], line['company_name'], line['job_location'],
                                line['work_type'], salary, requirement, "\n".join(line["job_description"]), urls[index],
                                line['company_url']])
            index+=1


if __name__ == "__main__":
    main()