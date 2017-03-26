from WBClass import Scrapper
import time

url = 'https://www.glassdoor.com/Reviews/Accenture-Chicago-Reviews-EI_IE4138.0,9_IL.10,17_IM167.htm'
filename = 'reviews.csv'
Result = []

start = time.time()
print ('Starting Scrapper and logging in to {}...'.format(url.split('.')[1]))
SR = Scrapper()
print ('Getting reviews page 1...')
SR.fetch_page(url)
print ('parsing...',)
data = SR.parse_data
print (len(data), 'reviews found on this page.')
Result.extend(data)

count = 2
Next_Page = True
while Next_Page:
    Next_Page = SR.fetch_nextpage()
    if Next_Page:
        print ('Getting reviews page %s...'%(count))
        SR.fetch_page(Next_Page)
        print ('parsing...')
        data = SR.parse_data
        print (len(data), 'reviews found on this page.')
        Result.extend(data)
        count +=1


print ('Writing results to %s'%filename)

Headers = [ "headline", "rating", "position", "status", "date", "duration", "cons", "pros", "management_advice",
            "recommends", "outlook" ]

with open(filename, 'w') as f:

    headings = ','.join(Headers)
    f.write(headings+'\n')
    for Data in Result:
        line = ''
        for item in Headers:
            if Data[item] == None:
                Data[item] = str(Data[item])
            Data[item] = Data[item].replace(',', ' ')
            Data[item] = Data[item].replace(')', '')
            line+=Data[item]+','

        line.strip(',')
        f.write(line+'\n')

print ('Total time: ' + str((time.time()-start)/60).format("%2f") + 'minutes')
print ('Completed Successfully, Exiting...')
