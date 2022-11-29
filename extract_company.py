import jsonlines
import csv
import pandas as pd

def extract(str):
    sentences = str.split('\n')
    try:
        i1 = sentences.index("Website")
        website = sentences[i1 + 1]
    except:
        website = ""
    try:
        i2 = sentences.index("Industry")
        industry = sentences[i2 + 1]
    except:
        industry = ""
    try:
        i3 = sentences.index('Company size')
        size = sentences[i3 + 1]
    except:
        size = ""
    try:
        i4 = sentences.index('Headquarters')
        headquarters = sentences[i4 + 1]
    except:
        headquarters = ""
    try:
        i5= sentences.index('Founded')
        founded = sentences[i5 + 1]
    except:
        founded = ""
    return website, industry, size, headquarters, founded


def main():
    output = open(f'csvfile_category/linkedin_company.csv', 'w', newline='', encoding='utf-8')
    head = ['company_name', 'headquarters', 'website', 'size', 'industry', 'founded', "description", "url", 'img_url']
    csvwriter = csv.writer(output)
    csvwriter.writerow(head)
    #urls = []
    names = []
    urlfile = jsonlines.open('jsonfile_category/company_url.jsonl', "r")
    for line in urlfile:
        #if line['url'] != None:
        #    urls.append(line['url'])
        if line['company_url'] != "":
            names.append(line['company_name'])
    print(len(names))
    exist_name = []  # deduplicate again
    with jsonlines.open('jsonfile_category/companies1.jsonl') as f:
        index = 0
        for line in f:
            if names[index] not in exist_name:
                website, industry, size, headquarters, founded = extract(line['info'])
                csvwriter.writerow([names[index], headquarters, website, size, industry, founded, line['desc'], line['url'], line['img_url']])
                exist_name.append(names[index])
            index += 1
    print(len(exist_name))
    #states = ['California', 'Florida', 'Georgia', 'NewJersey', 'NewYork', 'Pennsylvania', 'Texas', 'Washington']
    #company_names = []
    #for state in states:
    df = pd.read_csv(f'csvfile_category/linkedin_req.csv', usecols=['company_name', 'url'])
    for index, row in df.iterrows():
        if row['company_name'] not in exist_name:
            #company_names.append(row['company_name'])
            exist_name.append(row['company_name'])
            csvwriter.writerow([row['company_name'], "", "", "", "", "", "", "", ""])



if __name__ == "__main__":
    main()
