import pandas as pd

def main():
    states = ['California', 'Florida', 'Georgia', 'NewJersey', 'NewYork', 'Pennsylvania', 'Texas', 'Washington']
    company_names = []
    job_urls = []
    for state in states:
        df = pd.read_csv(f'csvfile/job_positions_{state}.csv', usecols=['company_name', 'url'])
        for index, row in df.iterrows():
            if row['company_name'] not in company_names:
                company_names.append(row['company_name'])
                job_urls.append(row['url'])
    print(len(job_urls))
    with open("txtfile/links_company.txt", "w") as f:
        for url in job_urls:
            f.write(f"{url}")


if __name__ == "__main__":
    main()